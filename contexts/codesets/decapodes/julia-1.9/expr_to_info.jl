using SyntacticModels, Decapodes, Catlab
import JSON3, DisplayAs

function expr_to_svg(model)
    io = IOBuffer()
    Catlab.Graphics.Graphviz.run_graphviz(io, to_graphviz(model), format="svg")
    io |> String ∘ take! 
end

_response = Dict(
    "application/json" => (generate_json_acset ∘ expand_operators)({{ target }}),
    "image/svg" => expr_to_svg({{ target }}) # TODO: Reinclude when graphviz bug is fixed
)



_response |> DisplayAs.unlimited ∘ JSON3.write
