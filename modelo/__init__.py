from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from modelo.controller import api as modelo_api

app = Flask(__name__)
api = Api(app)
CORS(app)

app.register_blueprint(modelo_api)