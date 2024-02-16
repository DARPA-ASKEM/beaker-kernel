concepts_name_map = model.get_concepts_name_map()
if "{{ outcome_name }}" not in concepts_name_map:
    outcome_concept = Concept(name = "{{ outcome_name }}")
else:
    outcome_concept = concepts_name_map.get("{{ outcome_name }}")

if "{{controller_name}}" not in concepts_name_map:
    controller_concept = Concept(name = "{{controller_name}}")
else:
    controller_concept = concepts_name_map.get("{{controller_name}}")


parameter_unit = Unit(expression = sympy.Symbol("{{ parameter_units }}"))

parameters = {
    "{{ parameter_name }}": Parameter(name = "{{ parameter_name }}", value = {{ parameter_value }}, units = parameter_unit, description = "{{ parameter_description }}")
}

initials = { 
    "{{outcome_name}}": Initial(concept = outcome_concept, expression = sympy.Float({{outcome_initial_value }})),
    "{{controller_name }}": Initial(concept = controller_concept, expression = sympy.Float({{controller_initial_value }}))
}

model = model.add_template(
    template = ControlledProduction(
        outcome = outcome_concept,
        controller = controller_concept,
        rate_law = sympy.parsing.sympy_parser.parse_expr("{{ template_expression }}", local_dict=_clash),
        name = "{{ template_name }}"
    ),
    parameter_mapping = parameters,
    initial_mapping = initials
)
