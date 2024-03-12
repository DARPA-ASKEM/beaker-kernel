# Define needed variables in above cell(s)
model # Selected model is loaded as a dictionary 

result = optimize(
    model_path_or_json = model,
    static_parameter_interventions = param_value_objective([], [torch.tensor({{ start_time | default("0.0")}})]),
    objfun = lambda x: np.sum(np.abs(x)),
    initial_guess_interventions =  [],
    bounds_interventions = [],
    qoi = lambda samples: obs_nday_average_qoi(samples, [], 1),
    risk_bound = {{ risk_bound | default("300")}},
    start_time = {{ start_time | default("0.0")}},
    end_time = {{ end_time | default("90.0")}},
    solver_method = '{{ solver_method | default("dopri5")}}',
    solver_options = {},
    n_samples_ouu = {{ n_samples_ouu | default("100")}},
    alpha = {{ alpha | default("0.95")}},
    maxiter = {{ maxiter | default("5")}},
    maxfeval = {{ maxfeval | default("25")}},
    logging_step_size = {{ logging_step_size | default("1.0")}},
    verbose = False,
    roundup_decimal = 4,
)