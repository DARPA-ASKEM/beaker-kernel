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


class MiraConfigEditAgent(BaseAgent):
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
    async def get_parameters_initials(self, _type: str, agent: AgentRef, loop: LoopControllerRef):
        """
        This tool is used when a user wants to see the names and values of the model configuration"s parameters.
        Please generate the code as if you were programming inside a Jupyter Notebook and the code is to be executed inside a cell.
        You MUST wrap the code with a line containing three backticks (```) before and after the generated code.
        No addtional text is needed in the response, just the code block.   

        Args:
            _type (str): either "parameters" or "initials" and determines whether to fetch values of the parameters or the initial conditions
        """
        loop.set_state(loop.STOP_SUCCESS)
        if _type == "parameters":
            code = agent.context.get_code("get_params")
        elif _type == "initials":
            code = agent.context.get_code("get_initials")
        return json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )

    @tool(autosummarize=True)
    async def update_parameters(self, parameter_values: dict, agent: AgentRef, loop: LoopControllerRef):
        """
        This tool is used when a user wants to update the model configuration parameter values.
        It takes in a dictionary where the key is the parameter name and the value is the new value in the form:

        ```
        {"param1": 10,
         "param_n: 2,
         ...}
        ```

        Please generate the code as if you were programming inside a Jupyter Notebook and the code is to be executed inside a cell.
        You MUST wrap the code with a line containing three backticks (```) before and after the generated code.
        No addtional text is needed in the response, just the code block.   

        Args:
            parameter_values (dict): the dictionary of parameter names and the values to update them with
        """
        loop.set_state(loop.STOP_SUCCESS)
        code = agent.context.get_code("update_params", {"parameter_values": parameter_values})
        return json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )

    @tool()
    async def inspect_parameters(self, query: str, agent: AgentRef, loop: LoopControllerRef):
        """
        This tool is used when a user wants to determine which parameters to update for a complex parameter that is part of an interaction matrix.
        
        Please generate the code as if you were programming inside a Jupyter Notebook and the code is to be executed inside a cell.
        You MUST wrap the code with a line containing three backticks (```) before and after the generated code.
        No addtional text is needed in the response, just the code block.   


        Args:
            query (str): A fully grammatically correct question about the model parameters
        """
        prompt = f"""
You are a programmer writing code to help with updating model parameters in a model configuration.

You have access to information about the model configuration parameter relationships via the following JSON:
{await agent.context.template_params()}

In that structure, each key `t*` is a template and each item in the `params` key of the template is one of the model"s underlying parameters.
You can think of the `subject` and `outcome` defining a relationship between two compartments in the model with respect to the parameters in `params`.

For example:

```
{{"t1": {{"name": "t1",
"params": ["me", "mc", "beta", "C_0", "N"],
"subject": "S_middle",
"outcome": "E_middle",
"controllers": ["I_middle"]}},
"t2": {{"name": "t4",
"params": ["me", "mc", "C_2", "beta", "N"],
"subject": "S_old",
"outcome": "E_old",
"controllers": ["I_old"]}}}}
```

Here we see that in `t1` or template 1, the `S_middle` and `E_middle` compartments or state variables have an interaction over the parameters: ["me", "mc", "beta", "C_0", "N"].
So, if you are asked to update the value for the `C` parameter between `S_middle` and `E_middle` you would know to update `C_0` but not `C_2` since
that governs interactions between `S_old` and `E_old`.

In many cases you may be simply asked to update certain specific parameters, but otherwise you will need to rely on information from the parameter
relationships provided to infer which parameters actually need to be updated.

In your thoughts please describe which parameters you have selected and why you chose them, then craft the code to perform the update.
The code to update the parameters should look something like this:

```
model_config.parameters[kk].value = vv
```

where `kk` is the parameter name and `vv` is the value to be updated. You MUST use this template to perform the parameter value update.

Please generate the code as if you were programming inside a Jupyter Notebook and the code is to be executed inside a cell.

You MUST wrap the code with a line containing three backticks (```) before and after the generated code.
No addtional text is needed in the response, just the code block.
"""

        llm_response = await agent.oneshot(prompt=prompt, query=query)
        loop.set_state(loop.STOP_SUCCESS)
        preamble, code, coda = re.split("```\w*", llm_response)
        result = json.dumps(
            {
                "action": "code_cell",
                "language": "python3",
                "content": code.strip(),
            }
        )
        return result