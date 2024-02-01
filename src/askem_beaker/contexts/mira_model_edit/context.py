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

from .agent import MiraModelEditAgent
from askem_beaker.utils import get_auth

if TYPE_CHECKING:
    from beaker_kernel.kernel import LLMKernel
    from beaker_kernel.lib.subkernels.base import BaseSubkernel

logger = logging.getLogger(__name__)


class MiraModelEditContext(BaseContext):

    agent_cls = MiraModelEditAgent

    model_id: Optional[str]
    model_json: Optional[str]
    model_dict: Optional[dict[str, Any]]
    var_name: Optional[str] = "model"

    def __init__(self, beaker_kernel: "LLMKernel", subkernel: "BaseSubkernel", config: Dict[str, Any]) -> None:
        self.reset()
        self.auth = get_auth()
        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    def reset(self):
        pass
        
    async def setup(self, config, parent_header):
        self.config = config
        item_id = config["id"]
        item_type = config.get("type", "model")
        print(f"Processing {item_type} AMR {item_id} as a MIRA model")
        await self.set_model(
            item_id, item_type, parent_header=parent_header
        )

    async def post_execute(self, message):
        await self.send_mira_preview_message(parent_header=message.parent_header)

    async def set_model(self, item_id, item_type="model", agent=None, parent_header={}):
        if item_type == "model":
            self.model_id = item_id
            self.config_id = "default"
            meta_url = f"{os.environ['DATA_SERVICE_URL']}/models/{self.model_id}"
            self.amr = requests.get(meta_url, auth=self.auth.requests_auth()).json()
        elif item_type == "model_config":
            self.config_id = item_id
            meta_url = f"{os.environ['DATA_SERVICE_URL']}/model_configurations/{self.config_id}"
            self.configuration = requests.get(meta_url, auth=self.auth.requests_auth()).json()
            self.model_id = self.configuration.get("model_id")
            self.amr = self.configuration.get("configuration")
        self.original_amr = copy.deepcopy(self.amr)
        if self.amr:
            await self.load_mira()
        else:
            raise Exception(f"Model '{item_id}' not found.")
        await self.send_mira_preview_message(parent_header=parent_header)

    async def load_mira(self):
        model_url = f"{os.environ['DATA_SERVICE_URL']}/models/{self.model_id}"
        command = "\n".join(
            [
                self.get_code("setup"),
                self.get_code("load_model", {
                    "var_name": self.var_name,
                    "model_url": model_url,
                    "auth_header": self.auth.auth_header(),
                }),
            ]
        )
        print(f"Running command:\n-------\n{command}\n---------")
        await self.execute(command)

    async def send_mira_preview_message(
        self, server=None, target_stream=None, data=None, parent_header={}
    ):
        try:
            preview = await self.evaluate(self.get_code("model_preview"), {"var_name": self.var_name})
            content = preview["return"]
            self.beaker_kernel.send_response(
                "iopub", "model_preview", content, parent_header=parent_header
            )
        except Exception as e:
            raise

    @intercept()
    async def reset_request(self, message):
        content = message.content

        model_name = content.get("model_name", "model")
        reset_code = self.get_code("reset", {
            "var_name": model_name,
        })
        reset_result = await self.execute(reset_code)

        content = {
            "success": True,
            "executed_code": reset_result["parent"].content["code"],
        }

        self.beaker_kernel.send_response(
            "iopub", "reset_response", content, parent_header=message.header
        )
        await self.send_mira_preview_message(parent_header=message.header)

    @intercept()
    async def replace_template_name(self, message):
        content = message.content

        model = content.get("model")
        old_name  = content.get("old_name")
        new_name = content.get("new_name")

        self.beaker_kernel.send_response(
            "iopub",
            "replace_template_name",
            {
                "model": model,
                "old_name": old_name,
                "new_name": new_name
            },
        )

    @intercept()
    async def replace_state_name(self, message):
        content = message.content

        model = content.get("model")
        template_name  = content.get("template_name")
        old_name  = content.get("old_name")
        new_name = content.get("new_name")

        self.beaker_kernel.send_response(
            "iopub",
            "replace_state_name",
            {
                "model": model,
                "template_name": template_name,
                "old_name": old_name,
                "new_name": new_name
            },
        )

    @intercept()
    async def add_template(self, message):
        content = message.content

        model = content.get("model")
        subject  = content.get("subject")
        outcome  = content.get("outcome")
        expr = content.get("expr")
        name = content.get("name")

        self.beaker_kernel.send_response(
            "iopub",
            "add_template",
            {
                "model": model,
                "subject": subject,
                "outcome": outcome,
                "expr": expr,
                "name": name
            },
        )
