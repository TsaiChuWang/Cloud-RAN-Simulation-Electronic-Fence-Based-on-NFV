from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json
import socket
import random
import requests

app = Flask(__name__)
PORT = 1440
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/CU_Uma_LOS_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)

CU_IP="10.0.2.99"
#Initialize Parameter
def Initialize():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    CU_IP=s.getsockname()[0]

"""
Functions of Configurations
1.CU_gNB_UEs_Configuration
2.gNB_CU_UE_F1AP_ID
"""
#Obtain CU_gNB_UEs_Configuration.json
def Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name):
    CU_gNB_UEs_Configuration={}
    with open('./configuration/CU_gNB_UEs_Configuration.json') as CU_gNB_UEs_Configuration_file:
        CU_gNB_UEs_Configuration = json.load(CU_gNB_UEs_Configuration_file)
        CU_gNB_UEs_Configuration_file.close()
    return CU_gNB_UEs_Configuration[gNB_Name][UE_Name]

#Update CU_gNB_UEs_Configuration.json
def Update_CU_gNB_UEs_Configuration(gNB_Name,UE_Name,data):
    CU_gNB_UEs_Configuration={}
    with open('./configuration/CU_gNB_UEs_Configuration.json') as CU_gNB_UEs_Configuration_file:
        CU_gNB_UEs_Configuration = json.load(CU_gNB_UEs_Configuration_file)
        CU_gNB_UEs_Configuration_file.close()
    
    CU_gNB_UEs_Configuration_gNB=CU_gNB_UEs_Configuration[gNB_Name]
    CU_gNB_UEs_Configuration_UE=CU_gNB_UEs_Configuration_gNB[UE_Name]
    CU_gNB_UEs_Configuration_UE.update(data)
    CU_gNB_UEs_Configuration_gNB.update({UE_Name:CU_gNB_UEs_Configuration_UE})
    CU_gNB_UEs_Configuration.update({gNB_Name:CU_gNB_UEs_Configuration_gNB})
    with open('./configuration/CU_gNB_UEs_Configuration.json', 'w') as CU_gNB_UEs_Configuration_file:
        json.dump(CU_gNB_UEs_Configuration, CU_gNB_UEs_Configuration_file, ensure_ascii=False)
        CU_gNB_UEs_Configuration_file.close()

#Allocate gNB-CU UE F1AP ID
def Allocate_gNB_CU_UE_F1AP_ID(gNB_Name,UE_Name):
    ID=random.randint(0,2**32)
    gNB_CU_UE_F1AP_ID="{0:b}".format(ID)
    Update_CU_gNB_UEs_Configuration(gNB_Name,UE_Name,{"gNB_CU_UE_F1AP_ID":gNB_CU_UE_F1AP_ID})
    return gNB_CU_UE_F1AP_ID

