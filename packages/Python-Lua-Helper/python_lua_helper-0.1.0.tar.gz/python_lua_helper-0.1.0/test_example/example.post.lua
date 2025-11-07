loader.log("example.post.lua: message from optional post script, you can add lua asserts for exported config values here")

assert(tonumber(config.sub.number1) ~= nil)
assert(tonumber(config.sub.number2) ~= nil)
--assert(tonumber(config.sub.string) ~= nil)

assert(config.paths.tempdir ~= nil and config.paths.tempdir ~= "")
assert(config.paths.workdir ~= nil and config.paths.workdir ~= "")
assert(config.paths.dynpath ~= nil and config.paths.dynpath ~= "")

