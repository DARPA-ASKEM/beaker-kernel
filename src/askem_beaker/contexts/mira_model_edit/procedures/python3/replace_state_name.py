def replace_state_name(model, template_name: str, old_name: str, new_name: str):
    """Replace the name of a state/concept in a given model."""
    if old_name not in model.get_concepts_name_map():
        raise ValueError(f"State with name {old_name} not found in the given model")

    for template in model.templates:
        if template.name == template_name:
            for concept in template.get_concepts():
                if concept.name == old_name:
                    concept.name = new_name

    # Update observables
    for observable in model.observables.values():
        observable.expression = SympyExprStr(
            observable.expression.args[0].subs(
                sympy.Symbol(old_name), 
                sympy.Symbol(new_name)
            )
        )

    # Update initials
    for key, initial in copy.deepcopy(model.initials).items():
        if initial.concept.name == old_name:
            model.initials[key].concept.name = new_name
            if key == old_name:
                model.initials[new_name] = model.initials.pop(old_name)

    return model


model = replace_state_name({{ model|default("model") }}, {{ template_name|default("template_name") }}, {{ old_name|default("old_name") }}, {{ new_name|default("new_name") }})