#Allocate gNB-DU UE F1AP ID
def Allocate_gNB_DU_UE_F1AP_ID(gNB_Name,UE_Name):
    ID=random.randint(0,2**32)
    gNB_DU_UE_F1AP_ID="{0:b}".format(ID)
    Update_CU_gNB_UEs_Configuration(gNB_Name,UE_Name,{"gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID})
    return gNB_DU_UE_F1AP_ID

#Allocate eNB_UE_S1AP_ID
def Allocate_eNB_UE_S1AP_ID(gNB_Name,UE_Name):
    ID=random.randint(0,2**24)
    eNB_UE_S1AP_ID="{0:b}".format(ID)
    Update_CU_gNB_UEs_Configuration(gNB_Name,UE_Name,{"eNB_UE_S1AP_ID":eNB_UE_S1AP_ID})
    return eNB_UE_S1AP_ID

"""
Functions response to DU
1.DL_RRC_MESSAGE_TRANSFER
"""

#Step(3) forward the RRC message RRCSetup to the gNB-DU.
def DL_RRC_MESSAGE_TRANSFER(request_data):
    UE_Name=request_data['UE_Name']
    gNB_Name=request_data['gNB_Name']
    
    response_data={
        "UE_Name":UE_Name,
        "UE_IP":request_data['UE_IP'],
        "gNB_Name":request_data['gNB_Name'],
        "gNB_IP":request_data['gNB_IP'],
        "gNB_DU_UE_F1AP_ID":Allocate_gNB_DU_UE_F1AP_ID(gNB_Name,UE_Name),
        "gNB_CU_UE_F1AP_ID":Allocate_gNB_CU_UE_F1AP_ID(gNB_Name,UE_Name),
        "SRB_ID":1,
        "RRC_Container":"RRCSetup",
        "Execute_Duplication":True,
        "RAT_Frequency_Priority_Information":{
            "EN_DC":{
                "Subscriber_Profile_ID_RAT_Frequency_priority":"111111"
            },
            "NG_RAN":{
                "Index_RAT_Frequency_Selection_Priority":"1010111"
            }
        },
        "RRC_Delivery_Status_Request":True
    }
    return response_data

"""
Functions of APIs to UE Access(CU-CP)
1.RRCSetupRequest
2.UL_RRC_MESSAGE_TRANSFER
"""

#Setp(2) Get RRCSetupRequest from gNB_DU and 1.Allocate Cell Group 2.Response to gNB_DU
@app.route("/INITIAL_UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def INITIAL_UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    return jsonify(DL_RRC_MESSAGE_TRANSFER(request_data))

#Setp(6) Get RRCSetupRequest from gNB_DU and 1.Allocate Cell Group 2.Response to gNB_DU
@app.route("/UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    INITIAL_UE_MESSAGE_Data=INITIAL_UE_MESSAGE(request_data)
    INITIAL_CONTEXT_SETUP_REQUEST_Data=INITIAL_CONTEXT_SETUP_REQUEST(INITIAL_UE_MESSAGE_Data)
    print(INITIAL_UE_MESSAGE_Data)
    return jsonify({})

"""
Fumctions about AMF
1.INITIAL UE MESSAGE
2.INITIAL CONTEXT SETUP REQUEST
"""
#Step(7)
def INITIAL_UE_MESSAGE(request_data):
    gNB_Name=request_data["gNB_Name"]
    UE_Name=request_data["UE_Name"]
    ID="{0:b}".format(random.randint(0,3))
    GS_TAI=str(request_data["Selected_PLMN_ID"])+ID
    eNB_UE_S1AP_ID=Allocate_eNB_UE_S1AP_ID(gNB_Name,UE_Name)
    INITIAL_UE_MESSAGE_Data={
        "eNB_UE_S1AP_ID":eNB_UE_S1AP_ID,
        "NAS_PDU":"INITIAL_UE_MESSAGE",
        "5GS_TAI":GS_TAI,
        "RRC_Establishment_Cause":"mo-Signalling",
        "User_Location_Information":{
            "NR_CGI":request_data["NR_CGI"],
            "5GS_TAI":GS_TAI,
            "Age_Location":5
        },
        "Allowed_NSSAI":"11001001011111101011110001100011"
    }
    return INITIAL_UE_MESSAGE_Data

#Step(8)
def INITIAL_CONTEXT_SETUP_REQUEST(INITIAL_UE_MESSAGE_Data):
    INITIAL_CONTEXT_SETUP_REQUEST_Data={
        "MME_UE_S1AP_ID":"{0:b}".format(random.randint(0,2**32)),
        "eNB_UE_S1AP_ID":INITIAL_UE_MESSAGE_Data["eNB_UE_S1AP_ID"],
        "UE_Aggregate_Maximum_Bit_Rate":{
            "UE_Aggregate_Maximum_Bit_Rate_Downlink":3080,
            "UE_Aggregate_Maximum_Bit_Rate_Uplink":1100,
            "Extended_UE_Aggregate_Maximum_Bit_Rate_Downlink":3080,
            "Extended_UE_Aggregate_Maximum_Bit_Rate_Uplink":1100
        },
        "E_RAB__Be_Setup_Item_IEs":{
            "E_RAB_ID":"{0:b}".format(random.randint(0,16)),
            "E_RAB_Level_QoS_Parameters":""
        },
        "UE_Security_Capabilities":{
            "Encryption_Algorithms":"",
            "Integrity_Protection_Algorithms":""
        },
        "Security_Key":"{0:b}".format(random.randint(0,2**256))
    }
    return INITIAL_CONTEXT_SETUP_REQUEST_Data

"""
Functions about CU-UP
1.
"""

"""
Functions of RSRP Detections
1.RecieveRSRPResponse
"""
@app.route("/RecieveRSRPResponse", methods=['POST'])
def RecieveRSRPResponse():
    request_data=request.get_json()
    Update_CU_gNB_UEs_Configuration(request_data["gNB_Name"],request_data["UE_Name"],{"RSRP":request_data["RSRP"]})
    return "RECIEVE SUCCESS"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)