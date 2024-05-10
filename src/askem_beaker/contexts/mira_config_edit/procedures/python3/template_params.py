_template_params = {}

_count = 0
for _tm in model_config.templates:
    _count += 1
    _name = getattr(_tm, "name", f"generated-{_count}")
    _template_params[_name] = {
        "name": _name,
        "params": list(_tm.get_parameter_names()),
        "subject": _tm.subject.name if hasattr(_tm, 'subject') else None,
        "outcome": _tm.outcome.name if hasattr(_tm, 'outcome') else None,
        "controllers": [x.name for x in _tm.get_controllers()],
    }

_template_params
