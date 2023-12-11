import os
import requests
from typing import TYPE_CHECKING, Any, Dict

from beaker_kernel.lib.context import BaseContext

from .agent import WorkflowAssistantAgent

if TYPE_CHECKING:
    from beaker_kernel.kernel import LLMKernel
    from beaker_kernel.lib.agent import BaseAgent
    from beaker_kernel.lib.subkernels.base import BaseSubkernel

config={'workflow_id':'36e62b6d-1fc2-440c-bb1a-6e5cce33d62a','project_id':87}

class WorkflowAssistantContext(BaseContext):

    slug: str = "workflow_assistant"
    agent_cls: "BaseAgent" = WorkflowAssistantAgent

    def __init__(self, beaker_kernel: "LLMKernel", subkernel: "BaseSubkernel", config: Dict[str, Any]) -> None:
        self.TDS_URL ="https://data-service.staging.terarium.ai"
        self.PYCIEMSS_URL="https://pyciemss.staging.terarium.ai"
        self.SCIML_URL="https://sciml.staging.terarium.ai"
        self.workflow_id='36e62b6d-1fc2-440c-bb1a-6e5cce33d62a'
        self.project_id=87

        super().__init__(beaker_kernel, subkernel, self.agent_cls, config)

    async def setup(self, config, parent_header):
        config={'workflow_id':'36e62b6d-1fc2-440c-bb1a-6e5cce33d62a','project_id':87}
        self.workflow_id=config['workflow_id']
        self.project_id =config['project_id']
        self.workflow=await self.get_workflow()
        self.config = config
        
    async def post_execute(self, message):
        self.workflow = await self.get_workflow()

    async def get_workflow(self):
        workflow_response = requests.get(
            self.TDS_URL + f"/workflows/{self.workflow_id}",
            headers={"Content-Type": "application/json"},
        )
        if workflow_response.status_code==200:
            return workflow_response.json()
        else:
            return f'Failed to get workflow. Status Code:{workflow_response.status_code}.Error:{workflow_response.reason}'
        
        
    async def auto_context(self):
        prompt = {}
        prompt['prefix']="""You are a helpful assistant whose goal it is to assist the user in constructing a workflow in the Terarium scientific modeling application.
        
        Terarium is a comprehensive modeling and simulation ecosystem designed to support decision making in diverse missions and scientific domains built for researchers. Within the application users can create models which model different systems, datasets to calibrate models and simulations to use models to make predictions given certain configurations of model parameters.
        
        You will be given information about the current state of the workflow as well as tools with which to perform actions for the user in the Terarium application.
        The current workflow information will be formatted as a dictionary as follows:
        {{'id':str id of the workflow,'timestamp':str when the workflow was created,'name':str name of the workflow,'description':str description of the workflow,'nodes':list of dictionaries with information about objects(models, datasets,simulations, calibrations) in the current workflow,'edges':list of dictionaries with information on edges representing connections between objects,'transform':dict with x,y,k}}
        
        """
        #If the user asks you to perform an action but does not give all the inputs needed for using the tools required to perform those actions, ask the user clarifying questions using the Ask User tool to get the rest of the inputs, then perform those actions using the appropriate tools.
        prompt['suffix']=f"""Begin!
        
        Here is information on the current workflow : \n{await self.get_workflow()}
        """
        result = "\n".join([prompt[key] for key in prompt.keys()])
        return result
