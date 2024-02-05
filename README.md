# ASKEM Beaker: integrated AI-enabled coding notebooks within Terarium

This repo uses Jataware's [Beaker-Kernel](https://github.com/jataware/beaker-kernel) to provide customized contexts for dataset manipulation, model editing and configuration and other core operations within Terarium, thereby enabling Terarium to have an embedded notebook with seameless HMI integration.

In addition to an integrated notebook/coding environment for the scientific workflow, ASKEM Beaker offers an AI assistant that can support scientitific tasks such as model stratification, regridding, etc. The AI assistant is powered by Jataware's [Archytas](https://github.com/jataware/archytas) framework, a custom implementation of the [ReAct framework](https://react-lm.github.io/). The AI assistant has contextual awareness of code creation and execution in the notebook and can support the Terarium user in generating code for difficult operations in the ASKEM frameworks (e.g. Mira, Decapodes, etc).

To learn more about Beaker we encourage developers and users to check out its [comprehensive documentation](https://jataware.github.io/beaker-kernel/).

## Contexts

This repository contains several Beaker contexts that offer ASKEM specific functionalities and capabilities. Each has a specific use case or maps to a specific Terarium operator and may support specific custom messages for integration into the workbench. They are:

1. `dataset`
2. `decapodes`
3. `mira_config_edit`
4. `mira_model`
5. `mira_model_edit`
6. `oceananigans`
7. `pypackage`

> Note: the default payload setup for each context can be found at `src/askem_beaker/contexts/{context_name}/default_payload.json` and can be referenced to see an example payload for instantiating the context.

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