import codecs
import copy
import json
import datetime
import os
import requests
from base64 import b64encode
from typing import TYPE_CHECKING, Any, Dict

from beaker_kernel.lib.context import BaseContext
from beaker_kernel.lib.utils import action

from .agent import PyCIEMSSAgent
from askem_beaker.utils import get_auth

if TYPE_CHECKING:
    from beaker_kernel.kernel import LLMKernel
    from beaker_kernel.lib.agent import BaseAgent
    from beaker_kernel.lib.subkernels.base import BaseSubkernel

import logging
logger = logging.getLogger(__name__)


class PyCIEMSSContext(BaseContext):

    agent_cls: "BaseAgent" = PyCIEMSSAgent

    def __init__(self, beaker_kernel: "LLMKernel", subkernel: "BaseSubkernel", config: Dict[str, Any]) -> None:
        self.auth = get_auth()
        self.configs = []
        self.datasets = []
        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    async def setup(self, config: dict, parent_header):
        await self.execute(self.get_code("setup"))
        await self.set_model_configs(config["model_configs"], parent_header=parent_header)
        await self.set_datasets(config.get("datasets", {}), parent_header=parent_header)

    async def set_model_configs(self, configs, parent_header=None):
        if parent_header is None: parent_header = {}
        for name, id in configs.items():
            self.configs.append(name)
            config_url = f"{os.environ['HMI_SERVER_URL']}/model-configurations/{id}"
            configuration = requests.get(config_url,  auth=self.auth.requests_auth()).json()
            logger.info(f"Succeeded in fetching model configuration {id}, proceeding.")
        
            amr = configuration.get("configuration")
            command = f"{name} = {amr}"
            await self.execute(command)        
    
    async def set_datasets(self, datasets, parent_header=None):
        if parent_header is None: parent_header = {}
        name_to_url = {}
        for name, id in datasets.items():
            self.datasets.append(name)
            dataset_url = f"{os.environ['HMI_SERVER_URL']}/datasets/{id}"
            dataset = requests.get(dataset_url, auth=self.auth.requests_auth()).json()
            logger.info(f"Succeeded in fetching dataset {id}, proceeding.")
            filename = dataset["fileNames"][0]
            download_url = f"{dataset_url}/download-url?filename={filename}"
            data_url_req = requests.get(
                url=download_url,
                auth=self.auth.requests_auth(),
            )
            data_url = data_url_req.json().get("url", None)
            name_to_url[name] = data_url
        command = self.get_code("load_df", {"name_to_url": name_to_url})
        await self.execute(command)

    @action()
    async def get_simulate(self, message):
        args = message.content
        args["model"] = self.configs[0]
        code = self.get_code("simulate", args)
        self.send_response("iopub", "code_cell", {"code": code}, parent_header=message.header) 
        return code
    get_simulate._default_payload = "{}"

    @action()
    async def get_optimize(self, message):
        args = message.content
        args["model"] = self.configs[0]
        code = self.get_code("optimize", args)
        self.send_response("iopub", "code_cell", {"code": code}, parent_header=message.header) 
        return code
    get_optimize._default_payload = "{}"

    @action()
    async def get_calibrate(self, message):
        args = message.content
        args["model"] = self.configs[0]
        args["dataset"] = self.datasets[0]
        code = self.get_code("calibrate", args)
        self.send_response("iopub", "code_cell", {"code": code}, parent_header=message.header) 
        return code
    get_calibrate._default_payload = "{}"

    @action()
    async def get_ensemble_simulate(self, message):
        args = message.content
        args["models"] = ", ".join(self.configs)
        code = self.get_code("ensemble_simulate", args)
        self.send_response("iopub", "code_cell", {"code": code}, parent_header=message.header) 
        return code
    get_ensemble_simulate._default_payload = "{}"

    @action()
    async def get_ensemble_calibrate(self, message):
        args = message.content
        args["models"] = ", ".join(self.configs)
        args["datasets"] = self.datasets
        code = self.get_code("ensemble_simulate", args)
        self.send_response("iopub", "code_cell", {"code": code}, parent_header=message.header) 
        return code
    get_ensemble_calibrate._default_payload = "{}"

    @action()
    async def save_results(self, message):
        code = self.get_code("save_results")
        response = await self.evaluate(code)
        return response["return"]
    save_results._default_payload = "{}"

    @action()
    async def save_results_to_hmi(self, message):
        post_url = os.environ["HMI_SERVER_URL"] + "/simulations"
        sim_type = message.content.get("sim_type", "simulate")
        auth = self.auth.requests_auth()
        response = await self.evaluate(
           f"_result_fields()" 
        )
        result_files = response["return"]
        payload = {
            "name": "PyCIEMSS Notebook Session",
            "execution_payload": {},
            "result_files": result_files,
            "type": sim_type,
            "status": "complete",
            "engine": "ciemss",
        }
        response = requests.post(post_url, json=payload, auth=auth)
        if response.status_code >= 300:
            raise Exception(
                (
                    "Failed to create simulation on TDS "
                    f"(reason: {response.reason}({response.status_code}) - {json.dumps(payload)}"
                )
            )

        sim_id = response.json()["id"]
        sim_url = post_url + f"/{sim_id}"
        payload = requests.get(sim_url, auth=auth).json()
        result_files = await self.evaluate(
           f"_save_result('{sim_id}', '{auth.username}', '{auth.password}')" 
        )
        assert isinstance(result_files["return"], list)

        if "result.csv" not in result_files["return"]:
            return {
                "simulation_id": sim_id,
                "result_files": result_files["return"]
            }


        dataset_payload = {
            "name": "Beaker Kernel Results",
            "temporary": False,
            "publicAsset": True,
            "description": "Dataset created in the Beaker Kernel PyCIEMSS Context",
            "fileNames": [
                "result.csv"
            ],
            "columns": [
            ],
            "metadata": {},
            "source": "beaker-kernel",
            "grounding": {
                "identifiers": {},
                "context": {}
            }
        }

        dataservice_url = os.environ["HMI_SERVER_URL"] + "/datasets"
        create_req = requests.post(dataservice_url, auth=auth, json=dataset_payload)
        dataset_id = create_req.json()["id"]
        dataset_url = dataservice_url + f"/{dataset_id}"
        data_url_req = requests.get(f"{dataset_url}/upload-url?filename=result.csv", auth=auth)
        data_url = data_url_req.json().get('url', None)
        code = self.get_code(
            "df_save_as",
            {
                "data_url": data_url,
            }
        )
        kernel_response = await self.execute(code) # TODO: Check error

        add_asset_url = os.environ["HMI_SERVER_URL"] + f"/projects/{message.content['project_id']}/assets/dataset/{dataset_id}"
        response = requests.post(add_asset_url, auth=auth)
        if response.status_code >= 300:
            raise Exception(
                (
                    "Failed to add dataset as asset ({add_asset_url}) "
                    f"(reason: {response.reason}({response.status_code}) - {json.dumps(payload)}"
                )
            )

        return {
            "dataset_id": dataset_id,
            "simulation_id": sim_id,
        }

    save_results_to_hmi._default_payload = '{\n\t"project_id": "a22f4865-c979-4ca2-aae0-5c9afc81b72a"\n}'



