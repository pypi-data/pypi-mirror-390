-- load this config script and execute with bash helper (or loader.lua)

loader.log("example.cfg.lua: message from user config script")

config =
{
	value="this variable is not selected for export, see example.bash for details",
	sub=
	{
		number1=123,
		number2="123",
		string="123x",
		multiline_string="line1\nline2\nline3",
		non_latin_string="Съешь еще этих мягких мексиканских кактусов, да выпей текилы",
		problematic_string=" $ $$ & && \\ - [1] \\\\ - [2] \\\\\\ - [3] ! !! [ [[ ] ]] ( (( ) )) ' '' \" \"\" ` `` \\n \\t \\r / // /// ? ?? !",
		sub=
		{
			message="another message",
		},
		lua_v1=loader.lua_version[1],
		lua_v2=loader.lua_version[2],
		lua_v3=loader.lua_version[3],
		lua_num=loader.lua_version.num,
		extra_1=loader.extra[1],
		extra_2=loader.extra[2],
		loader_args=loader.args,
		mixed={ 1, "text", true, key="test_value" }
	},
	paths=
	{
		tempdir=loader.tmpdir,
		workdir=loader.workdir,
		dynpath=loader.workdir .. "file",
		tempdir_raw=loader.tmpdir_raw,
		workdir_raw=loader.workdir_raw,
		dynpath_raw=loader.workdir_raw .. loader.slash .. "file",
	},
}

-- add yet another value
config.sub.sub.message2="yet " .. config.sub.sub.message

