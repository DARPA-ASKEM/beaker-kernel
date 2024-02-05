# ASKEM Beaker: integrated AI-enabled coding notebooks within Terarium

This repo uses Jataware's [Beaker-Kernel](https://github.com/jataware/beaker-kernel) to provide customized contexts for dataset manipulation, model editing and configuration and other core operations within Terarium, thereby enabling Terarium to have an embedded notebook with seameless HMI integration.

In addition to an integrated notebook/coding environment for the scientific workflow, ASKEM Beaker offers an AI assistant that can support scientitific tasks such as model stratification, regridding, etc. The AI assistant is powered by Jataware's [Archytas](https://github.com/jataware/archytas) framework, a custom implementation of the [ReAct framework](https://react-lm.github.io/). The AI assistant has contextual awareness of code creation and execution in the notebook and can support the Terarium user in generating code for difficult operations in the ASKEM frameworks (e.g. Mira, Decapodes, etc).

To learn more about Beaker we encourage developers and users to check out its [comprehensive documentation](https://jataware.github.io/beaker-kernel/).

## Quickstart

Run `make .env` which will copy the `env.example` to `.env`. Make sure to update `.env` and to set your `OPENAI_API_KEY` in your environment (e.g. `export OPENAI_API_KEY=your_key_here`). Next, run `make build`.

Now you're ready to run the stack with `make dev` which will run the development stack inside `docker-compose`.

> **Note**: the developer stack is currently in a transition from `TDS` to `HMI-Server` and the `docker-compose.yaml` needs to be updated accordingly. As a workaround, you can set `.env`'s `HMI-Server` settings to point to a remote instance of `HMI-Server` (e.g. `staging`) and use the `docker-compose-remote` setup with `docker-compose -f docker-compose-remote.yaml up`.

## Contexts

This repository contains several Beaker contexts that offer ASKEM specific functionalities and capabilities. Each has a specific use case or maps to a specific Terarium operator and may support specific custom messages for integration into the workbench. They are:

1. [`dataset`](#dataset-context)
2. [`decapodes`](#decapodes-context)
3. [`mira_config_edit`](#mira_config_edit-context)
4. [`mira_model`](#mira_model-context)
5. [`mira_model_edit`](#mira_model_edit-context)

> Note: the default payload setup for each context can be found at `src/askem_beaker/contexts/{context_name}/default_payload.json` and can be referenced to see an example payload for instantiating the context. The contexts that are in this repository but not listed above should not be considered supported and/or are experimental.

### `dataset` context

This context is used for ad hoc manipulation of datasets in either Python, Julia, or R. These manipulations might include basic data munging or more complex tasks. On setup it expects a dataset map to be provided where the key is the variable name for the dataet in the context and the value is the dataset ID in the `hmi-server`. For example:

```
{
  "df_hosp": "truth-incident-hospitalization",
  "df_cases": "truth-incident-case"
} 
```

Note that multiple datasets may be loaded at a given time. This context has **2 custom message types**:

1. `download_dataset_request`: stream a download of the desired dataset as specified by `var_name` (e.g. `df`).
2. `save_dataset_request`: save a dataset as specified by `var_name` (e.g. `df`), a `name` for the new dataset, the `parent_dataset_id` and an optional `filename` and create the new dataset. The response will include the `id` of the new dataset in `hmi-server`.


### `decapodes` context

This context is used for [Decapode](https://algebraicjulia.github.io/Decapodes.jl/dev/) model editing in Julia. On setup it expects a model `id` and a variable name to be provided. For example here `halfar` will be the name of the variable for the model in the context and `ice_dynamics-id` is the `id` of the correpsonding model in `hmi-server`:

```
{
  "halfar": "ice_dynamics-id"
}
```

This context has **4 custom message types**:

1. `compile_expr`: this takes in a `declaration` and compiles it
2. `save_amr_request`: accepts a `header` and saves the decapode AMR model; returns the new model `id` in `hmi-server`
3. `construct_amr`: this builds an AMR container for the decapode and can accept a `name`, `description`, `id`, 
4. `reset_request`: accepts a `model_name`

### `mira_config_edit` context

This context is used for editing model configurations via [Mira](https://github.com/gyorilab/mira). It accesses the `model` aspect of a configuration and loads it as a Mira Template Model for editing. On setup it expects a model configuration `id` to be provided; unlike other contexts the key is always `id` and the value is the model configuration `id`. For example:

```
{
  "id": "sir-model-config-id"
}
```

> **Note**: after setup, the model configuration is accessible via the variable name `model_config`.

This context's LLM agent supports two key capabilities: a user can ask for the current parameter values or initial condition values and the user can ask to update either of these. In both instances the AI assistant generates **code** for the user to execute that performs the inspection/update procedure so that the human is always in the loop.

This context has **1 custom message types**:

1. `save_model_config_request`: this does not require arguments; it simply executes a `PUT` on the model configuration to update it in place based on the operations performed in the context.


### `mira_model` context

This context is used for editing models via [Mira](https://github.com/gyorilab/mira). On setup it expects a model `id` to be provided; unlike other contexts the key is always `id` and the value is the model `id`. For example:

```
{
  "id": "sir-model-id"
}
```

> **Note**: after setup, the model is accessible via the variable name `model`.

This context's LLM agent supports generic code generation using Mira with a specific focus on stratification. Users have the ability to ask to perform a stratification (e.g. _"Stratify my model into two cities: Boston and New York"_).

This context has **4 custom message types**:

1. `save_amr_request`: takes in a `name` and saves the model as a new model in `hmi-server`, returning the new models `id`
2. `amr_to_templates`: converts AMR in JSON format to a Mira Template Model. Optionally accepts `model_name` which defaults to `model`--the variable where the AMR JSON is stored in context
3. `stratify_request`: stratifies the model based on `stratify_args` provided. Optionally accepts `model_name` which defaults to `model`--the variable where the AMR JSON is stored in context
4. `reset_request`: resets the `model` back to its original state


### `mira_model_edit` context

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