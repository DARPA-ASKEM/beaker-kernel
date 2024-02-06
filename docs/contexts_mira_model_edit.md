---
layout: default
title: mira_model_edit
parent: Contexts
nav_order: 1
has_toc: true
---

# mira_model_edit

This context is used for editing models via [Mira](https://github.com/gyorilab/mira) with a specific focus on fine-grained state and transition manipulation. This context was created by Uncharted. On setup it expects a model `id` to be provided; unlike other contexts the key is always `id` and the value is the model `id`. For example:

```
{
  "id": "sir-model-id"
}
```

> **Note**: after setup, the model is accessible via the variable name `model`.

This context has **4 custom message types**:

1. `replace_template_name_request`: replaces the template `old_name` with `new_name`
2. `replace_state_name_request`: replaces the state's `old_name` with `new_name` for a given `model` and `template_name`
3. `add_template_request`: for a given `model`, `subject`, `outcome`, `expr`, and `name` adds the template
4. `reset_request`: resets the `model` back to its original state