using SyntacticModels, Decapodes, Catlab
import JSON3, DisplayAs
using DiagrammaticEquations
using DiagrammaticEquations.Deca

{{ target }} = @decapode begin
    {{ declaration }}
end
