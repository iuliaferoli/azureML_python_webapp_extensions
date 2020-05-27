# AzureML python SDK WebApp extensions
# Introduction 

This code can be used to automatically register datasets & datastores into Azure Machine Learning at scale. 

Read this for overview of project.

See the `Runthrough example.md` if you want to just get started with exploring the code. 

Check () blog for the Azure deployments (with steps and Azure portal screenshots)

### The purpose of this project

* Create a way to automate the creation & management of a data science environment in AzureML
* Put all these functionalities (for example making a new environment for a new project or team, registering new datasets in it) in container(s) that can be triggered or run from one point of control 

    Some benefits:
    * Reproducability: the same environment for different projects / teams, 
    * Ease of scaling out environments and projects. (for example run an ADF pipeline to populate all resources)
    * Define RBAC and give access to trigger these tasks to only a few team members for increased security and traceability

### How
* Using the core functionalities of the Python SDK for AzureML and building extra functions around it.
* Containerize these functions with all their dependencies so anyone can run from different coding environments across the team, and expose them in an easy code-agnostic way so they are easy to call.
* Deploying these functions as WebApps that can be triggered via HTTP requests. (Azure Functions would behave similarily, you can choose to have different Azure functions for different tasks or a WebApp with different "pages" that each acts as a different function.)

### Technologies used

 IN THIS REPO

* Python and the AzureML-SDK
* Flask for adapting the python script to run as a web service

 AZURE SERVICES

* Azure Web service (Azure Functions also possible)
* Azure Data Factory if you want to trigger the HTTP requests to the web app from here (another service like Postman is also possible)
* For making this solution secure we will use Azure authorization and authentication concepts: Service Principal, Key Vault, Managed Identity, AAD. 

# Solution architecture / Data flow

![Solution Architecture](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/architecture.PNG?raw=true)

1. Data factory pipeline making calls to WebApp hosting a Python script running in Linux (this repo code)
2. The web app triggers registration of data in AML workspaces (see process below) 
(further data cleaning / model training / result generation can be done in AML generating more data)
3. New data from AML back to data lake (TBD)


# Installation / Running this code

You can use this code in flexible ways - take the register_data.py and use that code locally or in a Notebook, VM, etc and it will do the job. Or run the flask app from app_body.py locally and that will do the job. Or deploy the web app on Azure. It's an incremental approach - choose what fits best for your need.

### 0. Azure Resources

The explanation on how to set up everything in your Azure subscription is explained in detail on my blog here. The (summarized) steps for this are:

1. Deploy (if you don't already have):
    * 1+ AzureML workspace(s), 
    * 1+ data lake(s) or blob storage(s) 
    * with 1+ container(s) and at least one file in it.
2. Create a service principal app registered on your AAD that will allow authentication to your azureML resource and give it "blob owner" access to your storage.
3. Store your service principal credentials in your Key Vault (and save these credentials to insert in the code!)    
4. Deploy: 
    * A web service to host your app, 
    * an Azure Data Factory instance to send requests to your web app
5. Set up the managed identities for the web app and ADF in your AAD and set up the right authorizations; and authentication with AAD for your web app

### 1.  Install the requirements.txt in your coding environment. 

    >  pip install -r requirements.txt

### 2. Run the code locally & Fill in missing details
   * The main function is in the [`register_data.py`](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/app/register_data.py) Python script. 
   * The flask wrapper that uses the same function is in [`app_body.py`](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/app/app_body.py)
           
   See [`Runthrough example.md`](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/Runthrough%20example.md)  for detailed code breakdown and how to structure you input and function calls.

   Besides this input you also need to fill in the names and link to your key vault so that the code can connect to the service principal. Those variables need to be inputted in this part of the code in the [`register_data.py`](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/app/register_data.py) code:

   ![Service Principal fill in](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/sp_fill_in.PNG?raw=true)

   (The blog explains the creation of the key vault and storing the service principal credentials in there more clearly.)

### 3. (optional) Run the code as a web application locally

   The contents of the `app` folder are what needs to be packaged as a web app.
    
   You can also run this locally (for example for testing before you deploy the web app) (see [flask tutorial](https://flask.palletsprojects.com/en/1.1.x/cli/)) by running these commands in powershell (in the app folder):
   ```
   $env:FLASK_APP = "app_body"
   flask run
   ```

   This will give you the link to where your app runs locally. You can use a tool like Postman to send post requests to this. 

### 4. Deploy the code to an Azure Web App
   In order to access the registration service online / for your team members / not to keep the flask app running locally; you can now deploy your app to Azure. 

   * Simplest would be to use the Azure Visual Studio Code plugin for App Services. [Here](https://docs.microsoft.com/en-us/azure/developer/python/tutorial-deploy-app-service-on-linux-01) is a tutorial. 

   * If you don't develop in visual studio code you can also create the Web App wihtout using the IDE. [Here](https://docs.microsoft.com/en-us/azure/app-service/containers/quickstart-python?tabs=bash ) is a tutorial.

   * Now the app is accessible via the link you'll find in the resource overview in your Azure Portal. It will have the same functionality as running the flask app locally, and you can now send requests to the new website. You can still use postman for this, or an [ADF web activity](https://docs.microsoft.com/en-us/azure/data-factory/control-flow-web-activity) like so:  

   ![ADF Example](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/data_factory.PNG?raw=true)

### 5. Set up security & authentication on Azure

   Desired scenario: you whitelist the services or people that can access and make requests to your web app, for example only your security officer or data owner may send requests for a certain dataset to be registered in a workspace. 

   My colleague Rene Bremer made a great tutorial for this (in his example he uses an Azure Function instead of a Web App but every step is the same with the web app as well.) 

   This is what the authentication & authorization architecture looks like:

   ![Security Architecture](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/security_Rene_Bremer.png?raw=true)

   * [Here](https://github.com/rebremer/managed_identity_authentication) is a tutorial for setting this up.

   * Additional to this tutorial we set up authorizations for AzureML as well. Currently AzureML doesn't support managed identity, so this is why we use the service principal authentication instead. 
   * AzureML doesn’t support MSI at the moment, so we implement a service principal where we can still regulate authorizations
   
   1. Service principal to access azureML workspaces
   2. Service principal for azureML library to access datalake

   3. Storing secrets in key vault for all credentials

       A. Key vault to store service principal, data lake and azureML secrets

       B. Managed identity for the webapp to access key vault



   ![Other security](https://github.com/iuliaferoli/azureML_python_webapp_extensions/blob/master/images/security_azureml.PNG?raw=true)
