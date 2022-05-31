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

PORT = 1440
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
import random
CU_IP="10.0.2.99"

"""
Functions of IDs from configs(Obtain/Allocate)
1.gNB_CU_UE_F1AP_ID(Obatain/Allocate)[DL_RRC_MESSAGE_TRANSFER:]
2.
3.Allocate_
"""

#Obtain gNB_CU_UE_F1AP_ID
def Obtain_gNB_CU_UE_F1AP_ID(gNB_Name,UE_Name):
    gNB_CU_UE_F1AP_ID=""
    gNB_CU_UE_F1AP_ID_Config={}
    gNB_CU_UE_F1AP_ID_Config_gNB={}
    with open('./gNB_Configs/gNB_CU_UE_F1AP_ID.json') as gNB_CU_UE_F1AP_ID_file:
        gNB_CU_UE_F1AP_ID_Config = json.load(gNB_CU_UE_F1AP_ID_file)
        gNB_CU_UE_F1AP_ID_Config_gNB=gNB_CU_UE_F1AP_ID_Config[gNB_Name]
        gNB_CU_UE_F1AP_ID=gNB_CU_UE_F1AP_ID_Config_gNB[UE_Name]
        gNB_CU_UE_F1AP_ID_file.close()

    if(gNB_CU_UE_F1AP_ID==""):
        with open('./gNB_Configs/gNB_CU_UE_F1AP_ID.json','w') as gNB_CU_UE_F1AP_ID_file:
            print("Allocate gNB_CU_UE_F1AP_ID to "+gNB_Name+":"+UE_Name)
            logging.warning("Allocate gNB_CU_UE_F1AP_ID to "+gNB_Name+":"+UE_Name)
            ID=random.randint(0,(2**32))
            gNB_CU_UE_F1AP_ID="{0:b}".format(ID)
            gNB_CU_UE_F1AP_ID_Config_gNB.update({UE_Name:gNB_CU_UE_F1AP_ID})
            gNB_CU_UE_F1AP_ID_Config.update({gNB_Name:gNB_CU_UE_F1AP_ID_Config_gNB})
            json.dump(gNB_CU_UE_F1AP_ID_Config, gNB_CU_UE_F1AP_ID_file, ensure_ascii=False)
            gNB_CU_UE_F1AP_ID_file.close()

    return gNB_CU_UE_F1AP_ID

def Obtain_gNB_CU_CP_UE_E1AP_ID(UE_Name):
    gNB_CU_CP_UE_E1AP_ID=""
    with open('./gNB_Configs/gNB_CU_CP_UE_E1AP_ID.json') as gNB_CU_CP_UE_E1AP_ID_file:
        gNB_CU_CP_UE_E1AP_ID_Config = json.load(gNB_CU_CP_UE_E1AP_ID_file)
        gNB_CU_CP_UE_E1AP_ID=gNB_CU_CP_UE_E1AP_ID_Config[UE_Name]
        gNB_CU_CP_UE_E1AP_ID_file.close()
    return gNB_CU_CP_UE_E1AP_ID

"""
Functions of Parameters from configs(Obtain/Update/Allocate)
1.CUConfig(Obatain/Update)
2.RAT_Frequency_Priority_Information(Allocate)
"""

#Obtain CU Config
def Obtain_CUConfig_Parameters(key):
    CU_Config={}
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        CU_Config_file.close()
    return CU_Config[key]

#Update CU Config
def Update_CUConfig_Parameters(dict_new):
    CU_Config={}
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        CU_Config_file.close()
    
    CU_Config.update(dict_new)
    with open('CU.json', 'w') as CU_Config_file:
        json.dump(CU_Config, CU_Config_file, ensure_ascii=False)
        CU_Config_file.close()

#Allocate RAT_Frequency_Priority_Information if RAT_Frequency_Priority_Informationis not in range
#https://www.developingsolutions.com/DiaDict/Dictionary/RAT-Frequency-Selection-Priority-ID.html
def Allocate_RAT_Frequency_Priority_Information():
    print("Allocate RAT_Frequency_Priority_Information ")
    logging.warning("Allocate RAT_Frequency_Priority_Information ")
    RAT_Frequency_Priority_Information=random.randint(0,256)
    Update_CUConfig_Parameters({"RAT_Frequency_Priority_Information":RAT_Frequency_Priority_Information})


def Obtain_RRCReconfiguration(UE_Name):
    RRCReconfiguration={}
    with open('./gNB_Configs/RRCReconfiguration.json', 'r') as RRCReconfiguration_file:
        RRCReconfiguration = json.load(RRCReconfiguration_file)
        RRCReconfiguration_file.close()
    return RRCReconfiguration[UE_Name]


