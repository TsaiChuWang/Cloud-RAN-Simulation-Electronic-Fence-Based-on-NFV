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
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_Uma_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)

"""
Functions Related to Parameters:
1.gNB_IP
2.gNB_DU_UE_F1AP_ID(Obtain/Allocate)
3.gNB_UEs_Configuration
4.gNB_Configuration
5.C_RNTI
6.CellGroupConfiguration
7.Transaction_ID
"""
gNB_IP=""
CU_IP="10.0.2.99"

#Initialize Parameter
def Initialize():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    gNB_IP=s.getsockname()[0]

#Obtain gNB-DU UE F1AP ID for INITIAL UL RRC MESSAGE TRANSFER
def Obtain_gNB_DU_UE_F1AP_ID(UE_Name):
    gNB_DU_UE_F1AP_ID=Obtain_gNB_UEs_Configuration()[UE_Name]['gNB_DU_UE_F1AP_ID']
    if(gNB_DU_UE_F1AP_ID==""):
        logging.warning("gNB-DU UE F1AP ID is empty for "+UE_Name)
        gNB_DU_UE_F1AP_ID=Allocate_gNB_DU_UE_F1AP_ID(UE_Name)
        Update_gNB_UEs_Configuration(UE_Name,{"gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID})
    return gNB_DU_UE_F1AP_ID

#Allocate gNB-DU UE F1AP ID if it is empty
def Allocate_gNB_DU_UE_F1AP_ID(UE_Name):
    ID=random.randint(0,2**32)
    Update_gNB_UEs_Configuration(UE_Name,{"gNB_DU_UE_F1AP_ID":"{0:b}".format(ID)})
    return "{0:b}".format(ID)

#Obtain gNB_UEs_Configuration.json 
def Obtain_gNB_UEs_Configuration():
    gNB_UEs_Configuration={}
    with open('./configuration/gNB_UEs_Configuration.json') as gNB_UEs_Configuration_file:
        gNB_UEs_Configuration = json.load(gNB_UEs_Configuration_file)
        gNB_UEs_Configuration_file.close()
    return gNB_UEs_Configuration

#Update gNB_UEs_Configuration.json 
def Update_gNB_UEs_Configuration(UE_Name,data):
    gNB_UEs_Configuration=Obtain_gNB_UEs_Configuration()
    gNB_UEs_Configuration_UE=gNB_UEs_Configuration[UE_Name]
    gNB_UEs_Configuration_UE.update(data)
    gNB_UEs_Configuration.update({UE_Name:gNB_UEs_Configuration_UE})
    with open('./configuration/gNB_UEs_Configuration.json', 'w') as gNB_UEs_Configuration_file:
        json.dump(gNB_UEs_Configuration, gNB_UEs_Configuration_file, ensure_ascii=False)
        gNB_UEs_Configuration_file.close()

#Obtain gNB_Configuration
def Obtain_gNB_Configuration():
    gNB_Configuration={}
    with open('./configuration/gNB_Configuration.json') as gNB_Configuration_file:
        gNB_Configuration = json.load(gNB_Configuration_file)
        gNB_Configuration_file.close()
    return gNB_Configuration

#Update gNB_Configuration
def Update_gNB_Configuration(data):
    gNB_Configuration=Obtain_gNB_Configuration()
    gNB_Configuration.update(data)
    with open('./configuration/gNB_Configuration.json', 'w') as gNB_Configuration_file:
        json.dump(gNB_Configuration, gNB_Configuration_file, ensure_ascii=False)
        gNB_Configuration_file.close()

#Allocate C_RNTI for UE
def Allocate_C_RNTI(UE_Name):
    ID=random.randint(0,65535)
    C_RNTI="{0:b}".format(ID)
    Update_gNB_UEs_Configuration(UE_Name,{"C_RNTI":C_RNTI})
    return C_RNTI

#Obtain Cell Group Configuration
#not recommend
def Obtain_CellGroupConfiguration():
    CellGroupConfiguration={}
    with open('./configuration/CellGroupConfiguration.json') as CellGroupConfiguration_file:
        CellGroupConfiguration = json.load(CellGroupConfiguration_file)
        CellGroupConfiguration_file.close()
    return CellGroupConfiguration

#Allocate Transaction ID
def Allocate_Transaction_ID(UE_Name):
    ID=random.randint(0,255)
    Transaction_ID="{0:b}".format(ID)
    Update_gNB_UEs_Configuration(UE_Name,{"Transaction_ID":Transaction_ID})
    return Transaction_ID

#Obtain radioBearerConfig
def Obtain_radioBearerConfig():
    radioBearerConfig={}
    with open('./configuration/radioBearerConfig.json') as radioBearerConfig_file:
        radioBearerConfig = json.load(radioBearerConfig_file)
        radioBearerConfig_file.close()
    return radioBearerConfig

"""
Functions to request gNB_DU
1.INITIAL UL RRC MESSAGE TRANSFER
"""

#The purpose of the Initial UL RRC Message Transfer procedure is to transfer the initial RRC message to the gNB-CU.
def INITIAL_UL_RRC_MESSAGE_TRANSFER(request_data):
    logging.info(gNB_IP+": perform INITIAL_UL_RRC_MESSAGE_TRANSFER to "+CU_IP)
    url = "http://"+CU_IP+":1440/INITIAL_UL_RRC_MESSAGE_TRANSFER"
    UE_Name=request_data["UE_Name"]
    payload={
        "UE_Name":UE_Name,
        "UE_IP":request_data["UE_IP"],
        "gNB_Name":Obtain_gNB_Configuration()['gNB_Name'],
        "gNB_IP":gNB_IP,
        "gNB_DU_UE_F1AP_ID":Obtain_gNB_DU_UE_F1AP_ID(UE_Name),
        "NR_CGI":Obtain_gNB_Configuration()["NR_CGI"],
        "C_RNTI":Allocate_C_RNTI(UE_Name),
        "RRC_Container":"RRCSetupRequest",
        "DU_CU_RRC_Container":{
            "CellGroupConfig":Obtain_CellGroupConfiguration()
        },
        "SUL_Access_Indication":True,
        "Transaction_ID":Allocate_Transaction_ID(UE_Name)
    }
    payload=json.dumps(payload)
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)

"""
Functions Response Data to UE
1.RRCSetup
"""

#Step(4) Response RRCSetup message to UE
def RRCSetup():
    logging.info("Response RRCSetUp to UE.")
    radioBearerConfig=Obtain_radioBearerConfig()
    CellGroupConfig=Obtain_CellGroupConfiguration()
    data={"RRC":"RRCSetUp","radioBearerConfig":radioBearerConfig,"masterCellGroup":CellGroupConfig}
    return data

"""
Functions of APIs to UE Access
1.RRCSetupRequest
"""

#Setp(1) Get RRCSetupRequest from UE and 1.to CU 2.Response to UE
@app.route("/RRCSetupRequest", methods=['POST'])
def RRCSetupRequest():
    logging.info("Enable: gNB["+gNB_IP+"] Function:RRCSetupRequest")
    request_data=request.get_json()

    UE_Name=request_data['UE_Name']
    response_data=INITIAL_UL_RRC_MESSAGE_TRANSFER(request_data)
    Update_gNB_UEs_Configuration(UE_Name,{"gNB_DU_UE_F1AP_ID":response_data["gNB_DU_UE_F1AP_ID"]})
    Update_gNB_UEs_Configuration(UE_Name,{"gNB_CU_UE_F1AP_ID":response_data["gNB_CU_UE_F1AP_ID"]})

    return jsonify(RRCSetup())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)

