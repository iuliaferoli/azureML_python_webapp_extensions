import azureml.core
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace, Datastore, Dataset
import datetime

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main(workspace_definition, datastore_definition, dataset_definition):
    #get the credentials from the keyvault to use the service principal for AzureML
    serviceprincipal_definition = get_sp()
    
    for workspace in workspace_definition:
        #retrieve every workspace on the list
        ws = get_workspace(workspace, serviceprincipal_definition)
        print("DATASTORES")
        #go through every datastore we want registered
        for datastore in datastore_definition:
            register_datastore(ws, datastore, serviceprincipal_definition)
        print("DATASETS")
        #go through every dataset you want created or updated    
        time_stamp = str(datetime.datetime.now().timestamp())
        for dataset in dataset_definition:
            update_dataset(ws, datastore["adlsgen2_datastore_name"], dataset, time_stamp)
        print("\n")

def get_sp():
    # TO DO in next version: link and secret names as parameters to customize which sp to get for which case;
    # to have less parameters and not over-complicate the code, you can now add the link to the key vault 
    # and the secret names in the code if you don't plan on changing the way the authrization is done in the future.
    credential = DefaultAzureCredential()
    secret_client = SecretClient("FILL IN THE LINK TO YOUR KEY VAULT", credential)
    serviceprincipal_definition = {}
    #make sure the following secrets exist and are populated in your key vault (can change the names of the variables if you want)
    serviceprincipal_definition["tenant_id"] = secret_client.get_secret("tenant-id").value
    serviceprincipal_definition["service_principal_id"] = secret_client.get_secret("sp-id").value
    serviceprincipal_definition["service_principal_password"] = secret_client.get_secret("sp-password").value
    return serviceprincipal_definition

def get_workspace(workspace, serviceprincipal_definition):   
    auth_method = ServicePrincipalAuthentication(serviceprincipal_definition["tenant_id"], 
        serviceprincipal_definition["service_principal_id"],
        serviceprincipal_definition["service_principal_password"])
    
    ws = Workspace(
           subscription_id=workspace["subscription_id"],
           resource_group=workspace["resource_group"],
           workspace_name=workspace["workspace_name"],
           auth=auth_method)

    print("Found workspace {} at location {}".format(ws.name, ws.location))
    return ws

# Connecting the datastore folder
def register_datastore(ws, datastore, serviceprincipal_definition):
    if datastore["adlsgen2_datastore_name"] not in ws.datastores:
    #if the datastore is note registered then register it
        Datastore.register_azure_data_lake_gen2(workspace=ws,
                    datastore_name= datastore["adlsgen2_datastore_name"],
                    account_name= datastore["account_name"], # ADLS Gen2 account name
                    filesystem= datastore["filesystem"], # ADLS Gen2 filesystem
                    tenant_id=serviceprincipal_definition["tenant_id"],  # tenant id of service principal
                    client_id=serviceprincipal_definition["service_principal_id"], # client id of service principal
                    client_secret=serviceprincipal_definition["service_principal_password"]) # the secret of service principal                                                                       
        print("Mounted datastore " + datastore["filesystem"] + "to workspace " + ws.name)
    else:
        print("Workspace " + ws.name +" already has datastore " + datastore["filesystem"] + " mounted.")

# updateing the dataset to new version
def update_dataset(ws, datastore_name, dataset, time_stamp):
    datastore = Datastore.get(ws, datastore_name)
    #datastore = adlsgen2_datastore

    if dataset["dataset_name"] in ws.datasets:
        print("Dataset "+ dataset["dataset_name"] +" already created in "+ ws.name +", will update to new version...")
    else:
        print("Dataset "+ dataset["dataset_name"] +" is new and will be created in "+ ws.name +"...")

    # create a TabularDataset from the path in the datastore
    datastore_paths = [(datastore, dataset["dataset_path"])]
    retrieved_dataset = Dataset.Tabular.from_delimited_files(path=datastore_paths)
    
    #Register the dataset (and make a new version if needed)
    #The timestamp description to make it easier to see the same 
    # dataset was registered at the same time in different workspaces if you want to filter 
    retrieved_dataset = retrieved_dataset.register(workspace=ws,
                                                    name=dataset["dataset_name"],
                                                    description='versioned data, timestamp: '+ time_stamp,
                                                    create_new_version = True)
    print("Updated dataset "+ dataset["dataset_name"] +" in workspace "+ ws.name + " at timestamp "+ time_stamp)
    return retrieved_dataset