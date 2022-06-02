#!flask/bin/python
from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json

app = Flask(__name__)
PORT = 1445
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_RSRP_Detection.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('=================================================')
print('Start Server Port:', PORT)

import datetime
ISOTIMEFORMAT = '%Y/%m/%d,%H:%M:%S'
import requests

gNB_Name=""
gNB_IP=""


"""
Functions of Parameters
1.gNB_config
2.gNB_UE_RSRP
"""
with open('./config/gNB.json') as gNB_Config_file:
    gNB_Config = json.load(gNB_Config_file)
    gNB_Name=gNB_Config['gNB_Name']
    gNB_IP=gNB_Config['gNB_IP']

    gNB_Config_file.close()

#Obtain RSRP
def Obtain_UE_RSRP(UE_Name):
    gNB_Config={}
    with open('./config/gNB_UEs_RSRP.json', 'r') as gNB_UEs_RSRP_file:
        gNB_Config = json.load(gNB_UEs_RSRP_file)
        gNB_UEs_RSRP_file.close()
    return gNB_Config[UE_Name]

#Update gNB UE RSRP
def Update_gNB_UE_RSRP(UE_Name,RSRP):
    gNB_UEs_RSRP_Config={}
    with open('./config/gNB_UEs_RSRP.json', 'r') as gNB_UEs_RSRP_file:
        gNB_UEs_RSRP_Config = json.load(gNB_UEs_RSRP_file)
        gNB_UEs_RSRP_file.close()
    
    gNB_UEs_RSRP_Config.update({UE_Name:RSRP})
    with open('./config/gNB_UEs_RSRP.json', 'w') as gNB_UEs_RSRP_file:
        json.dump(gNB_UEs_RSRP_Config, gNB_UEs_RSRP_file, ensure_ascii=False)
        gNB_UEs_RSRP_file.close()

def Obtain_gNBConfig_Parameters(key):
    gNB_Config={}
    with open('./config/gNB.json') as gNB_Config_file:
        gNB_Config = json.load(gNB_Config_file)
        gNB_Config_file.close()
    return  gNB_Config[key]

def Obtain_gNBConfig_Parameters(key):
    gNBE_Config={}
    with open('./config/gNB.json', 'r') as gNB_Config_file:
        gNB_Config = json.load(gNB_Config_file)
        gNB_Config_file.close()
    return gNB_Config[key]

def Transfer_UE_RSRP(request_data):
    request_data=request.get_json()

    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1445/gNB_UEs_RSRP_Recieve"
    payload={
        "gNB_Name": gNB_Name,
        "gNB_IP": gNB_IP
    }
    payload.update(request_data)
    headers = {}
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return jsonify(json.loads(response.text))



@app.route("/gNB_Connection_Ready_Request", methods=['POST'])
def gNB_Connection_Ready_Request():
    request_data=request.get_json()
    logging.info(gNB_Name+"["+gNB_IP+"] Getting gNB_Connection_Ready_Request from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    print(gNB_Name+"["+gNB_IP+"] Getting gNB_Connection_Ready_Request from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    
    if(Obtain_gNBConfig_Parameters("gNB_Movement_Status")=="CLOSE"):
        return jsonify({"msg":"error","error":"gNB not ready"})
    
    if(request_data['UE_IP'] not in list(Obtain_gNBConfig_Parameters("gNB_Registered_UEs"))):
        return jsonify({"msg":"error","error":"UE IP: "+request_data['UE_IP']+" not regitered in this gNB["+gNB_IP+"]"})

    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1445/CU_Connection_Ready_Request"
    payload={
        "UE_Name": request_data['UE_Name'],
        "UE_IP": request_data['UE_IP'],
        "UE_Identity":request_data['UE_Identity'],

        "gNB_Name": gNB_Name,
        "gNB_IP": gNB_IP
    }
    headers = {}
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    print(json.loads(response.text)['msg'])
    return jsonify(json.loads(response.text))

@app.route("/gNB_Information_Request", methods=['GET'])
def gNB_Information_Request():

    if(Obtain_gNBConfig_Parameters("gNB_Information_Access_Status")=="CLOSE"):
        return jsonify({"msg":"error","error":"gNB not access"})
    
    gNB_Information={
        "msg":"ok",
        "gNB_Name": gNB_Name,
        "gNB_IP": gNB_IP,

        "gNB_Position_X":Obtain_gNBConfig_Parameters("gNB_Position_X"),
        "gNB_Position_Y":Obtain_gNBConfig_Parameters("gNB_Position_Y"),
        "gNB_BS_Height": Obtain_gNBConfig_Parameters("gNB_BS_Height"),
        "gNB_Antenna_Power": Obtain_gNBConfig_Parameters("gNB_Antenna_Power"),
        "gNB_Center_Frequency": Obtain_gNBConfig_Parameters("gNB_Center_Frequency")
    }
    return jsonify(gNB_Information)

#UE transfer RSRP to gNB
@app.route("/Transfer_RSRP_Information", methods=['POST'])
def Transfer_RSRP_Information():
    request_data=request.get_json()
    logging.info(gNB_Name+"["+gNB_IP+"] Getting RSRP from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    print(gNB_Name+"["+gNB_IP+"] Getting RSRP from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    Update_gNB_UE_RSRP(request_data['UE_Name'],request_data['RSRP'])
    print(request_data)
    Transfer_UE_RSRP(request_data)
    return jsonify({"msg":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)