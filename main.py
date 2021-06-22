import os, shutil
import os.path as path
import pymongo
import re
from datetime import datetime as dtt

import pandas as pd
from flask import Flask, request, make_response

app = Flask(__name__)

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

    client = pymongo.MongoClient('mongodb://0.0.0.0:27017')
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

    date = dtt.strptime(date, '%Y-%m-%d').date()

    client = pymongo.MongoClient('mongodb://0.0.0.0:27017')
    database = client['viasoluti-database']
    col = database['data']

    doc = col.find_one({
        "network": env
    })

    print(doc)

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

    data = info.to_dict('records')

    return make_response({
        "type": "OK",
        "data": data
    }, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8045)
