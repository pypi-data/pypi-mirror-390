#!/usr/bin/env lua

-- Copyright (c) 2016-2017 DarkCaster, MIT License, see https://github.com/DarkCaster/Bash-Lua-Helper for more info

-- helper script basic logic:

-- parse cmdline args, save all internal state into loader lable for use inside user config scripts
-- TODO: add logic, that perform verification of config variables passed with -e options, and explicitly transform it to one format (for example: root.sub1.sub2.value)
-- TODO: define some basic config-script verification logic
-- ???
-- sequentially, execute lua scripts from remaining args
-- recursively iterate through global params, saving valid value contents to text files inside temp dir for later reuse inside bash scripts
-- profit!

-- storage for loader params
loader={}
loader["export"]={}
loader["extra"]={}
loader["args"]={}
loader["lua_version"]={}
loader.pathseparator=package.config:sub(1,1)
loader.slash=loader.pathseparator

-- logging
function loader.log(...)
 local msg = string.format(...)
-- TODO: create more advanced logging
 print(msg)
end

-- show usage
function loader_show_usage()
 print("usage: loader.lua <params>")
 print("")
 print("mandatory params:")
 print("-t <dir> : Temporary directory, where resulted global variables will be exported as text. It must exist.")
 print("-w <dir> : Work directory, may be reffered in used scripts as \"loader.workdir\"")
 print("-c <condif script path> : Main config script file.")
 print("-e <variable name> : Name of global variable, to be exported after script is run. You can specify multiple -e params. At least one must be specified.")
 print("")
 print("optional params:")
 print("-pre <script>: Optional lua script, executed before main config script. May contain some additional functions for use with main script. Non zero exit code aborts further execution.")
 print("-post <script>: Optional lua script, executed after main config script. May contain some some verification logic for use with main script. Non zero exit code aborts further execution.")
 print("-ext <string>: You may pass multiple -ext params. Add extra string and store it inside loader.extra table (indexed by number, starting from 1). You can refer loader.extra elements in your config/pre/post scripts")
 print("-ver <version formatted with spaces>: Add lua version string. Reserved for internal use. Current lua version numbers will be saved to loader.lua_version table starting from index 1")
 print("-- mark completion of option list for this script. all remaining options will be stored in loader.args starting from index 1")
 os.exit(1)
end

function loader_param_set_check(par)
 if loader[par] ~= nil then
  print(string.format("param \"%s\" already set",par))
  print()
  loader_show_usage()
 end
end

function loader_param_not_set_check(par)
 if loader[par] == nil then
  print(string.format("param \"%s\" is not set",par))
  print()
  loader_show_usage()
 end
end

function loader_set_param (name, value)
 if name == nil then
  error(string.format("param \"%s\" is nil",name))
 end
 if value == nil then
  error(string.format("param \"%s\" is not set",name))
 end
 loader[name]=tostring(value)
end

function loader_set_dir (name, value)
 -- original not processed dir
 loader_set_param(name .. "_raw",value)
 -- check last character in dir, add path separator if missing
 if string.sub(value, -1, -1) == loader.slash then
  loader_set_param(name,value)
 else
  loader_set_param(name,value .. loader.slash)
 end
end

set=false
par="none"
export_cnt=0
extra_cnt=0
args_cnt=0
ver_cnt=0

for i,ar in ipairs(arg) do
 if set == true then
  if par == "add_version" then
   ver_cnt=ver_cnt+1
   loader.lua_version[ver_cnt] = tonumber(tostring(ar))
   if ver_cnt == 3 then
    par = "none"
    set = false
    loader.lua_version.num=loader.lua_version[1]*1000*1000+loader.lua_version[2]*1000+loader.lua_version[3]
   end
  elseif par == "add_args" then
   args_cnt=args_cnt+1
   loader.args[args_cnt] = tostring(ar)
  else
   if par == "add_export" then
    loader.export[export_cnt] = tostring(ar)
   elseif par == "add_extra" then
    loader.extra[extra_cnt] = tostring(ar)
   elseif par == "workdir" or par == "tmpdir" then
    loader_set_dir(par,ar)
   else
    loader_set_param(par,ar)
   end
   set = false
  end
 else
  if ar == "-t" then
   par="tmpdir"
  elseif ar == "-w" then
   par="workdir"
  elseif ar == "-c" then
   par="exec"
  elseif ar == "-pre" then
   par="preexec"
  elseif ar == "-post" then
   par="postexec"
  elseif ar == "-e" then
   par="add_export"
   export_cnt=export_cnt+1
  elseif ar == "-ext" then
   par="add_extra"
   extra_cnt=extra_cnt+1
  elseif ar == "--" then
   par="add_args"
  elseif ar == "-ver" then
   par="add_version"
  else
   print("incorrect parameter: " .. ar)
   print()
   loader_show_usage()
  end
  loader_param_set_check(par)
  set = true
 end
