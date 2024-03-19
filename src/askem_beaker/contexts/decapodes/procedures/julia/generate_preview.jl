import DisplayAs
using Catlab
using JSON3

_graph = Catlab.Graphics.to_graphviz_property_graph({{ var_name|default("decapode") }})
_html = IOBuffer()
_text = IOBuffer()

show(_html, "text/html", {{ var_name|default("decapode") }})
show(_text, "text/plain", {{ var_name|default("decapode") }})

_preview = Dict(
    "application/x-askem-decapode-json-graph" => _graph,
    "application/json" => _graph,
    "text/html" => String(take!(_html)),
    "text/plain" => String(take!(_text)),
)

_preview |> DisplayAs.unlimited ∘ JSON3.write
