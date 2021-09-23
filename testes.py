import requests
import configs
import pandas as pd
import json
import base64


host = configs.host
port = configs.port
# df_dados = pd.read_csv('./datasets/log_1.txt')
#
# response = requests.post(f"http://{host}:5000/send/", json={'dados': df_dados.to_json(orient='records'), 'ambiente': '1'})
#
# response = requests.post(f"http://{host}:5000/treinamento/", json={'ambiente': '1'})
# # print(response.content)
#
response = requests.post(f"http://{host}:{port}/interpolacao/",
                        json={'dados': [
                                        {'x': 0, 'y': 0, 'z': 0, 'date': '2021-03-31 16:00:08'},
                                         {'x': 1, 'y': 1, 'z': 0, 'date': '2021-03-31 16:00:10'},
                                        {'x': 2, 'y': 2, 'z': 0, 'date': '2021-03-31 16:00:12'},
                                         {'x': 2, 'y': 2, 'z': 1, 'date': '2021-03-31 16:00:14'}
                             ], 'ambiente': '1', 'latencia_objetivo': 0.5}
                        )

# files = {
#          'file': ('download.jpeg', open('download.jpeg', 'rb'), 'application/octet-stream')
#     }

# response = requests.post(f"http://{host}:5000/send_img/", files=files)

# response = requests.post(f"http://{host}:5000/send_anchors/", json={"pontos": [{'x': 0.75292, 'y': 0.940541}, {'x': 0.51484, 'y': 0.933359}], "ambiente": '1'})

print(response.content)


# response = requests.get(f"http://{host}:8040/send_img/0")
# response = response.json()
# with open(response['response']['fullname'], "wb") as f:
#     f.write(base64.decodebytes(response['response']['file'].encode("utf-8")))
