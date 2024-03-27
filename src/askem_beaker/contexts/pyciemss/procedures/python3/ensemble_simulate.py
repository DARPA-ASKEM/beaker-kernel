# Define needed variables in above cell(s)
result = ensemble_sample(
    model_paths_or_jsons = [{{ models }}],
    
    # Function for each model is needed
    # Each function should describe how to take the individual models states (a dict)
    # and transform it into the ensmebled models states (another dict)
    solution_mappings = [], 
   
    start_time = {{ start_time | default("0.0")}},
    end_time = {{ end_time | default("90.0")}},
    logging_step_size = {{ logging_step_size | default("1.0")}},
    num_samples = {{ num_samples | default("100")}},
    dirichlet_alpha = {{ dirichlet_alpha | default("None")}},
    solver_method = '{{ solver_method | default("dopri5")}}',
    solver_options = {},
    noise_model = None,
    noise_model_kwargs = {},
    time_unit = None,
)