""""
Functions response gNB_DU
1.DL_RRC_MESSAGE_TRANSFER
"""

#This message is sent by the gNB-CU to transfer the layer 3 message to the gNB-DU over the F1 interface. (F1AP 9.2.3.2)
def DL_RRC_MESSAGE_TRANSFER(gNB_DU_UE_F1AP_ID,gNB_Name,UE_Name):
    print("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:DL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:DL_RRC_MESSAGE_TRANSFER")

    RAT_Frequency_Priority_Information=Obtain_CUConfig_Parameters("RAT_Frequency_Priority_Information")
    if(RAT_Frequency_Priority_Information<0 or RAT_Frequency_Priority_Information>255):
        Allocate_RAT_Frequency_Priority_Information()
        RAT_Frequency_Priority_Information=Obtain_CUConfig_Parameters("RAT_Frequency_Priority_Information")

    DL_RRC_MESSAGE={
        "gNB_CU_UE_F1AP_ID":Obtain_gNB_CU_UE_F1AP_ID(gNB_Name,UE_Name),
        "gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID,
        "SRB_ID":1,#This IE uniquely identifies a SRB for a UE.(F1AP 9.3.17)
        "RRC_Container": "RRCSetup",
        "Execute_Duplication":Obtain_CUConfig_Parameters("Execute_Duplication"),
        "RAT_Frequency_Priority_Information":Obtain_CUConfig_Parameters("RAT_Frequency_Priority_Information"),
        "RRC_Delivery_Status_Request":Obtain_CUConfig_Parameters("RRC_Delivery_Status_Request")
    }
    return DL_RRC_MESSAGE

def Obtain_RAN_UE_NGAP_ID(UE_Name):
    RAN_UE_NGAP_ID=0
    with open('./gNB_Configs/RAN_UE_NGAP_ID.json') as RAN_UE_NGAP_ID_file:
        RAN_UE_NGAP_ID_Config = json.load(RAN_UE_NGAP_ID_file)
        RAN_UE_NGAP_ID=RAN_UE_NGAP_ID_Config[UE_Name]
        RAN_UE_NGAP_ID_file.close()
    return RAN_UE_NGAP_ID

def INITIAL_UE_MESSAGE(UE_Name,RRC_Container,UE_IP,RegisteredAMF):
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_UE_MESSAGE")
    logging.info("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_UE_MESSAGE")
    
    payload={
        "RegisteredAMF":RegisteredAMF,
        "UE_Name":UE_Name,
        "UE_IP":UE_IP,
        "RAN_UE_NGAP_ID":Obtain_RAN_UE_NGAP_ID(UE_Name),
        "NAS_PDU":RRC_Container,
        "User_Location_Information":UE_IP,
        "RRC_Establishment_Cause":"mo-Signalling",
        "5G-S-TMSI":Obtain_CUConfig_Parameters("5G-S-TMSI"),
        "UE_Context_Request":Obtain_CUConfig_Parameters("UE_Context_Request"),
        "Allowed_NSSAI":Obtain_CUConfig_Parameters("Allowed_NSSAI")
    }
    url = "http://"+CU_IP+":1441/INITIAL_UE_MESSAGE"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def BEARER_CONTEXT_SETUP_REQUEST(UE_Name):
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:BEARER_CONTEXT_SETUP_REQUEST")
    logging.info("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:BEARER_CONTEXT_SETUP_REQUEST")
    
    payload={
        "UE_Name":UE_Name,
        "gNB_CU_CP_UE_E1AP_ID":Obtain_gNB_CU_CP_UE_E1AP_ID(UE_Name),
        "Security Information":{
            "Security_Algorithm":{
                "Ciphering_Algorithm":"NEA0",
                "Integrity_Protection_Algorithm":"NIA0"
            },
            "User_Plane_Security_Keys":{
                "Encryption_Key":"",
                "Integrity_Protection_Key":""
            }
        },
        "UE_DL_Aggregate_Maximum_Bit_Rate":732903737658,
        "UE_DL_Maximum_Integrity_Protected_Data_Rate":451033748973,
        "Serving_PLMN":Obtain_CUConfig_Parameters("PLMN"),
        "Activity_Notification_Level":"",
        "Bearer_Context_Status_Change":Obtain_CUConfig_Parameters("Bearer_Context_Status_Change"),
        "CHOICE_System":"NR",
        "PDU_Session_Resource_To_Setup_List":[]
    }
    url = "http://"+CU_IP+":1442/BEARER_CONTEXT_SETUP_REQUEST"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    response_data=json.loads(response.text)
    return UE_CONTEXT_SETUP_REQUEST(response_data)

