## Explanation for the register_data.py script:

Using the azureML library a python script can:

1. Create a reference of data in the container of a data lake and mount it as a datastore into each AML workspace we have listed
2. Get datastore
    * If files from that folder weren’t registered before, register a new one 
    * If the datastore already exists, get it by name
3. Register a dataset based on the new file reference from the registered datastore

![Data Registration](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/register_data_1.PNG?raw=true)

As you can see in this diagram, each folder would become a datastore and each file a dataset you can update with new versions.

You can run this script directly in the notebook environment of the workspace, but to make the solution scalable and enterprise ready, we package the script in a webapp and call it from data factory pipelines. 

![Scale out](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/register_data_2.PNG?raw=true)

Code input needs to be a json with a list of workspaces, datastores, and datasets.
The code will then:
1. Loop through the list of provided workspaces and credentials
2. Check if the datastore is already mounted, or if you need to bring it into the workspace
3. Register the dataset (with new version option), add time stamp to the description to track when it was made (same timestamp for all workspaces so you can compare). Can see version and timestamp in dataset description

## Inputs & Running

The input to this function is a python nested dictionary, containing lists of workspaces, datasets, and datastores. See the `example_input.json` file. 

For example, if you wanted to register one accounting dataset from a folder/container called silver in your data lake to just one azure workspace callded ml-ws-1, you would build these dictionaries:

```
workspace_definition = {
    "workspace_name" : "ml-ws-1",
    "subscription_id" : "YOUR AZURE subscription_id HERE",
    "resource_group" : "test"
    }
datastore_definition = {
        "adlsgen2_datastore_name" : "silver",
        "account_name" : "sourcedata",
        "filesystem" : "silver"
        }  
dataset_definition" : {
        "dataset_name" : "accounting_dataset",
        "dataset_path" : "accounting/accounting_data.csv"
        }
```

And then you would use the main function like so:

> main(workspace_definition, datastore_definition, dataset_definition)

Which would trigger the registration of the accounting_dataset into ml-ws-1

## Explanation for the app_body script:

This is the same as when, after deploying this code as a flask web app, you send this json file through a POST request, and the code in `app_body.py` in the `send_data` function processes this into dictionaries for you.

```
{
    "workspace_definition" : [{
        "workspace_name" : "ml-ws-1",
        "subscription_id" : "YOUR AZURE subscription_id HERE",
        "resource_group" : "ahold-test"
        }],
    "datastore_definition" : [{
        "adlsgen2_datastore_name" : "silver",
        "account_name" : "sourcedata",
        "filesystem" : "silver"
        }],
    "dataset_definition" : [{
        "dataset_name" : "accounting_dataset",
        "dataset_path" : "accounting/accounting_data.csv"
        }]
}



```

![Postman Example](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/postman_example.PNG?raw=true)