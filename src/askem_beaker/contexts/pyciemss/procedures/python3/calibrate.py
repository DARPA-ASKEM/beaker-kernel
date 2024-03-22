# Define needed variables in above cell(s)
{{ model }} # Selected model is loaded as a dictionary 

result = calibrate(
    model_path_or_json = {{ model }},
    data_path = {{ dataset }}
    data_mapping = {}
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