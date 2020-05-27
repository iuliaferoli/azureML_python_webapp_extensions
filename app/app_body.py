from flask import request
import register_data

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello Iulia!!"

@app.route("/send_data", methods = ["POST"])
def post_json():
    content = request.get_json()

    ws = content["workspace_definition"]
    dataset = content["dataset_definition"]
    datastore = content["datastore_definition"]
    register_data.main(ws, datastore, dataset)
    return "Registered" 
