{{ model|default("model") }} = {{ model|default("model") }}.add_template(
    template = NaturalConversion(
        subject = Concept(name = {{ subject|default("subject") }}),
        outcome = Concept(name = {{ outcome|default("outcome") }}),
        rate_law = sympy.parsing.sympy_parser.parse_expr({{ expr|default("EXPRESSION_HERE") }}),
        name = {{ name|default("name") }}
    )
)
