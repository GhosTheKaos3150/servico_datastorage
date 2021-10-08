import os

import pymongo
from datetime import datetime as dtt, date as dt

import re
import json as j
import pandas as pd
from flask import Flask, request, make_response
from flask_cors import CORS

# Mmoodel
import configs

app = Flask(__name__)
CORS(app)

# [
# {
#     "_id": "60b14ed3f34a4b001d688a10",
#     "geminiId": "1",
#     "groupId": "PETS",
#     "deviceId": "DOLLY",
#     "value": {
#         "dType": "Tag",
#         "pType": "dwm1001",
#         "network": "casa",
#         "value": {"x":7.803216,"y":0.38016921,"z":1.4939197,"q":91},
#         "unit": "m",
#         "when": "2021-05-28T20:13:07.323Z"
#     },
#     "when": "2021-05-28T20:13:07.323Z"
# },
# (...)]


@app.route('/')
def hello():
    return "<h2>Olá Mundo!</h2><br>" \
           "Para enviar dados, use a rota <b>\"/add_data\"</b>.<br>" \
           "Para solicitar dados, use a rota <b>\"/get\"</b>."


@app.route('/add_data', methods=['POST'])
def add_data():

    # MongoDB - Formato do Documento
    #
    # {
    #   "network": <network>,
    #   "last_update": <att>,
    #   "data": [{
    #       "id": <id>,
    #       "x": 0,
    #       "y": 0,
    #       "z": 0,
    #       "date": <date>
    #    }, (...) ]
    #   }, (...) ]
    # }

    json = request.json

    print(json)
    with open(f'data/data-{dtt.now()}.json', 'w', encoding='utf-8') as f:
        j.dump(json, f, ensure_ascii=False, indent=4)

    client = pymongo.MongoClient(
        host=os.environ.get('MONGODB_HOST') + ":" + os.environ.get('MONGODB_PORT'),
        username=os.environ.get('MONGODB_USER'),
        password=os.environ.get('MONGODB_PASSWORD'),
        authSource='admin'
    )
    database = client['viasoluti-database']
    col = database['data']

    for value in json:
        device_id = value['deviceId']
        att = dtt.now()
        d_value = value['value']

        data = d_value['value']
        date = dtt.strptime(d_value['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        network = d_value['network']

        # adicionando date e id ao data
        data['date'] = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data['id'] = device_id

        doc = col.find_one({"network": network})

        if doc is None:
            col.insert_one(
                {
                    "network": network,
                    "last_update": att.strftime('%Y-%m-%d %H:%M:%S'),
                    "data": [data]
                }
            )

        else:

            prev_data = doc['data']
            prev_data.append(data)

            query = {
                "network": network,
            }

            update = {'$set': {
                    "last_update": att.strftime('%Y-%m-%d %H:%M:%S'),
                    "data": prev_data
                }
            }

            col.update_one(query, update)

    return make_response('OK', 200)


@app.route('/get')
def get_data():
    
    json = request.json
    env = json['env']
    _id = json['id']
    date = json['date']

    if not type(env) is str:
        return make_response({
            "type": "NOT ACCEPTABLE",
            "what": "env value is not allowed".upper()
        }, 406)

    if not type(_id) is str:
        return make_response({
            "type": "NOT ACCEPTABLE",
            "what": "id value is not allowed".upper(),
        }, 406)

    dt_test = re.search("\d{4}-\d{2}-\d{2}", date)
    if dt_test is None:
        return make_response({
            "type": "NOT ACCEPTABLE",
            "what": "date format is not allowed".upper(),
        }, 406)

    date = dt.fromisoformat(date)

    client = pymongo.MongoClient(
        host=os.environ.get('MONGODB_HOST') + ":" + os.environ.get('MONGODB_PORT'),
        username=os.environ.get('MONGODB_USER'),
        password=os.environ.get('MONGODB_PASSWORD'),
        authSource='admin'
    )
    database = client['viasoluti-database']
    col = database['data']

    doc = col.find_one({
        "network": env
    })

    if doc is None:
        return make_response({
            "type": "NOT FOUND",
            "what": "on enviroment".upper(),
        }, 404)

    info = pd.DataFrame(doc['data'])
    info['date'] = pd.to_datetime(info['date'])

    info = info.loc[info['id'] == _id]
    
    if info.empty:
        return make_response({
            "response": "NOT FOUND",
            "what": "on id".upper(),
        }, 404)

    info = info.loc[info['date'].dt.date == date]
    
    if info.empty:
        return make_response({
            "response": "NOT FOUND",
            "what": "on date".upper(),
        }, 404)

    info['date'] = info['date'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    data = info.to_dict('records')

    return make_response({
        "type": "OK",
        "data": data
    }, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8045)
