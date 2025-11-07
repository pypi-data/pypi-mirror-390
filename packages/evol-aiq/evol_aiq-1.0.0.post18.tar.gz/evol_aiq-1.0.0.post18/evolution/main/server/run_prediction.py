import subprocess

from flask import Flask
# waitress import serve

from evolution.main.server.PredictorServer import PredictorServer
import os

config = {
    "app_sever": {
        "port": 5000,
        "auth_username": "admin",
        "auth_password": "admin",
        "model_data_gen_module": "evolution.plugin.model.TestModelDataGen",
        "model_data_gen_class": "TestModelDataGen"
    }
}


def load_app() -> Flask:
    predictor_server = PredictorServer(config)
    app = predictor_server.get_app()
    return app

dev_deploy = os.environ.get("dev_deploy", "true")
app: Flask = load_app()

if dev_deploy == "true":
    app.run(port=config['app_sever']["port"])
#else:
    #serve(app, host='127.0.0.1', port=5000, threads=8)

