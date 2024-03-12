import codecs
import copy
import datetime
import os
import requests
from base64 import b64encode
from typing import TYPE_CHECKING, Any, Dict

from beaker_kernel.lib.context import BaseContext
#from beaker_kernel.lib.utils import action

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
        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    async def setup(self, config: dict, parent_header):
        await self.execute(self.get_code("setup"))
        # if "model_config_id" in config:
        #     await self.set_model_config(config["model_config_id"], parent_header=parent_header)
        if "optimize" in config:
                await self.get_optimize(config["optimize"], parent_header=parent_header)

    async def set_model_config(self, config_id, agent=None, parent_header=None):
        if parent_header is None: parent_header = {}
        self.config_id = config_id
        meta_url = f"{os.environ['HMI_SERVER_URL']}/model-configurations/{self.config_id}"
        logger.error(f"Meta url: {meta_url}")
        self.configuration = requests.get(meta_url, 
                                          auth=(os.environ['AUTH_USERNAME'],
                                                os.environ['AUTH_PASSWORD'])
                                                ).json()
        logger.info(f"Succeeded in fetching model configuration, proceeding.")
        
        self.amr = self.configuration.get("configuration")
        self.schema_name = self.amr.get("header",{}).get("schema_name","petrinet")
        self.original_amr = copy.deepcopy(self.amr)
        command = f"model = {self.amr}"
        print(f"Running command:\n-------\n{command}\n---------")
        await self.execute(command)        


    async def get_optimize(self, config: dict, agent=None, parent_header=None):
        if parent_header is None: parent_header = {}
        code = self.get_code("optimize", config)
        content = {"code": code}
        self.send_response("iopub", "code_cell", content, parent_header)
