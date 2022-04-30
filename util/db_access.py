import pymongo
import requests
from datetime import datetime, timedelta

def date_format():
    return '%Y-%m-%dT%H:%M:%S.%fZ'

def get_latency(form_data):

    latency = 0
    last = None
    for i, data in enumerate(form_data):
        if i == 0:
            last = datetime.strptime(data["date"], date_format())
            continue

        now = datetime.strptime(data["date"], date_format())
        latency += now - last
        last = now
    
    latency /= len(form_data)

    return latency


def get_data_formated(network, gemini, init, end, train=False):
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

    get_params1 = f"startDate={init}&endDate={end}"
    get_params2 = f"deviceType=Tag&network={network}&geminiId={gemini}"

    res = requests.get(f"http://indoorsense.ddns.net:4000/api/root/gemini/save-value?{get_params1}&{get_params2}")
    data = res.json()

    formated = []
    for d in data:
        if train:
            formated.append({
                "id": d["deviceId"],
                "x": d["value"]["fv"]["x"],
                "y": d["value"]["fv"]["y"],
                "z": d["value"]["fv"]["z"],
                "date": d["when"]
            })
        else:
            formated.append({
                "geminiId": d["geminiId"],
                "network": d["value"]["nw"],
                "groupId": d["groupId"],
                "type": d["value"]["dt"],
                "id": d["deviceId"],
                "x": d["value"]["fv"]["x"],
                "y": d["value"]["fv"]["y"],
                "z": d["value"]["fv"]["z"],
                "date": d["when"]
            })
    
    return formated

