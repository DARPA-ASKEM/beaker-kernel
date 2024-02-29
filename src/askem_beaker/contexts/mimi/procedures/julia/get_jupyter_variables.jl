write("/tmp/state.csv", "name,type,value\n")
open("/tmp/state.csv", "a")

_var_names = names(Main)
for var in _var_names
    value = eval(var)
    write("$var,$(typeof(value)),$value")
end
