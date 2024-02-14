subject_concept = Concept(name = "{{ subject_name }}")
outcome_concept = Concept(name = "{{ outcome_name }}")
parameter_unit = Unit(expression = sympy.Symbol("{{ parameter_units }}"))

parameters = {
    "{{ parameter_name }}": Parameter(name = "{{ parameter_name }}", value = {{ parameter_value }}, units = parameter_unit, description = "{{ parameter_description }}")
}

initials = { 
    "{{subject_name }}": Initial(concept = subject_concept, expression = sympy.Float({{subject_initial_value }})),
    "{{outcome_name }}": Initial(concept = outcome_concept, expression = sympy.Float({{outcome_initial_value }}))
}

model = model.add_template(
    template = NaturalConversion(
        subject = subject_concept,
        outcome = outcome_concept,
        rate_law = sympy.parsing.sympy_parser.parse_expr("{{ template_expression }}", local_dict=_clash),
        name = "{{ template_name }}"
    ),
    parameter_mapping = parameters,
    initial_mapping = initials
)
