import json
import logging
import re

from archytas.react import Undefined
from archytas.tool_utils import AgentRef, LoopControllerRef, tool

from beaker_kernel.lib.agent import BaseAgent
from beaker_kernel.lib.context import BaseContext
from beaker_kernel.lib.jupyter_kernel_proxy import JupyterMessage

logging.disable(logging.WARNING)  # Disable warnings
logger = logging.Logger(__name__)


class PyCIEMSSAgent(BaseAgent):
    """
    LLM Agent used to interact with the PyCIEMSS library.
    """

    def __init__(self, context: BaseContext = None, tools: list = None, **kwargs):
        super().__init__(context, tools, **kwargs)

    # @tool()
    # async def generate_code(
    #     self, query: str, agent: AgentRef, loop: LoopControllerRef
    # ) -> None:
    #     """
    #     Generated  code to be run in an interactive Jupyter notebook for the purpose of exploring, modifying and visualizing a Dataframe.

    #     Input is a full grammatically correct question about or request for an action to be performed on the loaded dataframe.

    #     Args:
    #         query (str): A fully grammatically correct question about the current dataset.

    #     """
    #     # set up the agent
    #     # str: Valid and correct python code that fulfills the user's request.
    #     var_sections = []
    #     for var_name, dataset_obj in agent.context.asset_map.items():
    #         df_info = await agent.context.describe_dataset(var_name)
    #         var_sections.append
    #     llm_response = await agent.oneshot(prompt=prompt, query=query)
    #     loop.set_state(loop.STOP_SUCCESS)
    #     preamble, code, coda = re.split("```\w*", llm_response)
    #     result = json.dumps(
    #         {
    #             "action": "code_cell",
    #             "language": agent.context.lang,
    #             "content": code.strip(),
    #         }
    #     )
    #     return result
