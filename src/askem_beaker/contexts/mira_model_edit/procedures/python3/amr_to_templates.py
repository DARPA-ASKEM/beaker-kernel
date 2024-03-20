from mira.sources.amr.petrinet import template_model_from_amr_json
# from mira.modeling.amr.petrinet import AMRPetriNetModel
from mira import modeling
from mira.modeling.amr.petrinet import template_model_to_petrinet_json
from mira.modeling.amr.stockflow import template_model_to_stockflow_json
from mira.modeling.amr.regnet import template_model_to_regnet_json



model_json = {{ var_name|default("model") }}
# model_tm = template_model_from_amr_json(model_json)
model_tm = model_json

# Check if `model_tm` has `initials`
if ~hasattr(model_tm, "initials"):
    model_tm.initials = {}

# if missing, initialize `initials` with `0.0` for every concept/state

# Fails, ask Nelson
# if len(model_tm.initials) < len(model.get_concepts_name_map()):
#     model_tm.initials = {name: Initial(concept = concept, expression = SympyExprStr(0.0)) for name, concept in model_tm.get_concepts_name_map().items()}


# Make sure each template has a unique name
# If missing or non-unique, default name = "t{i}"
template_names = {i: t.name for i, t in enumerate(model_tm.templates)}
if len(set(template_names.values())) < len(model.templates):
    names = list(template_names.values())
    names_count = {name: names.count(name) for name in set(names)}
    template_names_new = {i: name for i, name in template_names.items() if names_count[name] == 1}
    for i, name in template_names.items():
        if name not in names_map.keys():
            new_name = f"t{i}"
            while new_name in template_names_new.values():
                t += 1
                new_name = f"t{i}"
            template_names_new[i] = new_name

    for i, t in enumerate(model_tm.templates):
        t.name = template_names_new[i]
        t.display_name = template_names_new[i]



# Define a new MIRA TemplateModel for each template in the model
templates_tm = []
templates_amr = []
for i, __ in enumerate(model_tm.templates):
    t = copy.deepcopy(model_tm.templates[i])
    tm = TemplateModel(
        templates = [t],
        parameters = {p: model_tm.parameters[p] for p in t.get_parameter_names()},
        initials = {v: model_tm.initials[v] for v in t.get_concept_names() if v in model_tm.initials.keys()},
        annotations = Annotations(name = f"{t.name}"),
        observables = {},
        time = model_tm.time
    )
    templates_tm.append(tm)

# Define a new MIRA TemplateModel for each observable in the model
# concepts = model_tm.get_concepts_name_map()
# staticconcepts = [str(symb): concepts[str(symb)] for symb in model_tm.observables["N"].expression.free_symbols]
for obs_name, obs in model_tm.observables.items():
    tm = TemplateModel(
        templates = [
            StaticConcept(subject = model_tm.get_concepts_name_map()[str(symb)])
            for symb in obs.expression.free_symbols
        ],
        observables = {obs_name: obs},
        time = model_tm.time,
        annotations = Annotations(name = obs_name)
    )
    templates_tm.append(tm)


#
# Generate AMR for each template
#
# model_framework = ""
# if (model_framework == None):
#     if (model_amr != None):
#         model_framework = model_amr["header"]["schema_name"]
#     else:
#         model_framework = "petrinet"
        
# match model_framework:
#     case "petrinet":
#         templates_amr = [modeling.amr.petrinet.template_model_to_petrinet_json(tm) for tm in templates_tm]
#     case "regnet":
#         templates_amr = [modeling.amr.regnet.template_model_to_regnet_json(tm) for tm in templates_tm]
#     case "stockflow":
#         templates_amr = [modeling.amr.stockflow.template_model_to_stockflow_json(tm) for tm in templates_tm]

if "{{ schema_name }}" == "regnet":
    templates_amr = [template_model_to_regnet_json(tm) for tm in templates_tm]
elif "{{ schema_name }}" == "stockflow":
    templates_amr = [template_model_to_stockflow_json(tm) for tm in templates_tm]
else:
    templates_amr = [template_model_to_petrinet_json(tm) for tm in templates_tm]

#
# Return
#
{
  "templates": templates_amr,
}







# Define a new MIRA TemplateModel for each template in the model
# templates_tm = []
# templates_json = []
# for i, __ in enumerate(model_tm.templates):
#     t = copy.deepcopy(model_tm.templates[i])
#     tm = TemplateModel(
#         templates = [t],
#         # parameters = {params_global[p]: params_concepts_global[params_global[p]] for p in t.get_parameter_names()},
#         # initials = {vars_global[c.name]: inits_concepts_global[c.name] for c in t.get_concepts()},
#         # annotations = Annotations(name = f"{t.name}{i}")
#         parameters = {p: model_tm.parameters[p] for p in t.get_parameter_names()},
#         initials = {v: model_tm.initials[v] for v in t.get_concept_names()},
#         annotations = Annotations(name = f"{t.name}"),
#         observables = {},
#         time = model_tm.time
#     )
#     templates_tm.append(tm)
#     templates_json.append(AMRPetriNetModel(Model(tm)).to_json())

# Define a new MIRA TemplateModel for each observable in the model
# concepts = model_tm.get_concepts_name_map()
# staticconcepts = [str(symb): concepts[str(symb)] for symb in model_tm.observables["N"].expression.free_symbols]
# for obs_name, obs in model_tm.observables.items():
#     tm = TemplateModel(
#         templates = [
#             StaticConcept(subject = model_tm.get_concepts_name_map()[str(symb)])
#             for symb in obs.expression.free_symbols
#         ],
#         observables = {obs_name: obs},
#         time = model_tm.time,
#         annotations = Annotations(name = obs_name)
#     )
#     templates_tm.append(tm)
#     templates_json.append(AMRPetriNetModel(Model(tm)).to_json())


# {
#   "templates": templates_json
# }