end

loader_param_not_set_check("tmpdir")
loader_param_not_set_check("workdir")
loader_param_not_set_check("exec")

if loader.export[1] == nil then
 print("at least one global variable name to export must be provided!")
 print()
 loader_show_usage()
end

-- unset non-needed defines
export_cnt=nil
extra_cnt=nul
set=nil
par=nil
args_cnt=nil
ver_cnt=nil
loader_show_usage=nil
loader_param_set_check=nil
loader_param_not_set_check=nil
loader_set_param=nil
loader_set_dir=nil

-- define some path string management logic
loader["path"]={}

function loader.path.trim_lead_slashes(path,min_len)
 local p=tostring(path)
 while string.len(p) > min_len and string.sub(p, 1, 1) == loader.slash do
  p=string.sub(p,2)
 end
 return p
end

function loader.path.trim_trail_slashes(path,min_len)
 local p=tostring(path)
 while string.len(p) > min_len and string.sub(p,-1,-1) == loader.slash do
  p=string.sub(p,1,-2)
 end
 return p
end

function loader.path.append_slash(path)
 local p=tostring(path)
 if string.len(p) > 0 and string.sub(p, -1, -1) ~= loader.slash then
  p=p .. loader.slash
 end
 return p
end

-- export path function for path combine
function loader.path.combine(first, second, ...)
 local f=tostring(first)
 if type(second)=="nil" then second="" end
 local s=tostring(second)
 local a={ ... }
 if s=="" and #a==0 then return loader.path.trim_trail_slashes(f,1) end
 f=loader.path.append_slash(loader.path.trim_trail_slashes(f,1))
 s=loader.path.trim_trail_slashes(loader.path.trim_lead_slashes(s,0),0)
 local c=f .. s
 for i,v in ipairs(a) do
  c=loader.path.combine(c,v)
 end
 return c
end

-- define some table management logic
loader["table"]={}

function loader.table.remove_value(target, value)
  assert(type(target)=="table", "target must be a table!")
  for i = #target, 1, -1 do
    if target[i]==value then table.remove(target, i) end
  end
  return target
end

-- TODO: define some config verification logic

-- execute pre-script
if loader.preexec ~= nil then
 -- loader.log("running preexec script")
 dofile(loader.preexec)
end

-- execute main script
-- print("running main config script")
dofile(loader.exec)

-- execute post-script
if loader.postexec ~= nil then
 -- loader.log("running postexec script")
 dofile(loader.postexec)
end

loader.dataout=loader.tmpdir..loader.pathseparator.."data"..loader.pathseparator
loader.metaout=loader.tmpdir..loader.pathseparator.."meta"..loader.pathseparator

function loader_data_export(name,value)
 local target = assert(io.open(loader.dataout..name, "w"))
 target:write(string.format("%s",tostring(value)))
 target:close()
end

function loader_meta_export(name,value)
 local target = assert(io.open(loader.metaout..name, "w"))
 target:write(string.format("%s",tostring(value)))
 target:close()
end

function loader_node_export(name,node)
  if type(node) == "boolean" or type(node) == "number" then
    loader_data_export(name,node)
    loader_meta_export(name,type(node))
  elseif type(node) == "string" then
    loader_data_export(name,node)
    loader_meta_export(name,"string:"..tostring(string.len(node)))
  elseif type(node) == "table" then
    local limits_set=false
    local key_min=0
    local key_max=0
    for key,value in pairs(node) do
      if type(key)=="number" then
        if limits_set==true then
          if key>key_max then
            key_max=key
          elseif key<key_min then
            key_min=key
          end
        else
          limits_set=true
          key_min=key
          key_max=key
        end
      end
      loader_node_export(string.format("%s.%s",name,tostring(key)),value)
    end
    loader_data_export(name,"")
    if limits_set==true then
      loader_meta_export(name,"table:"..tostring(key_min)..":"..tostring(key_max+1))
    else
      loader_meta_export(name,"table")
    end
  else
    loader.log("failed to export node '%s' with unsupported type '%s'",name,type(node))
  end
end

for index,value in ipairs(loader.export) do
  local status=false
  local target
  if loader.lua_version.num>=5002000 then
    status,target=pcall(load("return " .. value))
  else
    status,target=pcall(loadstring("return " .. value))
  end
  if status == false or type(target) == "nil" then
    loader.log("requested global variable or table with name %s is not exist",value)
  else
    loader_node_export(value,target)
  end
end
