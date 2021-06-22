import os, shutil
import os.path as path
import pymongo
from datetime import datetime as dtt

import pandas as pd
from flask import Flask, request

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

    return {
        'response': 'OK',
        'status': 200
    }


@app.route('/get')
def get_data():
    
    json = request.json
    env = json['env']
    _id = json['id']
    date = json['date']

    client = pymongo.MongoClient('mongodb://0.0.0.0:27017')
    database = client['viasoluti-database']
    col = database['data']

    doc = col.find_one({
        "network": env
    })

    if doc is None:
        return {
            "response": "NOT FOUND",
            "what": "on enviroment".upper(),
            "status": 404
        }
    else:
        print(doc)

    info = pd.DataFrame(doc['objects'])
    info = info.loc[info['id'] == _id]
    
    if info.empty:
        return {
            "response": "NOT FOUND",
            "what": "on id".upper(),
            "status": 404
        }
    
    info = info['dates'].tolist()[0]

    data_by_date = pd.DataFrame(info)
    data_by_date = data_by_date.loc[data_by_date['date'] == date]
    
    if data_by_date.empty:
        return {
            "response": "NOT FOUND",
            "what": "on date".upper(),
            "status": 404
        }
    
    data = data_by_date['data'].tolist()[0]

    return {
        "response": "OK",
        "status": 200,
        "data": data
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8045)
