def replace_rate_law_sympy(model, template_name: str, new_rate_law):
    """Replace the rate law of transition. The new rate law passed in will be a sympy.Expr object

    Parameters
    ----------
    model :
        The model as an AMR JSON
    template_name :
        The ID of the transition whose rate law is to be replaced, this is
        typically the name of the transition
    new_rate_law :
        The new rate law to replace the existing rate law with

    Returns
    -------
    :
        The updated model as an AMR JSON
    """
    # NOTE: this assumes that a sympy expression object is given
    # though it might make sense to take a string instead
    assert isinstance(model, TemplateModel)
    tm = model
    for template in tm.templates:
        if template.name == template_name:
            template.rate_law = SympyExprStr(new_rate_law)
    return tm

model = replace_rate_law_sympy(model, "{{ template_name }}", "{{ new_rate_law }}")