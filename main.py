import os
import os.path as path
import requests
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


# @app.route('/add_data', methods=['POST'])
# def add_data():
#     # Treating Data
#     data = request.json
#
#     for value in data:
#         obj_id = value['deviceId']
#         obj_data = value['value']
#         obj_date_att = dtt.strptime(value['when'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
#
#         network = obj_data['network']
#
#         os.chdir('..')
#         if not 'data' in os.listdir(path.abspath(path.curdir)):
#             os.mkdir('data')
#
#         os.chdir('data')
#
#         if f'{network}' in os.listdir(path.abspath(path.curdir)):
#             os.chdir(f'{network}')
#         else:
#             os.mkdir(f'{network}')
#             os.chdir(f'{network}')
#
#         if f'{obj_id}' in os.listdir(path.abspath(path.curdir)):
#             os.chdir(f'{obj_id}')
#         else:
#             os.mkdir(f'{obj_id}')
#             os.chdir(f'{obj_id}')
#
#         if f'{obj_date_att}' in os.listdir(path.abspath(path.curdir)):
#             os.chdir(f'{obj_date_att}')
#         else:
#             os.mkdir(f'{obj_date_att}')
#             os.chdir(f'{obj_date_att}')
#
#         info = {
#             'id': [obj_id],
#             'network': [network],
#             'date': [dtt.now().strftime('%d de %b de %Y, ás %H:%M:%S')]
#         }
#         info = pd.DataFrame(data=info)
#
#         save_data = obj_data['value']
#         save_data = {
#             'x': [save_data['x']],
#             'y': [save_data['y']],
#             'z': [save_data['z']],
#         }
#
#         save_data = pd.DataFrame(data=save_data, columns=['x', 'y', 'z'])
#         save_data['id'] = save_data.index
#         save_data['date'] = obj_data['when']
#         save_data['id_obj'] = obj_id
#
#         if 'data.csv' in os.listdir(path.abspath(path.curdir)):
#             prev_data = pd.read_csv(path.abspath(path.curdir) + '/data.csv')
#             save_data = pd.concat([prev_data, save_data], join='inner', ignore_index=True)
#
#         save_data.to_csv(path.abspath(path.curdir) + '/data.csv')
#         info.to_csv(path.abspath(path.curdir) + '/info.csv')
#
#         os.chdir('../../../../servico_datastorage')
#
#     return {
#         'response': 'OK',
#         'status': 200
#     }


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
                    "last_update": att,
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


@app.route('/repair', methods=['GET'])
def repair_data():
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

    client = pymongo.MongoClient('mongodb://0.0.0.0:27017')
    database = client['viasoluti-database']
    col = database['data']

    main_dir = path.abspath(path.curdir)
    os.chdir('..')

    data_dir = path.abspath(path.curdir)
    if not 'data' in os.listdir(path.abspath(path.curdir)):
        return {
            'result': 'REPAIR DATA NOT FOUND',
            'status': 404
        }

    os.chdir('data')
    for env in os.listdir(path.abspath(path.curdir)):
        os.chdir(env)
        env_dir = path.abspath(path.curdir)

        for obj in os.listdir(env_dir):
            os.chdir(obj)

            #TODO Captar e mandas os dados pro Mongo

            # retornando
            os.chdir(env_dir)

        os.chdir(data_dir)

    os.chdir(main_dir)

    return {
        'result': 'OK',
        'status': 200
    }


@app.route('/get/id=<_id>&date=<date>')
def get_data(_id, date):

    os.chdir('../data')
    if _id in os.listdir(path.abspath(path.curdir)):
        os.chdir(path.abspath(path.curdir)+f'/{_id}')

        if date in os.listdir(path.abspath(path.curdir)):
            os.chdir(path.abspath(path.curdir)+f'/{date}')

            data = pd.read_csv(path.abspath(path.curdir)+f'/data.csv')
            info = pd.read_csv(path.abspath(path.curdir)+f'/info.csv')

            obj = {
                'imageType': info['imageType'],
                'imageName': info['imageName'],
                'image': info['image'],
                'anchor': info['anchor'],
                'dados': data.to_dict()
            }

            return {
                'response': obj,
                'status': 200,
            }

        else:
            return {
                'response': 'INTERNAL SERVER ERROR',
                'status': 500
            }

    else:
        return {
            'response': 'INTERNAL SERVER ERROR',
            'status': 500
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8045)
