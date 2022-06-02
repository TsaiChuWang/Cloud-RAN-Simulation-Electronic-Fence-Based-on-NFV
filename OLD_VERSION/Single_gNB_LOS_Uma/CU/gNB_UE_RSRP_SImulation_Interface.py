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
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_UE_RSRP_SImulation_Interface.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('=================================================')
print('Start Server Port:', PORT)

import datetime
ISOTIMEFORMAT = '%Y/%m/%d,%H:%M:%S'
import requests


CU_Name=""
CU_IP=""

with open('CU.json') as CU_Config_file:
    CU_Config = json.load(CU_Config_file)
    CU_Name=CU_Config['CU_Name']
    CU_IP=CU_Config['CU_IP']
    gNB_List=list(CU_Config['gNBs'])
    CU_Config_file.close()

"""
FUnctions of Parameters
1.CUConfig
"""

#Obtain_CUConfig_Parameters
def Obtain_CUConfig_Parameters(key):
    CUE_Config={}
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        CU_Config_file.close()
    return CU_Config[key]

#Obtain gNB list in CUConfig
def get_gNBs():
    gNB_List=[]
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        gNB_List=list(CU_Config['gNBs'])
        CU_Config_file.close()
    return gNB_List

#Obtain registered UE list in specified gNB
def Obtain_gNB_Registered_UEs(gNB_Name):
    gNB_Registered_UEs=[]
    with open('CU.json', 'r') as CU_Config_file:
        CU_Config = json.load(CU_Config_file)
        gNB_Registered_UEs=CU_Config[gNB_Name]['gNB_Registered_UEs']
        CU_Config_file.close()
    return gNB_Registered_UEs

#Obtain gNB_UEs_RSRP_Configs of specified gNB
def Obtain_gNB_RSRP(gNB_Name):
    gNB_Config={}
    with open('./gNB_Configs/gNB_UEs_RSRP.json', 'r') as gNB_UEs_RSRP_file:
        gNB_Configs = json.load(gNB_UEs_RSRP_file)
        gNB_Config=gNB_Configs[gNB_Name]
        gNB_UEs_RSRP_file.close()
    return gNB_Config


#Update gNB UE RSRP
def Update_gNB_UE_RSRP(gNB_Name,UE_Name,RSRP):
    gNB_UEs_RSRP_Config={}
    with open('./gNB_Configs/gNB_UEs_RSRP.json', 'r') as gNB_UEs_RSRP_file:
        gNB_UEs_RSRP_Config = json.load(gNB_UEs_RSRP_file)
        gNB_UEs_RSRP_file.close()
    
    gNB_Config=gNB_UEs_RSRP_Config[gNB_Name]
    gNB_Config.update({UE_Name:RSRP})
    gNB_UEs_RSRP_Config.update(gNB_Config)
    with open('./gNB_Configs/gNB_UEs_RSRP.json', 'w') as gNB_UEs_RSRP_file:
        json.dump(gNB_UEs_RSRP_Config, gNB_UEs_RSRP_file, ensure_ascii=False)
        gNB_UEs_RSRP_file.close()

@app.route("/CU_Connection_Ready_Request", methods=['POST'])
def CU_Connection_Ready_Request():
    request_data=request.get_json()

    logging.info("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    print("CU["+CU_IP+"] Getting CU_Connection_Ready_Request from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] ")
    
    logging.info(request_data['gNB_Name']+"["+request_data['gNB_IP']+"] Getting gNB_Connection_Ready_Request from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    print(request_data['gNB_Name']+"["+request_data['gNB_IP']+"] Getting gNB_Connection_Ready_Request from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    
    if(Obtain_CUConfig_Parameters("CU_Movement_Status")=="CLOSE"):
        return jsonify({"msg":"error","error":"CU not ready"})
    else:
        print("CU_Movement_Status: "+Obtain_CUConfig_Parameters("CU_Movement_Status"))

    if(request_data['gNB_Name'] not in get_gNBs()):
        return jsonify({"msg":"error","error":"gNB: "+request_data['gNB_Name']+" not regitered in this CU["+CU_IP+"]"})
    else:
        print(request_data['gNB_Name']+" is in the gNB_List")
  
    if(request_data['UE_IP'] not in Obtain_gNB_Registered_UEs(request_data['gNB_Name'])):
       return jsonify({"msg":"error","error":"UE: "+request_data['UE_Name']+" not regitered in this CU["+CU_IP+"]"})
    else:
        print("UE: "+request_data['UE_Name']+" is regitered in this CU["+CU_IP+"]")

    return jsonify({"msg":"CU and gNB Connection Ready"})

#Get RSRP and show in figure
@app.route("/gNB_UEs_RSRP_Recieve", methods=['POST'])
def gNB_UEs_RSRP_Recieve():
    request_data=request.get_json()

    logging.info("CU["+CU_IP+"] Getting RSRP from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] RSRP= "+str(request_data['RSRP']))
    print("CU["+CU_IP+"] Getting RSRP from "+request_data['gNB_Name']+"["+request_data['gNB_IP']+"] RSRP= "+str(request_data['RSRP']))

    Update_gNB_UE_RSRP(request_data['gNB_Name'],request_data['UE_Name'],request_data['RSRP'])
    return jsonify({"msg":"CU and gNB Connection Ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)