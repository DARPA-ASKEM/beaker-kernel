# Define needed variables in above cell(s)

result = ensemble_calibrate(
    model_path_or_jsons = [{{ models }}],
    data_paths = [{{ datasets }}]

    # Map the columns of the data to the model states
    data_mapping = {}
    # Function for each model is needed
    # Each function should describe how to take the individual models states (a dict)
    # and transform it into the ensmebled models states (another dict)
    solution_mappings = [] 

    start_time = {{ start_time | default("0.0")}},
    logging_step_size = {{ logging_step_size | default("1.0")}},
    num_iterations = {{ num_iterations | default("1000")}},
    num_particles = {{ num_iterations | default("1")}},
    lr = {{ lr | default("0.03")}},
    solver_method = '{{ solver_method | default("dopri5")}}',
    solver_options = {},
    noise_model = None,
    noise_model_kwargs = {},
    static_state_interventions = {},
    static_parameter_interventions = {},
    dynamic_state_interventions = {},
    dynamic_parameter_interventions = {},
    deterministic_learnable_parameters = [],
)