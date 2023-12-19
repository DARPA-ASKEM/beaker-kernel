import json
import logging
import re
import requests
import uuid
from datetime import datetime
import time

from archytas.tool_utils import  tool, toolset

from beaker_kernel.lib.agent import BaseAgent
from beaker_kernel.lib.context import BaseContext

logging.disable(logging.WARNING)  # Disable warnings
logger = logging.Logger(__name__)
from archytas.tool_utils import toolset, tool

@toolset()
class TDSToolset:
    """
    general explanation of the class and how it's used
    """
    def __init__(self,workflow_id,project_id,TDS_URL,PYCIEMSS_URL,SCIML_URL):
        self.workflow_id=workflow_id
        self.project_id=project_id
        self.TDS_URL=TDS_URL
        self.PYCIEMSS_URL=PYCIEMSS_URL
        self.SCIML_URL=SCIML_URL
        
    async def add_workflow(self,workflow_payload):
        workflow_response = requests.post(
            self.TDS_URL + "/workflows",
            json=workflow_payload,
            headers={"Content-Type": "application/json"},
        )
        if workflow_response.status_code >= 300:
            raise Exception(f"Failed to post workflow ({workflow_response.status_code})")
        else:
            await self.add_asset(workflow_response.json()["id"], "workflows", self.project_id)
        return workflow_response
            
    async def create_project(self):
        '''
        Generate test project in TDS
        '''
        current_timestamp = datetime.now()
        ts = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')

        project = {
            "name": "LLM Playground",
            "description": f"Project to try out LLM stuff",
            "assets": [],
            "active": True,
            }    

        resp = requests.post(f"{self.TDS_URL}/projects", json=project)
        project_id = resp.json()['id']

        return project_id   
        
    async def get_project(self):
        resp = requests.get(f"{self.TDS_URL}/projects/{self.project_id}")
        return resp.json()

    async def get_project_assets(self):
        resp = requests.get(f"{self.TDS_URL}/projects/{self.project_id}/assets")
        return resp.json()

    async def get_model_configs(self,model_id):
        res=requests.get(
            self.TDS_URL + f"/models/{model_id}/model_configurations",
            headers={"Content-Type": "application/json"},
        )
        if res.status_code>300:
            return f'Invalid model id. Please try again with valid model id. Maybe you entered a model config id?'
        return res.json()
    
    async def get_model_information(self,model_id):
        res=requests.get(
            self.TDS_URL + f"/models/{model_id}",
            headers={"Content-Type": "application/json"},
        )
        if res.status_code>300:
            return f'Invalid model id. Please try again with valid model id. Maybe you entered a model config id? To lookup model config ids use the Lookup Model Configuration Information tool'
        return res.json()
    async def get_dataset_information(self,dataset_id):
        res=requests.get(
            self.TDS_URL + f"/datasets/{dataset_id}",
            headers={"Content-Type": "application/json"},
        )
        if res.status_code>300:
            return f'Invalid dataset id. Please try again with valid dataset id'
        return res.json()
    
    async def get_simulation_information(self,simulate_or_calibrate_id):
        res=requests.get(
            self.TDS_URL + f"/simulations/{simulate_or_calibrate_id}",
            headers={"Content-Type": "application/json"},
        )
        if res.status_code>300:
            return f'Invalid simulation/calibration id. Please try again with valid simulation/calibration id'
        return res.json()
    
    async def get_model_config(self,model_config_id):
        res=requests.get(
            self.TDS_URL + f"/model_configurations/{model_config_id}",
            headers={"Content-Type": "application/json"},
        )
        if res.status_code>300:
            return f'Invalid model config id. Please try again with valid model config id. Maybe you entered a model id? To lookup model ids use the Lookup Model Information tool'
        return res.json()
    
    async def add_model_config(self,config_payload):
        model_config_res = requests.post(
            self.TDS_URL + "/model_configurations",
            json=config_payload,
            headers={"Content-Type": "application/json"},
        )
        if model_config_res.status_code>300:
            return f'Failed to get add model config. Status Code:{model_config_res.status_code}.Error:{model_config_res.reason}'
        return model_config_res.json()

    async def get_workflow(self):
        workflow_response = requests.get(
            self.TDS_URL + f"/workflows/{self.workflow_id}",
            headers={"Content-Type": "application/json"},
        )
        if workflow_response.status_code==200:
            return workflow_response.json()
        else:
            return f'Failed to get workflow. Status Code:{workflow_response.status_code}.Error:{workflow_response.reason}'

    async def modify_workflow(self,workflow_payload):
        workflow_response = requests.put(
            self.TDS_URL + f"/workflows/{self.workflow_id}",
            json=workflow_payload,
            headers={"Content-Type": "application/json"},
        )

        return f"Workflow Successfully modified."

    async def eval_integration(self,service_name, endpoint, request):
        start_time = time.time()
        is_success = False
        base_url = self.PYCIEMSS_URL if service_name == "pyciemss" else self.SCIML_URL
        sim_id = None
        kickoff_request = requests.post(
            f"{base_url}/{endpoint}",
            json=request,
            headers={"Content-Type": "application/json"},
        )
        logging.info(
            f"Kicked request: {kickoff_request.status_code} {kickoff_request.text}"
        )
        await self.add_asset(sim_id, "simulations", self.project_id)
        return {
            "Integration Status": is_success,
            "Execution Time": time.time() - start_time,
        }, sim_id

    async def add_asset(self,resource_id, resource_type):

        logging.info(f"Adding asset {resource_id} of type {resource_type} to project {self.project_id}")
        resp = requests.post(f"{self.TDS_URL}/projects/{self.project_id}/assets/{resource_type}/{resource_id}")
        if resp.status_code >= 300:
            logging.error(f"Failed to add asset to project: status - {resp.status_code}: {resp.json()}")
            return resp.json()
        
        provenance_payload = {
            "relation_type": "CONTAINS",
            "left": self.project_id,
            "left_type": "Project",
            "right": resource_id,
            "right_type": resource_type[:-1].capitalize(), # Converts "models" to "Model", etc.
        }
        prov_resp = requests.post(f"{self.TDS_URL}/provenance", json=provenance_payload)

        if prov_resp.status_code >= 300:
            logging.error(f"Failed to add provenance for project CONTAINS {resource_type}: status - {prov_resp.status_code}: {prov_resp.json()}")
        return resp.json()


    async def generate_workflow(self,workflow_name, workflow_description):
        workflow_id = str(uuid.uuid4())
        workflow_payload = {
            "id": workflow_id,
            "name": workflow_name,
            "description": workflow_description,
            "transform": {"x": 0, "y": 0, "k": 1},
            "nodes": [],
            "edges": [],
        }

        return workflow_payload, workflow_id


    async def generate_model_module(self,model_id, model_config_id=None,model_label=None):
        model_module_uuid = str(uuid.uuid4())
        config_output_uuid = str(uuid.uuid4())
        default_config_output_uuid = str(uuid.uuid4())
        if not model_label:model_label=model_config_id
        model_payload = {
            "id": model_module_uuid,
            "workflowId": self.workflow_id,
            "operationType": "ModelOperation",
            "displayName": "Model",
            "x": 400,
            "y": 150,
            "state": {"modelId": model_id, "modelConfigurationIds": [model_config_id]},
            "inputs": [],
            "outputs": [
                {
                    "id": config_output_uuid,
                    "type": "modelConfigId",
                    "label": model_label,
                    "value": [model_config_id],
                    "status": "not connected",
                },
            ],
            "statusCode": "valid",
            "width": 180,
            "height": 220,
        }

        return (
            model_payload,
            model_module_uuid,
            config_output_uuid,
            default_config_output_uuid,
        )


    async def generate_dataset_module(self,dataset_id):
        module_uuid = str(uuid.uuid4())

        dataset_output_uuid = str(uuid.uuid4())

        dataset_module_payload = {
            "id": module_uuid,
            "workflowId": self.workflow_id,
            "operationType": "Dataset",
            "displayName": "Dataset",
            "x": 375,
            "y": 550,
            "state": {"datasetId": dataset_id},
            "inputs": [],
            "outputs": [
                {
                    "id": dataset_output_uuid,
                    "type": "datasetId",
                    "label": dataset_id,
                    "value": [dataset_id],
                    "status": "not connected",
                }
            ],
            "statusCode": "invalid",
            "width": 180,
            "height": 220,
        }

        return dataset_module_payload, module_uuid, dataset_output_uuid


    async def generate_calibrate_simulate_ciemms_module(
        self,config_id, dataset_id, simulation_output,timespan,extra
    ):
        module_uuid = str(uuid.uuid4())

        config_uuid = str(uuid.uuid4())
        dataset_uuid = str(uuid.uuid4())
        sim_output_uuid = str(uuid.uuid4())

        module_payload = {
            "id": module_uuid,
            "workflowId": self.workflow_id,
            "operationType": "CalibrationOperationCiemss",
            "displayName": "Calibrate & Simulate (probabilistic)",
            "x": 1100,
            "y": 200,
            "state": {
                "chartConfigs": [
                    {"selectedRun": simulation_output, "selectedVariable": []}
                ],
                "mapping": [{"modelVariable": "", "datasetVariable": ""}],
                "simulationsInProgress": [],
                "timeSpan": timespan,
                "extra": extra,
            },
            "inputs": [
                {
                    "id": config_uuid,
                    "type": "modelConfigId",
                    "label": config_id,
                    "status": "connected",
                    "value": [config_id],
                },
                {
                    "id": dataset_uuid,
                    "type": "datasetId",
                    "label": dataset_id,
                    "status": "connected",
                    "value": [dataset_id],
                },
            ],
            "outputs": [
                {
                    "id": sim_output_uuid,
                    "type": "number",
                    "label": "Output 1",
                    "value": [{"runId": simulation_output}],
                    "status": "not connected",
                }
            ],
            "statusCode": "invalid",
            "width": 420,
            "height": 220,
        }

        return module_payload, module_uuid, config_uuid, dataset_uuid


    async def generate_simulate_ciemms_module(self, config_id, simulation_output,timespan, extra):
        module_uuid = str(uuid.uuid4())

        config_uuid = str(uuid.uuid4())
        sim_output_uuid = str(uuid.uuid4())
        num_samples=100
        if "num_samples" in extra.keys():
            num_samples=extra["num_samples"]
        module_payload = {
            "id": module_uuid,
            "workflowId": self.workflow_id,
            "operationType": "SimulateCiemssOperation",
            "displayName": "Simulate (probabilistic)",
            "x": 1100,
            "y": 500,
            "state": {
                "simConfigs": {
                    "runConfigs": {
                        simulation_output: {
                            "runId": simulation_output,
                            "active": True,
                            "configName": "Model configuration",
                            "timeSpan": timespan,
                            "numSamples": num_samples,
                            "method": "dopri5",
                        }
                    },
                    "chartConfigs": [],
                },
                "currentTimespan": timespan,
                "extra": extra,
                "numSamples": num_samples,
                "method": "dopri5",
                "simulationsInProgress": [],
            },
            "inputs": [
                {
                    "id": config_uuid,
                    "type": "modelConfigId",
                    "label": config_id,
                    "status": "connected",
                    "value": [config_id],
                    "acceptMultiple": False,
                }
            ],
            "outputs": [
                {
                    "id": sim_output_uuid,
                    "type": "simOutput",
                    "label": "Output 1",
                    "value": [simulation_output],
                    "status": "not connected",
                }
            ],
            "status": "invalid",
            "width": 420,
            "height": 220,
        }
            

        return module_payload, module_uuid, config_uuid


    async def generate_edge(self, source_id, target_id, source_port, target_port):
        edge_uuid = str(uuid.uuid4())
        edge_payload = {
            "id": edge_uuid,
            "workflowId": self.workflow_id,
            "source": source_id,
            "sourcePortId": source_port,
            "target": target_id,
            "targetPortId": target_port,
            "points": [
                {
                    "x": 0,
                    "y": 0,
                },
                {
                    "x": 0,
                    "y": 0,
                },
            ],
        }
        return edge_payload, edge_uuid

    async def clear_workflow(self):
        workflow_payload=await self.get_workflow(self.workflow_id)
        workflow_payload['nodes'],workflow_payload['edges']=[],[]
        await self.modify_workflow(workflow_payload,self.workflow_id)
        
    @tool(name="Create Project")
    async def create_project_tool(self):
        """
        Create a project to put new workflows and assets into.
        A project in Terarium is a self-contained set of assets (models, workflows, simulations, calibrations, etc..) and workflows using those assets.
        This project will automatically be used in creating future workflows and nodes and edges in that workflow.

        """
        project_id=self.create_project()
        self.project_id=project_id
        return f'Project succesfully created. Project ID is {project_id}'

        
    @tool(name="Create Workflow")
    async def create_workflow_tool(self,workflow_name:str, workflow_description:str):
        """
        Create a workflow in the current project to perform actions on assets(models, workflows, simulations, calibrations, etc..).
        To create a workflow you will need to first create a project if one does not exist or is not specified. 
        If the user does not specify the workflow name or description when attempting to create a workflow, use the Ask User tool to ask them for a workflow name and description
        This workflow will automatically be used as the default workflow until another workflow is created.
        
        Args:
            workflow_name (str): The name of the workflow.
            workflow_description (str) : A description of the workflow
            

        """
        workflow_payload,workflow_id=self.generate_workflow(workflow_name,workflow_description)
        workflow_response=await self.add_workflow(workflow_payload)
        workflow_id=workflow_response.json()["id"]
        return f'Workflow succesfully created. Workflow ID is {workflow_id}'
        

    @tool(name="Add Model to Workflow")
    async def add_model(self,model_id:str):
        """
        Add an existing model in the Terarium Data Service to the current Terarium workflow.
        Populates the model with the default config if it exists.
        You need a model id to use this function. You can get model ids by searching the Terrarium Data Service database for models using the Search for Models tool.
        The input to this tool should be a single string like "model_id"
        
        Args:
            model_id (str) : The model id of the model which is going to be added.

        """
        workflow_payload=await self.get_workflow() #get from env
        #get default config if it exists
        model_configs=await self.get_model_configs(model_id)
        model_config_id=None
        model_label=None
        for config in model_configs:
            if 'default' in config['name'].lower():
                model_config_id=config['id']
                model_label=config['name']
                break
        if not model_config_id:
            model_config_id=model_configs[0]['id']
            model_label=model_configs[0]['name']
        (
            model_payload,
            model_module_uuid,
            config_output_uuid,
            default_config_output_uuid,
        ) = await self.generate_model_module(model_id=model_id,model_config_id=model_config_id,model_label=model_label)
        workflow_payload['nodes'].append(model_payload)
        res=await self.modify_workflow(workflow_payload)
        await self.add_asset(model_id, "models")
        return res

    @tool(name="Add Dataset to Workflow")
    async def add_dataset(self,dataset_id:str):
        """
        Add an existing dataset in the Terarium Data Service to the current Terarium workflow.
        You need a dataset id to use this function. The user should give you the dataset id.
        
        Args:
            dataset_id (str) : The Terarium Data Service id of the dataset which is going to be simulated.

        """
        #call tds apis
        workflow_payload=self.get_workflow() #get from env
        #add exception to remove duplicate datasets or just modify datasets in place if we try to create a super similar dataset
        (
            dataset_payload,
            dataset_module_uuid,
            dataset_output_uuid,
        ) = await self.generate_dataset_module(dataset_id)

        workflow_payload["nodes"].append(dataset_payload)
        res=await self.modify_workflow(workflow_payload)
        await self.add_asset(dataset_id, "datasets")
        return res
    @tool(name="Add Simulation module to Workflow")
    async def add_simulation(self,model_config_id:str,simulation_settings:dict=None):
        """
        Adds a new simulation module to the current Terarium workflow.
        A simulation module takes a model configuration and simulates the model associated with that model configuration with the particular configuration enabled.
        To use this function you will need a model config id, which can be found in the workflow id 
        
        Args:
            model_config_id (str): The id of the model configuration which is going to be simulated, can be found in the workflow dictionary.
            simulation_settings (dict): a dictionary of simulation settings in the form of       
                {{
                      "timespan": {{
                        "start": 0,
                        "end": 90
                      }},
                      "extra": {{
                        "num_samples": 100
                      }}
                    }}
                Each dictionary (timespan and extras) can optionally be included. Each key in extras can be used independently as well.
            
        """
        workflow_payload=await self.get_workflow()
        #get model tds based on model config
        model_config_tds_id=None
        associated_model_tds_id=None
        associated_model_workflow_id=None
        for node in workflow_payload['nodes']:
            for output in node['outputs']:
                if output['id']==model_config_id or output['value'][0]==model_config_id: #correct tds/workflow id mixups
                    model_config_tds_id=output['value'][0]
                    model_config_id=output['id']
                    associated_model_workflow_id=node['id']
                    model_config=self.get_model_config(model_config_tds_id)
                    associated_model_tds_id=model_config['model_id']
                                 
        #example simulate for sidarthe
        #     {
        #   "engine": "ciemss",
        #   "username": "not_provided",
        #   "model_config_id": "sidarthe",
        #   "timespan": {
        #     "start": 0,
        #     "end": 90
        #   },
        #   "extra": {
        #     "num_samples": 100
        #   }
        #
        
        simulation_dictionary= {
              "engine": "ciemss",
              "username": "not_provided",
              "model_config_id": model_config_tds_id, #model tds or model config tds?
              "timespan": {
                "start": 0,
                "end": 90
              },
              "extra": {
                "num_samples": 100
              }
            }
        if simulation_settings: simulation_dictionary.update(simulation_settings)
        
        success,simulation_output = await self.eval_integration("pyciemss", "simulate", simulation_dictionary) #options from endpoint are calibrate,optimize-calibrate,optimize-simulate,simulate
        
        (
            simulate_ciemss_payload,
            simulate_ciemss_uuid,
            config_input_uuid,
        ) = await self.generate_simulate_ciemms_module(
             model_config_tds_id, simulation_output,simulation_dictionary["timespan"],simulation_dictionary["extra"] #model tds or model config tds?
        )
        workflow_payload["nodes"].append(simulate_ciemss_payload)
        config_output_uuid = str(uuid.uuid4())
        model_simulate_edge, model_simulate_edge_uuid = self.generate_edge(
            associated_model_workflow_id,
            simulate_ciemss_uuid,
            model_config_id,
            config_input_uuid,
        )
        for i,node in enumerate(workflow_payload['nodes']):
            for j,output in enumerate(node["outputs"]):
                if output['id']==model_config_id:
                   workflow_payload['nodes'][i]["outputs"][j]['status']="connected"
        workflow_payload["edges"].append(model_simulate_edge)
        res=await self.modify_workflow(workflow_payload)
        return f"Simulation node was added to the workflow."

    @tool(name="Add Calibration module to Workflow")
    async def add_calibration(self,model_config_id:str,dataset_id:str,mappings:dict,calibration_settings:dict=None):
        
        """
        Adds a new calibration/simulation node to the current Terarium workflow.
        This node first calibrates a model configuration based on relevant variables in a dataset which must be associated to model configuration states via a mapping dictionary.
        If you are unsure of how to map the model and dataset variables to each other, make your best guess and use the Ask User tool to ask the user if the mapping is correct.
        Make sure to provide the model variables and the dataset variables to the user when you ask, you can get these using the Lookup Model Information and Lookup Dataset Information tools respectively.
        It then simulates the associated model using the calibrated model configuration.
        
        Args:
            model_config_id (str) : The id of the model configurationwhich is going to be simulated, can be found in the workflow dictionary.
            dataset_id (str) : The node id of the dataset which is going to be used to calibrate the model configuration in the workflow dictionary.
            mappings (dict) : A dictionary that maps names of variables in the dataset to names of the same variable in the model state which are going to be calibrated by the dataset, along with the timestep column as well..
                For example. If we have a dataset with columns ['tstep','S'] and model variables ['Timestep','Infected','Recovered','Susceptible'], we would make a mapping - 
                {{'tstep':'Timestep','S':'Susceptible'}}
                Note that mappings are key value pairs where the key is a dataset variable name and the key is a single model variable name and that mappings MUST INCLUDE A TIME VARIABLE.
            calibration_settings (dict) : a dictionary of settings in the form of  
                {{"timespan": {{
                    "start": 0,
                    "end": 90
                }},
                  "extra": {{
                      "num_samples": 100,
                      "start_time": -1e-10,
                      "num_iterations": 1000,
                      "lr": 0.03,
                      "verbose": false,
                      "num_particles": 1,
                      "method": "dopri5"
                  }}
                }}
                which affects the calibration and simulation steps of this node.
                Each dictionary (timespan and extra) can optionally be included. Each key in extra can be used independently as well.
                If keys not included, they will set to the default above.
            
        """
        
        workflow_payload=await self.get_workflow()
        #checks to see if the agent accidentally provided a tds dataset id
        dataset_id=dataset_id
        for node in workflow_payload['nodes']:
            if 'datasetId' in node['state'].keys():
                if node['state']['datasetId']==dataset_id:
                    dataset_id=node['id']
        model_config_tds_id=None
        associated_model_tds_id=None
        associated_model_workflow_id=None
        dataset_workflow_output_id=None
        for node in workflow_payload['nodes']:
            for output in node['outputs']:
                if output['id']==model_config_id or output['value'][0]==model_config_id:
                    model_config_tds_id=output['value'][0]
                    model_config_id=output['id']
                    associated_model_tds_id=node['state']['modelId']
            if 'datasetId' in node['state'].keys():
                if node['id']==dataset_id or node['state']['datasetId']==dataset_id:
                    dataset_tds_id=node['state']['datasetId']
                    dataset_output_uuid=node['outputs'][0]['id']
                    associated_dataset_payload=await self.get_dataset_information(dataset_tds_id)
                    dataset_file_name=associated_dataset_payload['file_names'][0]
 
        #example calibrate for sidarthe
        # {
        #   "engine": "ciemss",
        #   "username": "not_provided",
        #   "model_config_id": "sidarthe",
        #   "dataset": {
        #     "id": "traditional",
        #     "filename": "traditional.csv",
        #     "mappings": {
        #       "tstep": "Timestamp",
        #       "S": "Susceptible"
        #     }
        #   },
        #   "timespan": {
        #     "start": 0,
        #     "end": 90
        #   },
        #   "extra": {
        #     "num_samples": 100,
        #     "start_time": -1e-10,
        #     "num_iterations": 1000,
        #     "lr": 0.03,
        #     "verbose": false,
        #     "num_particles": 1,
        #     "method": "dopri5"
        #   }
        # }
        
        calibration_dictionary= {
          "engine": "ciemss",
          "username": "",
          "model_config_id": model_config_tds_id,
          "dataset": {
            "id": dataset_id,
            "filename": dataset_file_name,
          },
          "timespan": {
            "start": 0,
            "end": 90
          },
          "extra": {
            "num_samples": 100,
            "start_time": -1e-10,
            "num_iterations": 1000,
            "lr": 0.03,
            "verbose": False,
            "num_particles": 1,
            "method": "dopri5"
          }
        }
        calibration_dictionary['dataset']['mappings']=mappings
        if calibration_settings: calibration_dictionary.update(calibration_settings)
        
        #options from endpoint are calibrate,optimize-calibrate,optimize-simulate,simulate
        success,simulation_output = await self.eval_integration("pyciemss", "calibrate", calibration_dictionary) 

        (
                calibrate_simulate_payload,
                calibrate_simulation_uuid,
                config_input_uuid, #model config workflow id
                dataset_input_uuid,
        ) = await self.generate_calibrate_simulate_ciemms_module(
            model_config_tds_id, dataset_tds_id, simulation_output,calibration_dictionary["timespan"],calibration_dictionary["extra"] #tds ids for model, dataset, sim
        )
        workflow_payload["nodes"].append(calibrate_simulate_payload)
        model_simulate_edge, model_simulate_edge_uuid =await self.generate_edge(
            associated_model_workflow_id,
            calibrate_simulation_uuid,
            model_config_id, #model config (output uuid from model node)
            config_input_uuid, #simulate config input uuid
        )
        for i,node in enumerate(workflow_payload['nodes']):
            for j,output in enumerate(node["outputs"]):
                if output['id']==model_config_id:
                   workflow_payload['nodes'][i]["outputs"][j]['status']="connected"
                   
        workflow_payload["edges"].append(model_simulate_edge)

        dataset_simulate_edge, dataset_simulate_edge_uuid = await self.generate_edge(
            dataset_id,
            calibrate_simulation_uuid,
            dataset_output_uuid,
            dataset_input_uuid, #simulate dataset input uuid
        )
        for i,node in enumerate(workflow_payload['nodes']):
            for j,output in enumerate(node["outputs"]):
                if output['id']==dataset_output_uuid:
                   workflow_payload['nodes'][i]["outputs"][j]['status']="connected"
                   
        workflow_payload["edges"].append(dataset_simulate_edge)

        res=await self.modify_workflow(workflow_payload)
        return f"Calibration node was added to the workflow."

    @tool(name="Lookup Model Information")
    async def lookup_model(self,model_id:str):
        """
        Look up information on a model by its model_id such as its state variables and Args: using the Terarium Data Service.
        Do not have any quotes on either end of the model id. Ie. '4353ba5a-9b40-44d2-8233-05911b250aa1' bad, 4353ba5a-9b40-44d2-8233-05911b250aa1 good.
        Args:
            model_id (str) : The model id of the model which is to be looked up. ex. 4353ba5a-9b40-44d2-8233-05911b250aa1
            

        """
        workflow_payload=await self.get_workflow()
        #checks to see if the agent accidentally provided a workflow model uuid
        model_id=model_id
        model_tds_id=model_id
        for node in workflow_payload['nodes']:
            if node['id']==model_id:
                model_tds_id=node['state']['modelId']
        res=await self.get_model_information(model_tds_id)
        return json.dumps(res)

    @tool(name="Lookup Dataset Information")
    async def lookup_dataset(self,dataset_id:str):
        """
        Look up information on a dataset by its dataset_id such as its state variables and Args: using the Terarium Data Service.
        Do not have any quotes on either end of the dataset id. Ie. '4353ba5a-9b40-44d2-8233-05911b250aa1' bad, 4353ba5a-9b40-44d2-8233-05911b250aa1 good.
        Args:
            dataset_id (str) : The dataset id of the dataset which is to be looked up. ex. 4353ba5a-9b40-44d2-8233-05911b250aa1
            

        """
        workflow_payload=await self.get_workflow()
        #checks to see if the agent accidentally provided a workflow dataset uuid
        dataset_id=dataset_id
        dataset_tds_id=dataset_id
        for node in workflow_payload['nodes']:
            if node['id']==dataset_id:
                dataset_tds_id=node['state']['datasetId']
        res=await self.get_dataset_information(dataset_tds_id)

        return json.dumps(res)

    @tool(name="Lookup Model Configuration Information")
    async def lookup_model_config(self,model_config_id:str):
        """
        Look up information on a model configuration by its id such as its state variables and Args: using the Terarium Data Service.
        Do not have any quotes on either end of the model id. Ie. '4353ba5a-9b40-44d2-8233-05911b250aa1' bad, 4353ba5a-9b40-44d2-8233-05911b250aa1 good.
        
        Args:
            model_config_id (str) : The id of the model configuration which is to be looked up. ex: 4353ba5a-9b40-44d2-8233-05911b250aa1
            

        """
        workflow_payload=await self.get_workflow()
        model_config_id=model_config_id #remove accidental strings
        model_config_tds_id=model_config_id
        #check to see if the agent gave the wrong id and correct it if it did
        for node in workflow_payload['nodes']:
            for output in node['outputs']:
                if output['id']==model_config_id:
                    model_config_tds_id=output['value'][0]
            
        res=await self.get_model_config(model_config_tds_id)
        return json.dumps(res)

    @tool(name="Search for Models")
    async def search_models(self,query:str):
        """
        Searches for models in the Terrarium Data Service database that are relevant for the query and Returns: the top 10 results along with information on those top 10 models.
        Use this tool when the user asks you to look for a model and return the results to the user in a easy to understand format including the model name and description and any other information about the models which you think will be helpful and ask them which one they want to use. 
        
        Args:
            query (str) : Plain Text Query to find relevant models
            

        """
        elasticsearch_payload={"multi_match": {
          "query": query,
          "fields": ["header.name", "header.description"]
          }
        }
        search_response = requests.post(
            self.TDS_URL + "/models/search",
            json=elasticsearch_payload,
            headers={"Content-Type": "application/json"},
        )
        if search_response.status_code==200:
            return f"Found models relevant to your query.\nModels:\n{search_response.json()}"
        else:
            return f"Error in request:Code:{search_response.status_code}.Reason:{search_response.reason}"

    @tool(name="Create Model Configuration for Existing Model")
    async def edit_model_config(self,model_id:str,model_config_id:str=None,parameters_dict:dict=None,initials_dict:dict=None):
        """
        Creates a new model configuration by modifying values in an existing configuration in the current Terrarium workflow.
        Usually a user will specific a few Args: in a model configuration that they will want to change.
        Note that the user may use natural language which does not exactly match the parameter names of the model config. You should use the lookup_model_config before using tool to find the model config options to determine which variables the user is referring to.
        In that case provide the id of the model associated with the model configuration and a dictionary of the Args: that are going to change.
        
        Args:
            model_id (str) : The id of the model with which the model configuration is associated in the workflow dictionary. This refers to the id in the workflow dictionary, not the id of the model in tds. ie. 
            model_config_id (str) : The id of the model configuration to start from. If None, uses default config associated with model id.
            parameters_dict (dict): Dict ofparameters to change in the model configuration along with their new values. Values should be floats. This is optional.
            initials_dict (dict): Dict of model initial condition variables to change in the model configuration along with their values.Values should be strings where the strings are floats., ie '0.95'. This is optional.

        """
        #ie. this field in the model config -               "parameters": {"minimum": 0.01,"maximum": 0.5}
        workflow_payload=await self.get_workflow(self.workflow_id)
        #checks to see if the agent accidentally provided a tds model id
        model_id=model_id
        for node in workflow_payload['nodes']:
            if 'modelId' in node['state'].keys():
                if node['state']['modelId']==model_id:
                    model_id=node['id']
                    
        model_tds_id=[node['state']['modelId'] for node in workflow_payload['nodes'] if node['id']==model_id][0]
        model_configs=await self.get_model_configs(model_tds_id)
        if not model_config_id:
            for config in model_configs:
                if 'default' in config['name'].lower():
                    model_config_id=config['id']
                    model_label=config['name']
                    break
        if not model_config_id:
            model_config_id=model_configs[0]['id']
            model_label=model_configs[0]['name']
        model_config_payload=await self.get_model_config(model_config_id)
        if parameters_dict:
            for key in parameters_dict:
                valid_key=False
                for i,item in enumerate(model_config_payload['configuration']['semantics']['ode']['Args:']):
                    if item['id']==key:
                        model_config_payload['configuration']['semantics']['ode']['Args:'][i].update({'value':parameters_dict[key]})
                        valid_key=True
                if not valid_key:
                    return f"Model Configuration was not created. Tell the user that the {key} parameter is not a parameter in the model and that the valid Args: are {[item['id'] for item in model_config_payload['configuration']['semantics']['ode']['Args:']]}"
        if initials_dict:
            for key in initials_dict:
                valid_key=False
                for i,item in enumerate(model_config_payload['configuration']['semantics']['ode']['initials']):
                    if item['target']==key:
                        model_config_payload['configuration']['semantics']['ode']['initials'][i].update({'expression':initials_dict[key]})
                        floaty=re.findall(r'[-+]?[0-9]*\.?[0-9]+', item['expression_mathml'])[0]
                        model_config_payload['configuration']['semantics']['ode']['initials'][i].update({'expression_mathml':item['expression_mathml'].replace(floaty,initials_dict[key])})
                        valid_key=True
                if not valid_key:
                    return f"Model Configuration was not created. Tell the user that the {key} state variable is not a variable in the model and that the valid state variables are {[item['target'] for item in model_config_payload['configuration']['semantics']['ode']['initials']]}"
        model_config_payload.pop('id')
        config_uuid=str(uuid.uuid4())
        model_config_payload['name']=config_uuid
        model_config_payload['description']=model_config_payload['description']+ ' Modified'
        new_model_config_id=await self.add_model_config(model_config_payload)['id'] #create model config in tds
        for i,node in enumerate(workflow_payload['nodes']):
            if node['id']==model_id:
                workflow_payload['nodes'][i]['state']['modelConfigurationIds'].append(new_model_config_id)
                
                workflow_payload['nodes'][i]['outputs'].append({'id': config_uuid,
                  'type': 'modelConfigId',
                  'label': new_model_config_id,
                  'value': [new_model_config_id],
                  'status': "not connected"})
        res=await self.modify_workflow(workflow_payload)
        return f"Model Configuration was created and changed to active config for the model in the workflow."

    @tool(name="Remove Node")
    async def remove_node(self,node_id:str):
        """
        Removes a node from the current workflow with a given id
        You can find the id of the node to be removed in the dictionary of the current workflow.
        
        Args:
            node_id (str) : The id of the node to be deleted in the workflow dictionary
            

        """
        workflow_payload=self.get_workflow()
        for i,node in enumerate(workflow_payload['nodes']):
            if node['id']==node_id:
                workflow_payload['nodes'].pop(i)
        res=await self.modify_workflow(workflow_payload)
        return f"Node was removed from the workflow"


class WorkflowAssistantAgent(BaseAgent):

    def __init__(self, context: BaseContext = None, tools: list = None, **kwargs):
        tools = [TDSToolset(context.workflow_id,context.project_id,context.TDS_URL,context.PYCIEMSS_URL,context.SCIML_URL)]
        super().__init__(context, tools, **kwargs)
        print(self.tools)
