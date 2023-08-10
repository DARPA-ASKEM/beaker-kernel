from textwrap import dedent

CODE = {
    "name": "Julia",
    # TODO: Maybe generate libraries and setup imports from a single source of truth?
    "libraries": """DataFrames, CSV, HTTP, JSON""",
    "setup": """using DataFrames, CSV, HTTP, JSON, DisplayAs""",
    "load_df": """df = DataFrame(CSV.File(IOBuffer(HTTP.get("{data_url}").body)))""",
    "df_lib_name": "DataFrames.jl",
    "df_info": """
        JSON.json(Dict(
            "head" => string(first(df,15)),
            "columns" => string(names(df)),
            "dtypes" => string(eltype.(eachcol(df))),
            "statistics" => string(describe(df)),
        )) |> DisplayAs.unlimited
    """,
    "df_preview": """
        _split_df = first(df, 30)
        _headers = names(_split_df)
        _data = [Array(_r) for _r=eachrow(_split_df)]

        JSON.json(Dict(
            "name" => "Temp dataset (not saved)",
            "headers" => _headers,
            "csv" => vcat([_headers], _data),
        )) |> DisplayAs.unlimited
    """,
    "df_download": """
        output_buff = IOBuffer()
        CSV.write(output_buff, df, writeheader=true)

        seekstart(output_buff)

        for line in readlines(output_buff)
            println(line)
        end
    """,
    "df_save_as": """
        parent_url = "$(dataservice_url)/datasets/$(parent_dataset_id)"
        response = HTTP.get(parent_url)
        parent_dataset = JSON.parse(String(response.body))

        if isempty(parent_dataset)
            error("Unable to locate parent dataset '$(parent_dataset_id)'")
        end

        new_dataset = deepcopy(parent_dataset)
        delete!(new_dataset, "id")
        new_dataset["name"] = new_name
        new_dataset["description"] *= "\nTransformed from dataset '$(parent_dataset["name"])' ($(parent_dataset["id"])) at $(Dates.format(Dates.now(), "c U"))"
        new_dataset["file_names"] = [filename]

        create_req = HTTP.post("$(dataservice_url)/datasets", body=JSON.json(new_dataset))
        new_dataset_id = JSON.parse(String(create_req.body))["id"]

        new_dataset["id"] = new_dataset_id
        new_dataset_url = "$(dataservice_url)/datasets/$(new_dataset_id)"
        data_url_req = HTTP.get("$(new_dataset_url)/upload-url?filename=$(filename)")
        data_url = JSON.parse(String(data_url_req.body)).get("url", nothing)

        temp_csv_file = tempname()
        CSV.write(temp_csv_file, df, writeheader=true)
        upload_response = HTTP.put(data_url, open(temp_csv_file, "r"))

        if upload_response.status != 200
            error("Error uploading dataframe: $(String(upload_response.body))")
        end

        # Cleanup
        rm(temp_csv_file)

        Dict("dataset_id" => new_dataset_id)
    """,
}

for key in CODE:
    CODE[key] = dedent(CODE[key]).strip("\n") 
