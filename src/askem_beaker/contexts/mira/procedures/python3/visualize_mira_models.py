import base64

from mira.metamodel import TemplateModel
from mira.modeling.viz import GraphicalModel


def __visualize_model(name: str, model: TemplateModel) -> str:
    graphical_model = GraphicalModel.from_template_model(model)
    filename = f"_preview_{name}.png"
    graphical_model.write(filename, format="png")
    with open(filename, "rb") as f:
        data = f.read()
        enc = base64.b64encode(bytes(data))
        return enc.decode("utf-8")


__state = locals()
__models = {}

for model in {{model_vars}}:
    model: str
    __models[model] = {"text/plain": repr(__state[model]), "image/png": __visualize_model(model, __state[model])}

del __state

__models