def UE_CONTEXT_SETUP_REQUEST(data):
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:UE_CONTEXT_SETUP_REQUEST")
    logging.info("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:UE_CONTEXT_SETUP_REQUEST")
    
    context={
        "gNB_CU_UP_UE_E1AP_ID":data['gNB_CU_UP_UE_E1AP_ID'],
        "gNB_CU_CP_UE_E1AP_ID":data['gNB_CU_CP_UE_E1AP_ID'],
        "SpCell_ID":0,
        "ServCellIndex":"00111",
        "SpCell_UL_Configured":False,
        "CU_to_DU_RRC_Information":"UEAssistanceInformation",
        "DRX_Cycle":"",
        "Candidate_SpCell_List":[],
        "SCell To Be Setup List":[],
        "SRB to Be Setup List":[],
        "DRB to Be Setup List":[],
        "Inactivity Monitoring Request":False,
        "RAT-Frequency Priority Information":"009A",
        "RRC_Container":"SecurityModeCommand",
        "gNB-DU UE Aggregate Maximum Bit Rate Uplink":"",
        "Serving PLMN":Obtain_CUConfig_Parameters("PLMN"),
        "RRC_Delivery_Status_Reques":"",
        "Resource Coordination Transfer Information":"",
        "servingCellMO":""
    }
    return context

def BEARER_CONTEXT_MODIFICATION_REQUEST(request_data):
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_REQUEST")
    logging.info("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:BEARER_CONTEXT_MODIFICATION_REQUEST")
    
    payload=request_data
    url = "http://"+CU_IP+":1442/BEARER_CONTEXT_MODIFICATION_REQUEST"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    response_data=json.loads(response.text)

def DL_RRC_MESSAGE_TRANSFER_SecurityModeComplete(request_data):
    print("Enable: CU["+CU_IP+"] UE_Access_Action_gNB.py Function:DL_RRC_MESSAGE_TRANSFER_SecurityModeComplete")
    logging.info("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    data={
        "RRCReconfiguration":Obtain_RRCReconfiguration(request_data['UE_Name'])
    }
    request_data.update(data)
    return request_data

def INITIAL_CONTEXT_SETUP_RESPONSE(request_data):
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_CONTEXT_SETUP_RESPONSE")
    logging.info("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_CONTEXT_SETUP_RESPONSE")
    
    payload=request_data
    url = "http://"+CU_IP+":1441/INITIAL_CONTEXT_SETUP_RESPONSE"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    response_data=json.loads(response.text)

""""
Functions getting request from gNB_DU
1.INITIAL_UL_RRC_MESSAGE_TRANSFER
"""

#Recieve RRC Request
@app.route("/INITIAL_UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def INITIAL_UL_RRC_MESSAGE_TRANSFER():
    print("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_UL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:INITIAL_UL_RRC_MESSAGE_TRANSFER")
    
    request_data = request.get_json()
    gNB_Name=request_data['gNB_Name']
    UE_Name=request_data['UE_Name']
    gNB_DU_UE_F1AP_ID= request_data['gNB_DU_UE_F1AP_ID']

    print(request_data)
    return jsonify(DL_RRC_MESSAGE_TRANSFER(gNB_DU_UE_F1AP_ID,gNB_Name,UE_Name))

@app.route("/UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    print("Enable: CU["+CU_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER")
    logging.info("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print(request_data)
    INITIAL_UE_MESSAGE(request_data['UE_Name'],request_data['RRC-Container'],request_data['UE_IP'],request_data['RegisteredAMF'])
    response_data=BEARER_CONTEXT_SETUP_REQUEST(request_data['UE_Name'])
    return jsonify(response_data)

@app.route("/UE_CONTEXT_SETUP_RESPONSE", methods=['POST'])
def UE_CONTEXT_SETUP_RESPONSE():
    request_data=request.get_json()
    print("Enable: CU["+CU_IP+"] UE_Access_Action_gNB.py Function:UE_CONTEXT_SETUP_RESPONSE")
    logging.info("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print(request_data)
    BEARER_CONTEXT_MODIFICATION_REQUEST(request_data)
    return jsonify({"ok":0})

@app.route("/UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete", methods=['POST'])
def UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete():
    request_data=request.get_json()
    print("Enable: CU["+CU_IP+"] CU_CP_Simulation.py Function:UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete")
    logging.info("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print(request_data)
    return jsonify(DL_RRC_MESSAGE_TRANSFER_SecurityModeComplete(request_data))

@app.route("/UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete", methods=['POST'])
def UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete():
    print("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_CP_Simulation Function:UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete")
    logging.info("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_CP_Simulation.py Function:UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete")
    request_data = request.get_json()
    print(request_data)
    INITIAL_CONTEXT_SETUP_RESPONSE(request_data)
    return jsonify({"msg":"UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)
