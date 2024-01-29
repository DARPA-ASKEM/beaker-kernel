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

#    LLM agent used for configuring models which have been ingested via the model extraction pipeline.
    # The model extraction pipeline provides model summary and description. Configuration variable details
    # and functions for editing the config files and code to run the model.
    # This will be used to find pre-written functions which will be used to edit a model.
class ClimateModelConfigAgent(BaseAgent):
    """
    """

    def __init__(self, context: BaseContext = None, tools: list = None, **kwargs):
        super().__init__(context, tools, **kwargs)


    @tool()
    async def run_model(self):
        """
        Use this tool to run a model.
        No input is required to this tool.
        Only use this tool once you have configured the model and have confirmed with the user that the configuration is correct.
        
        This tool returns confirmation of the model running successfully or summary of the model results or an error message if the model fails to run. (it may be configured improperly)
        
        """
        import subprocess
        import time
        
        #replace with actual job call
        process = subprocess.Popen(self.context.config['run_command'], shell=True)
        time.sleep(15)
        process.terminate()
    
        return 'Model Running. It will probably be a while. Let the user know that the model is running and ask if there is anything else you can help with.'
    
    @tool()
    async def configure_model(self,configuration_variables:dict):
        """
        Use this tool to configure a model.
        The input to this tool should be a a dictionary of model variables to change as well as the values that they are to be changed to.
        The configuration will be updated based on the dictionary that you provide. The rest of the values will remain the same. 
        You DO NOT need to provide all of the variables in the model, just the ones you want to change.
        Values of the variables should match the type given in the model information given to you.
        This tool returns confirmation of configuration being successfully changed or an error message describing any issues with the input you have given the model
        
        Args:
            configuration_variables (dict): A dictionary of key value pairs representing names of variables to be changed and values to be changed to.
                The dictionary should be in the format {{'variable_name':variable_value}}
        
        
    
        """  
        self.context.config['config_text']=await self.use_generate_functions_to_modify_config(configuration_variables)
        #update current dict
        self.context.config['current_model_configuration'].update(configuration_variables)
        return 'Model Configured Successfully'
    
    
    async def use_generate_functions_to_modify_config(self,user_inputs):
        """
        Args:
            user_inputs (dict): Dict with key value pairs of parameter names to change and values to change them to

        Returns:
        modified_config_text: The current agent's config text string modified by the information in the user input

        """
        #TODO: add invalid name catching or invalid type catching from what model extracted.. (variable details)
        
        #iterate over functions passing config text between functions to update the config
        for i,func in enumerate(self.context.config['functions']):
            valid_input_variables=func.split('def answer(')[1].split('):')[0].split(',')
            valid_input_variables=[v.strip() for v in valid_input_variables]
            input_subset={}
            # try:
            for key in self.context.config['variable_details'].keys():
                if key in valid_input_variables:
                    if key in user_inputs.keys():
                        print(key)
                        value=user_inputs[key]
                    else:
                        value=self.context.config['variable_details'][key]['default']
                    if type(value)==str:
                        if self.context.config['variable_details'][key]['type']=='int':
                            input_subset[key]=int(value)
                        elif self.context.config['variable_details'][key]['type']=='float':
                            input_subset[key]=float(value)
                        elif self.context.config['variable_details'][key]['type']=='bool':
                            input_subset[key]=value
                        else:
                            input_subset[key]=value
                    else:
                        input_subset[key]=value

            func=func.replace('def answer(',f'def answer{i}(')
            #remove extra code like examples, etc.. if present- 
            try:
                save=False
                lines=[]
                for line in func.split('\n'):
                    if 'def' in line:
                        save=True
                    if save:
                        lines.append(line)
                    if 'return' in line:
                        save=False
                new_func='\n'.join(lines)
                
                exec(new_func,globals())
            except:
                #if attempting to remove extra text breaks the function default to trying to run the entire code given by the agent
                exec(func,globals())
            dynamic_func = globals()[f'answer{i}']
            config_text=dynamic_func(self.context.config['config_text'],**input_subset)
            
        return config_text
