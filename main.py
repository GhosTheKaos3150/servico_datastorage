import os

import pymongo
from datetime import datetime as dtt, date as dt
from threading import Thread

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

    with open(f'data/data_{dtt.now().strftime("%Y-%m-%dT%H:%M:%S")}.json', 'w', encoding='utf-8') as f:
        if not os.path.exists('data'):
            os.mkdir("data")
        j.dump(json, f, ensure_ascii=False, indent=4)

    client = pymongo.MongoClient(
        host=os.environ.get('MONGODB_HOST') + ":" + os.environ.get('MONGODB_PORT'),
        username=os.environ.get('MONGODB_USER'),
        password=os.environ.get('MONGODB_PASSWORD'),
        authSource='admin'
    )
    database = client['viasoluti-database']
    col = database['data']

    ntwk_list = []
    data_list = []

    for value in json:
        device_id = value['deviceId']
        att = dtt.now()
        d_value = value['value']

        data = d_value['value']
        date = dtt.strptime(d_value['when'], '%Y-%m-%dT%H:%M:%S.%fZ')
        network = d_value['network']

        if not network in ntwk_list:
            ntwk_list.append(network)

        # adicionando date e id ao data
        data['date'] = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        data['id'] = device_id
        data['network'] = network

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

            data_list.append(data)

    print(data_list)

    for network in ntwk_list:
        doc = col.find_one({"network": network})
        att = dtt.now()

        data = [d for d in data_list if d['network'] == network]

        prev_data = doc['data']
        prev_data += data

        query = {
            "network": network,
        }

        update = {'$set': {
            "last_update": att.strftime('%Y-%m-%d %H:%M:%S'),
            "data": prev_data
        }
        }

        col.update_one(query, update)

    return make_response({
        'type': 'OK',
        'status': 200,
        "len_data": len(data_list),
        "len_envs": len(ntwk_list)
    })


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

    info.sort_values(by='date', inplace=True)
    info['date'] = info['date'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    data = info.to_dict('records')

    return make_response({
        "type": "OK",
        "data": data,
        "len": len(data)
    }, 200)


@app.route('/getall')
def getall_data():
    json = request.json
    env = json['env']
    date = json['date']

    if not type(env) is str:
        return make_response({
            "type": "NOT ACCEPTABLE",
            "what": "env value is not allowed".upper()
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

    info.sort_values(by='date', inplace=True)
    info['date'] = info['date'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    data = info.to_dict('records')

    return make_response({
        "type": "OK",
        "data": data,
        "len": len(data)
    }, 200)


@app.route("/rmdup")
def remove_duplicates():
    json = request.json
    env = json['env']

    client = pymongo.MongoClient(
        host=os.environ.get('MONGODB_HOST') + ":" + os.environ.get('MONGODB_PORT'),
        username=os.environ.get('MONGODB_USER'),
        password=os.environ.get('MONGODB_PASSWORD'),
        authSource='admin'
    )
    database = client['viasoluti-database']
    col = database['data']
    doc = col.find_one({"network": env})

    data = pd.DataFrame(doc['data'])
    data.drop_duplicates(inplace=True)
    data = data.to_dict('records')

    query = {
        "network": env,
    }

    update = {'$set': {
        "data": data
    }
    }

    col.update_one(query, update)

    return make_response({
        "type": "OK",
        "len": len(data),
        "data": data
    }, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8045)
