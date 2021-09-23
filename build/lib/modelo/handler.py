from flask import jsonify
import pandas as pd
import traceback
from datetime import datetime
from modelo.algoritmos import interpolacao#, rna, random_forest
import pickle
import configs
import numpy as np
import os
from datetime import datetime

ERRO_SERVIDOR = "Erro no servidor"


def treinamento(ambiente: str):
    try:
        # df_dados = pd.DataFrame(eval(infos_json)) ###TEMPORARIO
        df_dados = get_dados(ambiente)
        modelagem.run(df_dados, ambiente=ambiente, latencia=5)
        return jsonify({"response": "OK"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=ERRO_SERVIDOR), 500


def gen_points_to_predict(dados, latencia):
    latencia = 1000000000 * latencia
    def gen_points(row: dict):
        list_dict = []
        for t in np.arange(row['t1'] + latencia, row['t3'], latencia):
            new_row = row.copy()
            new_row['t2'] = np.int64(t)
            list_dict.append(new_row)
        return list_dict
            
    list_dicts = list(dados.apply(lambda row: gen_points(dict(row)), axis=1))

    df_to_predict = pd.DataFrame()
    ds = [len(list_dict) for list_dict in list_dicts]
    for dict_list in list_dicts:
        df = pd.DataFrame(dict_list)
        df_to_predict = pd.concat([df_to_predict, df])

    df_to_predict.reset_index(inplace=True, drop=True)
    return df_to_predict, ds


def predicao(exemplo_json: dict, ambiente: str, latencia: int):
    try:
        df = pd.DataFrame(exemplo_json)
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].values.astype(np.int64)

        df_exemplo_start = df.query("index % 2 == 0")
        df_exemplo_end = df.query("index % 2 != 0")

        df_exemplo_start.reset_index(inplace=True)
        df_exemplo_start.drop(columns=['index'], inplace=True)
        df_exemplo_start.columns = ['x1', 'y1', 'z1', 't1']
        df_exemplo_start['index'] = df_exemplo_start.index

        df_exemplo_end.reset_index(inplace=True)
        df_exemplo_end.drop(columns=['index'], inplace=True)
        df_exemplo_end.columns = ['x3', 'y3', 'z3', 't3']
        df_exemplo_end['index'] = df_exemplo_end.index

        df_exemplo = df_exemplo_start.merge(df_exemplo_end, on='index').drop(columns=['index'])
        df_exemplo, ds = gen_points_to_predict(df_exemplo, latencia)
        print(df_exemplo)
        df_exemplo['t2'] = df_exemplo['t2'].apply(lambda x: datetime.fromtimestamp(x/1000000000).strftime("%Y-%m-%d %H:%M:%S:%f"))
        t2_realtime = df_exemplo['t2']

        t2_relative_list = []
        t3_relative_list = []
        for d in ds:
            for i in range(1, d + 1):
                t2_relative_list.append(i)
                t3_relative_list.append(d + 1)

        df_exemplo['t3'] = t3_relative_list
        df_exemplo['t2'] = t2_relative_list
        
        #if os.path.exists(f'./modelagem/{ambiente}'):
        #    loaded_model = pickle.load(open(f"./modelagem/{ambiente}/rf/finalized_model.sav", 'rb'))
        #    df_predito = modelagem.predict(loaded_model, df_exemplo, latencia)
        #else:
        df_predito = interpolacao.run(df_exemplo, 'x1', 'y1', 'z1', 'x3', 'y3', 'z3', 't3', 't2')
        df_predito['date'] = t2_realtime
        print(df_predito)
        return jsonify({'response': df_predito.to_dict(orient='records')}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=ERRO_SERVIDOR), 500


def send(infos_json: dict, ambiente: str):
    try:
        df = pd.DataFrame(eval(infos_json))
        df['ambiente'] = ambiente
        if not os.path.exists(f'./datasets/{ambiente}'):
            os.mkdir(f'./datasets/{ambiente}')
        date = datetime.today().date()
        df.to_csv(f'./datasets/{ambiente}/{str(date)}.csv')
        df.to_csv(f'./../../dashboard-viasoluti/data/data_{ambiente}.csv')
        return jsonify({"response": "OK"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(error=ERRO_SERVIDOR), 500


# def get_dados(ambiente: str):30

# def recv_img(ambiente):
#     # response = requests.post(f"http://{host}:5000/send_img/{ambiente}")
#     img = open("/home/carlos/Área de Trabalho/dashboard-viasoluti/envs/001.jpeg", "rb")
#     img_bytes = img
#     image = Image.open(img_bytes)
#     image.save(f"/home/carlos/Área de Trabalho/dashboard-viasoluti/envs/data_{ambiente}.jpeg")
#     anchor = {"pontos": [{"x": -20, "y": -20}, {"x": 20, "y": 20}]}#response anchor json
#     anchor_df = pd.DataFrame(anchor["pontos"])
#     anchor_df.to_csv(f"/home/carlos/Área de Trabalho/dashboard-viasoluti/anchors/anch_{ambiente}.csv", index=False)
#     return "OK"


# def send_img(file_request):
#     try:
#         fullname = file_request.filename
#         img = open(f"./planta/data_{fullname}", 'wb')
#         img.write(file_request.read())
#         return jsonify({"response": "OK"}), 200
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify(error=ERRO_SERVIDOR), 500

# def send_anchor(anchor):
#     try:
#         p_anchor = anchor['pontos']
#         ambiente = anchor['ambiente']
#         df_anchor = pd.DataFrame.from_dict(p_anchor)
#         df_anchor.to_csv(f"./planta/anch_{ambiente}.csv", index=False)
#         return jsonify({"response": "OK"}), 200
#     except Exception as e:
#         traceback.print_exc()
#         return jsonify(error=ERRO_SERVIDOR), 500