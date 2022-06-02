#!flask/bin/python
from os import close, stat
from flask import Flask, jsonify, request
app = Flask(__name__)
import pymongo
from bson.objectid import ObjectId
import time
import logging
import json

import pymongo
from bson.objectid import ObjectId

PORT = 1442
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/CU_CP_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('=======================================')
print('Start Server Port:', PORT)

#client = pymongo.MongoClient(host='localhost', port=27017)
#db = client['gNBs']

#collection_gNB_PARAMETERs= db['gNB_PARAMETERs']
#collection_gNB_A= db['gNB_A']

import datetime
ISOTIMEFORMAT = '%Y/%m/%d,%H:%M:%S'
import requests
CU_IP="10.0.2.99"

def Obtain_CUConfig_Parameters(key):
    CU_Config={}
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        CU_Config_file.close()
    return CU_Config[key]

def Obtain_gNB_CU_CP_UE_E1AP_ID(UE_Name):
    gNB_CU_CP_UE_E1AP_ID=""
    with open('./gNB_Configs/gNB_CU_CP_UE_E1AP_ID.json') as gNB_CU_CP_UE_E1AP_ID_file:
        gNB_CU_CP_UE_E1AP_ID_Config = json.load(gNB_CU_CP_UE_E1AP_ID_file)
        gNB_CU_CP_UE_E1AP_ID=gNB_CU_CP_UE_E1AP_ID_Config[UE_Name]
        gNB_CU_CP_UE_E1AP_ID_file.close()
    return gNB_CU_CP_UE_E1AP_ID

def Obtain_gNB_CU_UP_UE_E1AP_ID(UE_Name):
    gNB_CU_UP_UE_E1AP_ID=""
    with open('./gNB_Configs/gNB_CU_UP_UE_E1AP_ID.json') as gNB_CU_UP_UE_E1AP_ID_file:
        gNB_CU_UP_UE_E1AP_ID_Config = json.load(gNB_CU_UP_UE_E1AP_ID_file)
        gNB_CU_UP_UE_E1AP_ID=gNB_CU_UP_UE_E1AP_ID_Config[UE_Name]
        gNB_CU_UP_UE_E1AP_ID_file.close()
    return gNB_CU_UP_UE_E1AP_ID

def BEARER_CONTEXT_SETUP_RESPONSE(UE_Name,request_data):
    print("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_SETUP_RESPONSE")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_SETUP_RESPONSE")
    data={
        "gNB_CU_UP_UE_E1AP_ID":Obtain_gNB_CU_UP_UE_E1AP_ID(UE_Name),
        "gNB_CU_CP_UE_E1AP_ID":request_data['gNB_CU_CP_UE_E1AP_ID'],
        "CHOICE_System":request_data['CHOICE_System'],
        "PDU_Session_Resource_Success":[{
            "PDU_Session_ID":"",
            "NG_U_DL_UP_Transport_Layer_Information":"",
            "PDU Session_Data_Forwarding_Information_Response":"",
            "DRB_Setup_List":[
                {
                    "DRB_ID":"",
                    "DRB Data_forwarding_information_Response":"",
                    "UL_UP_Parameters":"",
                    "Flow_Setup_List":[],
                    "Flow_Failed_List":[]
                }
            ]
        }],
        "PDU_Session_Resource_Failed":[{
            "PDU_Session_ID":"",
            "Cause":""
        }]
    }
    return data

def BEARER_CONTEXT_MODIFICATION_RESPONSE(request_data):
    print("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_RESPONSE")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_RESPONSE")
    return request_data

@app.route("/BEARER_CONTEXT_SETUP_REQUEST", methods=['POST'])
def BEARER_CONTEXT_SETUP_REQUEST():
    print("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_SETUP_REQUEST")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_SETUP_REQUEST")
    request_data = request.get_json()
    print(request_data)

    return jsonify(BEARER_CONTEXT_SETUP_RESPONSE(request_data['UE_Name'],request_data))

@app.route("/BEARER_CONTEXT_MODIFICATION_REQUEST", methods=['POST'])
def BEARER_CONTEXT_MODIFICATION_REQUEST():
    print("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_REQUEST")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_UP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_REQUEST")
    request_data = request.get_json()
    print(request_data)
    return jsonify(BEARER_CONTEXT_MODIFICATION_RESPONSE(request_data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)
