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
Functions of APIs to UE Access
1.RRCSetupRequest
"""

#Setp(2) Get RRCSetupRequest from gNB_DU and 1.Allocate Cell Group 2.Response to gNB_DU
@app.route("/INITIAL_UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def INITIAL_UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    return jsonify(DL_RRC_MESSAGE_TRANSFER(request_data))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)