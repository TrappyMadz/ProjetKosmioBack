from flask import Flask, request, jsonify
from service.rag_service import rag_service
from flasgger import Swagger


rag_app = Flask(__name__)
swagger = Swagger(rag_app)

rag_service = rag_service()


@rag_app.route("/")
def home():
    return "Bonjour, bienvenue dans l'application wikiCO2 pfecytech2025"


@rag_app.route("/v1/process", methods=["POST"])
def process():
    # définir les entrées de l'api et les différents codes retour et leur signification
    file = request.files['pdf']

    return rag_service.process(file)
