import json
import logging
import re
import typing
from time import sleep

from archytas.react import ReActAgent, Undefined
from archytas.tool_utils import AgentRef, LoopControllerRef, tool

if typing.TYPE_CHECKING:
    from .context import BaseContext


logger = logging.getLogger(__name__)

USER_RESPONSE_WAIT_TIME = 100

class BaseAgent(ReActAgent):

    context: "BaseContext"

    def __init__(
        self,
        context: "BaseContext" = None,
        tools: list = None,
        **kwargs,
    ):
        self.context = context
        self.current_user_response = None
        self._is_awaiting_user_response = False

        super().__init__(
            # model="gpt-4",  # Use default
            # api_key=api_key,  # TODO: get this from configuration
            tools=tools,
            verbose=True,
            spinner=None,
            rich_print=False,
            allow_ask_user=False,
            thought_handler=context.beaker_kernel.handle_thoughts,
            **kwargs
        )

    @tool()
    async def ask_user(
        self, query: str, agent: AgentRef, loop: LoopControllerRef
    ) -> str:
        """
        Sends a query to the user and returns their response

        Args:
            query (str): A fully grammatically correct question for the user.

        Returns:
            str: User input
        """
        if self._is_awaiting_user_response:
            raise Exception("Another user query is already in progress")

        self._is_awaiting_user_response = True
        self.current_user_response = None
        self.context.beaker_kernel.send_response(
            "iopub", "input_request", {"prompt": query}
        )
        for _ in range(USER_RESPONSE_WAIT_TIME):
            if self.current_user_response is not None:
                self._is_awaiting_user_response = False
                return self.current_user_response
            sleep(1)

        self._is_awaiting_user_response = False
        raise Exception("Query timed out. User took too long to respond.")


    @tool()
    async def generate_code(
        self, query: str, agent: AgentRef, loop: LoopControllerRef
    ) -> None:
        """
        Generated code to be run in an interactive Jupyter notebook.

        Args:
            query (str): A fully grammatically correct question or request.
        """


        prompt = f"""
    You are a programmer writing code to help with working in a Python notebook.

    Please write code that satisfies the user's request below.

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
