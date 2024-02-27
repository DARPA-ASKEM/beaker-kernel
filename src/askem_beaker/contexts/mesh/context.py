import codecs
import copy
import datetime
import os
import requests
from base64 import b64encode
from typing import TYPE_CHECKING, Any, Dict

from beaker_kernel.lib.context import BaseContext
from beaker_kernel.lib.utils import intercept

from .agent import MeshAgent
from askem_beaker.utils import get_auth

if TYPE_CHECKING:
    from beaker_kernel.kernel import LLMKernel
    from beaker_kernel.lib.agent import BaseAgent
    from beaker_kernel.lib.subkernels.base import BaseSubkernel

import logging
logger = logging.getLogger(__name__)


class MeshContext(BaseContext):

    agent_cls: "BaseAgent" = MeshAgent

    def __init__(self, beaker_kernel: "LLMKernel", subkernel: "BaseSubkernel", config: Dict[str, Any]) -> None:
        self.auth = get_auth()
        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    async def setup(self, config, parent_header):
        self.config = config
        code = "\n\n".join(
            (
                self.get_code("setup"),

            )
        )
        await self.execute(self.get_code("setup"))

    async def post_execute(self, message):
        pass

    def reset(self):
        pass

    # async def auto_context(self):
    #     pass

    @intercept()
    def generate_mesh_from_geotiff(self, message):
        """
        """
        img_var_or_path = message.content.get("img_file_or_path")
        code = self.get_code(generate_mesh_from_geotiff)
        return None

    generate_mesh_from_geotiff.default_payload = {}
