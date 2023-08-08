from textwrap import dedent

CODE = {
    "name": "Python",
    # TODO: Maybe generate libraries and setup imports from a single source of truth?
    "libraries": "pandas as pd, numpy as np, scipy, pickle",
    "setup": "import pandas as pd; import numpy as np; import scipy; import pickle;",
    "load_df": "df = pd.read_csv('{data_url}');",
    "df_lib_name": "Pandas",
    "df_info": """
        {
            "head": str(df.head(15)),
            "columns": str(df.columns),
            "dtypes": str(df.dtypes),
            "statistics": str(df.describe()),
        }
    """,
    "df_preview": """
        import json
        split_df = json.loads(df.head(30).to_json(orient="split"))

        {
            "name": "Temp dataset (not saved)",
            "headers": split_df["columns"],
            "csv": [split_df["columns"]] + split_df["data"],
        }
    """,
    "df_download": """
        import pandas as pd; import io
        import time
        output_buff = io.BytesIO()
        df.to_csv(output_buff, index=False, header=True)
        output_buff.seek(0)

        for line in output_buff.getvalue().splitlines():
            print(line.decode())
    """,
    "df_save_as": """
        import copy
        import datetime
        import requests
        import tempfile

        parent_url = f"{dataservice_url}/datasets/{parent_dataset_id}"
        parent_dataset = requests.get(parent_url).json()
        if not parent_dataset:
            raise Exception(f"Unable to locate parent dataset '{parent_dataset_id}'")

        new_dataset = copy.deepcopy(parent_dataset)
        del new_dataset["id"]
        new_dataset["name"] = "{new_name}"
        new_dataset["description"] += f"\\nTransformed from dataset '{{parent_dataset['name']}}' ({{parent_dataset['id']}}) at {{datetime.datetime.utcnow().strftime('%c %Z')}}"
        new_dataset["file_names"] = ["{filename}"]

        create_req = requests.post(f"{dataservice_url}/datasets", json=new_dataset)
        new_dataset_id = create_req.json()["id"]

        new_dataset["id"] = new_dataset_id
        new_dataset_url = f"{dataservice_url}/datasets/{{new_dataset_id}}"
        data_url_req = requests.get(f'{{new_dataset_url}}/upload-url?filename={filename}')
        data_url = data_url_req.json().get('url', None)

        # Saving as a temporary file instead of a buffer to save memory
        with tempfile.TemporaryFile() as temp_csv_file:
            df.to_csv(temp_csv_file, index=False, header=True)
            temp_csv_file.seek(0)
            upload_response = requests.put(data_url, data=temp_csv_file)
        if upload_response.status_code != 200:
            raise Exception(f"Error uploading dataframe: {{upload_response.content}}")

        {{
            "dataset_id": new_dataset_id,
        }}
    """,
}

for key in CODE:
    CODE[key] = dedent(CODE[key]).strip("\n") 
