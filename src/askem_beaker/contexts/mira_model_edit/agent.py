import json
import logging
import re

import requests
from archytas.react import Undefined
from archytas.tool_utils import AgentRef, LoopControllerRef, tool

from beaker_kernel.lib.agent import BaseAgent
from beaker_kernel.lib.context import BaseContext
from beaker_kernel.lib.jupyter_kernel_proxy import JupyterMessage

logging.disable(logging.WARNING)  # Disable warnings
logger = logging.Logger(__name__)


class MiraModelEditAgent(BaseAgent):
    """
    LLM agent used for working with the Mira Modeling framework ("mira_model" package) in Python 3.
    This will be used to find pre-written functions which will be used to edit a model.

    A mira model is made up of multiple templates that are merged together like ...

    An example mira model will look like this when encoded in json:
    ```
    {
      "id": "foo",
      "bar": "foobar",
      ...
    }

    Instead of manipulating the model directly, the agent will always return code that will be run externally in a jupyter notebook.

    """

    def __init__(self, context: BaseContext = None, tools: list = None, **kwargs):
        super().__init__(context, tools, **kwargs)

    @tool()
    async def rename_template(self, old_name: str, new_name: str, model: str, agent: AgentRef):
        """
        This tool is used when a user wants to rename a template that is part of a model.

        Args:
            model (str): The variable name identifier of the model. If not known or specified, the default value of `model` should be used.
            old_name (str): The old/existing name of the template as it exists in the model before changing.
            new_name (str): The name that the template should be changed to.
        """
        code = agent.context.get_code("replace_template_name", {"model": model, "old_name": old_name, "new_name": new_name})
        return json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )

    @tool()
    async def replace_state_name(self, template_name: str, old_name: str, new_name: str, model: str, agent: AgentRef):
        """
        This tool is used when a user wants to rename a state name within a template that is part of a model.

        Args:
            model (str): The variable name identifier of the model. If not known or specified, the default value of `model` should be used.
            template_name (str): the template within the model where these changes will be made
            old_name (str): The old/existing name of the state as it exists in the model before changing.
            new_name (str): The name that the state should be changed to.
        """
        code = agent.context.get_code("replace_state_name", {"model": model, "template_name": template_name, "old_name": old_name, "new_name": new_name})
        return json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )

    @tool()
    async def add_template(self, name: str, subject: str, outcome: str, expr: str, model: str, agent: AgentRef):
        """
        This tool is used when a user wants to add a new transition to a model.

        Args:
            model (str): The variable name identifier of the model. If not known or specified, the default value of `model` should be used.
            subject (str): The state that is the source of the new transition.
            outcome (str): the state that the new transition outputs to.
            expr (str): the mathematical rate law for the transition.
            name (str): the name of the transition
        """
        code = agent.context.get_code("add_template", {"model": model, "subject": subject, "outcome": outcome, "expr": expr, name: "name"})
        return json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )



#    @tool()
#    async def generate_code(
#        self, query: str, agent: AgentRef, loop: LoopControllerRef
#    ) -> None:
#        """
#       Generated Python code to be run in an interactive Jupyter notebook for the purpose of exploring, modifying and visualizing a Pandas Dataframe.
#
#        Input is a full grammatically correct question about or request for an action to be performed on the loaded model.
#
#         Args:
#            query (str): A fully grammatically correct question about the current model.
#
#        """
#        # set up the agent
#        # str: Valid and correct python code that fulfills the user's request.
#        prompt = f"""
#You are a programmer writing code to help with scientific data analysis and manipulation in {agent.context.metadata.get("name", "a Jupyter notebook")}.
#
#Please write code that satisfies the user's request below.
#
#Assume that the model is already loaded and has the variable named `model`.
#
#If you are asked to modify or update the dataframe, modify the dataframe in place, keeping the updated variable the same unless specifically specified otherwise.
#
#If you are asked to replace the template name of the model, use the available function named `replace_template_name` that is defined by the following python code:
#````````````````````
#def replace_template_name(
#    model: mira.metamodel.template_model.TemplateModel,
#    old_name: str,
#    new_name: str,
#) -> mira.metamodel.template_model.TemplateModel
#
#    update the template name within a model.
#
#    E.g., can turn the S.I.R. model into a S.I.Recovery. model by using old_name R and new_name Recovery
#
#    Parameters
#    ----------
#    template_model :
#        A template model
#    old_name :
#        The (singular) name of the model state or transition to be updated, e.g., ``"I"``
#    new_name :
#       The (singular) updated name of the model state or transition, e.g., ``"Infected"``
#
#    Returns
#    -------
#    :
#       A template model
#````````````````````
#
#You also have access to the libraries {agent.context.metadata.get("libraries", "that are common for these tasks")}.
#
#Please generate the code as if you were programming inside a Jupyter Notebook and the code is to be executed inside a cell.
#You MUST wrap the code with a line containing three backticks (```) before and after the generated code.
#No addtional text is needed in the response, just the code block.
#"""
#
#        llm_response = await agent.oneshot(prompt=prompt, query=query)
#        loop.set_state(loop.STOP_SUCCESS)
#        preamble, code, coda = re.split("```\w*", llm_response)
#        result = json.dumps(
#            {
#                "action": "code_cell",
#                "language": agent.context.lang,
#                "content": code.strip(),
#            }
#        )
#        return result
#
