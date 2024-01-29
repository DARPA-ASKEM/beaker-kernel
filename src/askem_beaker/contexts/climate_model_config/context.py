import copy
import datetime
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from beaker_kernel.lib.context import BaseContext
from beaker_kernel.lib.utils import intercept

from .agent import ClimateModelConfigAgent
from .demo_constants import demo_config

if TYPE_CHECKING:
    from beaker_kernel.kernel import LLMKernel
    from beaker_kernel.lib.subkernels.base import BaseSubkernel

logger = logging.getLogger(__name__)


class ClimateModelConfigContext(BaseContext):

    agent_cls = ClimateModelConfigAgent

    model_config_id: Optional[str]
    model_config_json: Optional[str]
    model_config_dict: Optional[dict[str, Any]]
    var_name: Optional[str] = "climate_model_config"

    def __init__(self, beaker_kernel: "LLMKernel", subkernel: "BaseSubkernel", config: Dict[str, Any]=demo_config) -> None:
        self.reset()
        logger.error("initializing...")
        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    def reset(self):
        pass

    async def post_execute(self, message):
        pass    
        
    async def setup(self, config, parent_header):
        
        logger.error(f"performing setup...")
        self.config = config
        
    async def send_config_preview_message(
        self, server=None, target_stream=None, data=None, parent_header={}
    ):
        try:
            self.beaker_kernel.send_response(
                "iopub", "current_config", self.config['current_model_configuration'], parent_header=parent_header
            )
        except Exception as e:
            raise

    async def auto_context(self):
        prompt={}
        prompt['prefix']="""
        You are a helpful assistant whose goal is to help the user to configure and run the {self.config['model_name']} model from the {self.config['library_name']} code library.
        Make sure to confirm with the user that the configuration that you have created is correct before running the model.
        {self.config['library_description']}
        The {self.config['model_name']} model that the user is trying to run simulates 
        {self.config['model_description']}
        
        Here is information on the model configuration variables that are accessible to the user to edit in this simulation.
        
        {self.config['variable_details']}
        
        """
        prompt['suffix']="""Begin!

        Here is information on the model configuration currently. 
        This may be updated by use of the Configure Model tool: \n{self.config['current_model_configuration']}"""
        
        result = "\n".join([prompt[key] for key in prompt.keys()])
        return result