from flask import Blueprint, request, jsonify
from modelo import handler
import base64

api = Blueprint('modelo_api', __name__)


@api.route("/interpolacao/", methods=['POST'])
def predicao():
    dados_json = request.get_json()['dados']
    ambiente = request.get_json()['ambiente']
    latencia_objetivo = request.get_json()['latencia_objetivo']
    return handler.predicao(dados_json, ambiente, latencia_objetivo)


@api.route("/treinamento/", methods=['POST'])
def treinar_modelo():
    ambiente = request.get_json()['ambiente']
    return handler.treinamento(ambiente)


@api.route("/send/", methods=['POST'])
def recebimento():
    infos_json = request.get_json()['dados']
    ambiente = request.get_json()['ambiente']
    return handler.send(infos_json, ambiente)

@api.route("/send_img/<ambiente>", methods=['GET'])
def send_img(ambiente):
    image_file = open("data_001.jpeg", "rb")
    encoded_string = str(base64.b64encode(image_file.read()).decode("utf-8"))
    return jsonify({"response": 
                        {"file": encoded_string, "fullname": image_file.name, "pontos": [{'x': 0.75292, 'y': 0.940541}, {'x': 0.51484, 'y': 0.933359}]}
                  }), 200


# @api.route("/recv_img/", methods=['POST'])
# def recebimento_img():
#     file_request = request.files['file']
#     return handler.send_img(file_request)

# @api.route("/recv_anchors/", methods=['POST'])
# def recebimento_anchor():
#     anchor = request.get_json()
#     return handler.send_anchor(anchor)
