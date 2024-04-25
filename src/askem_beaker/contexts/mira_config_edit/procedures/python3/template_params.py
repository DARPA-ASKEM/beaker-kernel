template_params = {}

count = 0
for tm in model_config.templates:
    # Sanitize
    count = count + 1
    if tm.name == None or tm.name == "":
        tm.name = "generated-" + str(count)

    params = tm.get_parameter_names()
    params = list(params)

    subject = None
    outcome = None

    if hasattr(tm, 'subject'):
        subject = tm.subject.name

    if hasattr(tm, "outcome"):
        outcome = tm.outcome.name

    controllers = [x.name for x in tm.get_controllers()]
    entry = {
        "name": tm.name,
        "params": params,
        "subject": subject,
        "outcome": outcome,
        "controllers": controllers
    }
    template_params[tm.name] = entry

template_params