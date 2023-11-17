using SyntacticModels, Decapodes, Catlab
import JSON3, DisplayAs

function expr_to_svg(model)
    io = IOBuffer()
    # Catlab.Graphics.Graphviz.run_graphviz(io, to_graphviz(Decapodes.SummationDecapode(model)), format="svg")
    Catlab.Graphics.Graphviz.run_graphviz(io, to_graphviz(model), format="svg")
    String(take!(io))
end

_response = Dict(
    "application/json" => generate_json_acset({{ target }}),
    "image/svg" => expr_to_svg({{ target }})
)

path = "/tmp/decapode.json"

open(path, "w") do f
  JSON3.write(f, _response)
end

Dict("path" => path) |> DisplayAs.unlimited ∘ JSON3.write
