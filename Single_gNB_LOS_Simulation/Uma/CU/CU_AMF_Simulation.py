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

PORT = 1441
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/CU_AMF_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
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

def Obtain_AMF_UE_NGAP_ID(UE_Name):
    AMF_UE_NGAP_ID=""
    with open('./gNB_Configs/AMF_UE_NGAP_ID.json', 'r') as AMF_UE_NGAP_ID_file:
        AMF_UE_NGAP_ID = json.load(AMF_UE_NGAP_ID_file)[UE_Name]
        AMF_UE_NGAP_ID_file.close()
    return AMF_UE_NGAP_ID

def DL_RRC_MESSAGE_TRANSFER(gNB_DU_UE_F1AP_ID,gNB_Name,UE_Name):
    print("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:DL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: CU_CP["+CU_IP+"] CU_CP_Simulation.py Function:DL_RRC_MESSAGE_TRANSFER")
    DL_RRC_MESSAGE={
        "gNB_CU_UE_F1AP_ID":Obtain_gNB_CU_UE_F1AP_ID(gNB_Name),
        "gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID,
        "SRB_ID":Obtain_SRB_ID(gNB_Name,UE_Name),
        "RRC_Container": "RRCSetup",
        "Execute_Duplication":Obtain_CUConfig_Parameters("Execute_Duplication"),
        "RAT_Frequency_Priority_Information":Obtain_CUConfig_Parameters("RAT_Frequency_Priority_Information"),
        "RRC_Delivery_Status_Request":Obtain_CUConfig_Parameters("RRC_Delivery_Status_Request")
    }
    return DL_RRC_MESSAGE

def INITIAL_CONTEXT_SETUP_REQUEST(UE_Name,RAN_UE_NGAP_ID,RegisteredAMF):
    data={
        "AMF_UE_NGAP_ID":Obtain_AMF_UE_NGAP_ID(UE_Name),
        "RAN_UE_NGAP_ID":RAN_UE_NGAP_ID,
        "Old_AMF":"",
        "UE_Aggregate_Maximum_Bit_Rate":1,
        "Core_Network_Assistance_Information":{
            "UE_Identity_Index_Value":0,
            "UE_Specific_DRX":"",
            "Periodic_Registration_Update_Timer":"",
            "MICO_Mode_Indication":"",
            "AI_List_for_RRC_Inactive":"",
            "Expected_UE_Behaviour":""
        },
        "GUAMI":RegisteredAMF,
        "Allowed_NSSAI":"Allowed_NSSAI",
        "UE_Security_Capabilities":"NR_Encryption_Algorithms",
        "UE_Radio_Capability":"NR",
        "Security_Key":"",
        "Trace_Activation":"Trace_Session_Activation",
        "Mobility_Restriction_List":[],
        "Masked_IMEISV":"",
        "NAS_PDU":"",
        "Emergency_Fallback_Indicator":"",
        "RRC_Inactive_Transition_Report_Request":"",
        "UE_Radio_Capability_for_Paging":"",
        "Redirection_for_Voice_EPS_Fallback":""
    }
    return data

@app.route("/INITIAL_UE_MESSAGE", methods=['POST'])
def INITIAL_UE_MESSAGE():
    print("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_AMF_Simulation.py Function:INITIAL_UE_MESSAGE")
    logging.info("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_AMF_Simulation.py Function:INITIAL_UE_MESSAGE")
    request_data = request.get_json()
    print(request_data)
    return jsonify(INITIAL_CONTEXT_SETUP_REQUEST(request_data['UE_Name'],request_data['RAN_UE_NGAP_ID'],request_data['RegisteredAMF']))

@app.route("/INITIAL_CONTEXT_SETUP_RESPONSE", methods=['POST'])
def INITIAL_CONTEXT_SETUP_RESPONSE():
    print("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_AMF_Simulation.py Function:INITIAL_CONTEXT_SETUP_RESPONSE")
    logging.info("Enable: CU["+Obtain_CUConfig_Parameters('CU_IP')+"] CU_AMF_Simulation.py Function:INITIAL_CONTEXT_SETUP_RESPONSE")
    request_data = request.get_json()
    print(request_data)
    return jsonify({})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)
