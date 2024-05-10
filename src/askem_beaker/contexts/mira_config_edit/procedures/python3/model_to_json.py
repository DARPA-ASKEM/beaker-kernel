from mira.modeling.amr.{{ schema_name }} import template_model_to_{{ schema_name}}_json as _to_json
_to_json({{ var_name|default("model_config") }})
