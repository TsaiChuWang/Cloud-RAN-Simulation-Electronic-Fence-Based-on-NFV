from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json
import socket
import random
import requests



app = Flask(__name__)
PORT = 1441
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_Uma_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)

gNB_IP=""
CU_IP="10.0.2.99"

"""
FUNCTIONS OF PARAMETER ABOUT CONFIG
1.UEs_Configurations
2.gNB_CU_UE_F1AP_ID
3.gNB_DU_UE_F1AP_ID
4.gNB_Information
5.System_Field_Configuration
"""
def Obtain_UEs_Configurations(UE_Name):
    UEs_Configurations={}
    with open('./configuration/UEs_Configuration.json') as UEs_Configurations_file:
        UEs_Configurations = json.load(UEs_Configurations_file)
        UEs_Configurations_file.close()
    if(UE_Name==""):
        return UEs_Configurations
    return UEs_Configurations[UE_Name]

def Update_UEs_Configurations(UE_Name,data):
    UEs_Configurations=Obtain_UEs_Configurations("")
    UEs_Configurations_UE=UEs_Configurations[UE_Name]
    UEs_Configurations_UE.update(data)
    UEs_Configurations.update({UE_Name:UEs_Configurations_UE})
    with open('./configuration/UEs_Configuration.json', 'w') as UEs_Configurations_file:
        json.dump(UEs_Configurations, UEs_Configurations_file, ensure_ascii=False)
        UEs_Configurations_file.close()

def Update_UEs_Configurations_WHOLE(UE_Name,data):
    UEs_Configurations=Obtain_UEs_Configurations("")
    UEs_Configurations.update({UE_Name:data})
    with open('./configuration/UEs_Configuration.json', 'w') as UEs_Configurations_file:
        json.dump(UEs_Configurations, UEs_Configurations_file, ensure_ascii=False)
        UEs_Configurations_file.close()

#Allocate gNB-CU UE F1AP ID
def Allocate_gNB_CU_UE_F1AP_ID():
    ID=random.randint(0,2**32)
    gNB_CU_UE_F1AP_ID="{0:b}".format(ID)
    return gNB_CU_UE_F1AP_ID

#Allocate gNB-DU UE F1AP ID
def Allocate_gNB_DU_UE_F1AP_ID():
    ID=random.randint(0,2**32)
    gNB_DU_UE_F1AP_ID="{0:b}".format(ID)
    return gNB_DU_UE_F1AP_ID

def Update_Information_gNBs(response_data):
    with open('./configuration/gNBs_Configuration.json', 'w') as gNBs_Configuration_file:
        json.dump(response_data, gNBs_Configuration_file, ensure_ascii=False)
        gNBs_Configuration_file.close()

def Obtain_gNB_Information(gNB_Name):
    gNBs_Configuration={}
    with open('./configuration/gNBs_Configuration.json') as gNBs_Configuration_file:
        gNBs_Configuration = json.load(gNBs_Configuration_file)
        gNBs_Configuration_file.close()
    if(gNB_Name==""):
        return gNBs_Configuration
    return gNBs_Configuration[gNB_Name]

def Obtain_System_Field_Configuration(key):
    System_Field_Configuration={}
    with open('./configuration/System_Field_Configuration.json', 'r') as System_Field_Configuration_file:
        System_Field_Configuration = json.load(System_Field_Configuration_file)
        System_Field_Configuration_file.close()
    if(key==""):
        return System_Field_Configuration
    return System_Field_Configuration[key]


"""
Functions of RSRP Detection
1.Calculate_RSRPs_Threephase_Stator
2.UE_OUT_OF_RANGE(UE_Name)
"""
def Calculate_RSRPs_Threephase_Stator(request_data):
    UE_Position_X=request_data["UE_Position_X"]
    UE_Position_Y=request_data["UE_Position_Y"]
    return UE_Position_X,UE_Position_Y

def UE_OUT_OF_RANGE(UE_Name,UE_Position_X,UE_Position_Y):
    Range_Type=Obtain_System_Field_Configuration("Range_Type")
    X_OUT=False
    Y_OUT=False
    if(Range_Type=="Rectangle"):
        if(UE_Position_X<=Obtain_System_Field_Configuration("Rectangle_Start_X") or UE_Position_X>=Obtain_System_Field_Configuration("Rectangle_Start_X")+Obtain_System_Field_Configuration("Rectangle_Width")):
            X_OUT=True
        if(UE_Position_Y<=Obtain_System_Field_Configuration("Rectangle_Start_Y") or UE_Position_Y>=Obtain_System_Field_Configuration("Rectangle_Start_Y")+Obtain_System_Field_Configuration("Rectangle_Length")):
            Y_OUT=True
        Update_UEs_Configurations(UE_Name,{"UE_OUT_OF_RANGE":(X_OUT or Y_OUT)})
    
"""
Functions response to DU
1.DL_RRC_MESSAGE_TRANSFER
"""

#Step(3) forward the RRC message RRCSetup to the gNB-DU.
def DL_RRC_MESSAGE_TRANSFER(request_data):
    UE_Name=request_data['UE_Name']
    gNB_Name=request_data['MC']
    gNB_DU_UE_F1AP_ID=Allocate_gNB_DU_UE_F1AP_ID()
    gNB_CU_UE_F1AP_ID=Allocate_gNB_CU_UE_F1AP_ID()
    response_data={
        "UE_Name":UE_Name,
        "UE_IP":request_data['UE_IP'],
        "gNB_Name":gNB_Name,
        "gNB_IP":request_data['gNB_IP'],
        "gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID,
        "gNB_CU_UE_F1AP_ID":gNB_CU_UE_F1AP_ID,
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
    UE_Information=request_data["UE_Information"]
    UE_Information.update({"Transaction_ID":request_data["Transaction_ID"]})
    UE_Information.update({"gNB_DU_UE_F1AP_ID":request_data["gNB_DU_UE_F1AP_ID"]})
    UE_Information.update({"C_RNTI":request_data["C_RNTI"]})
    UE_Information.update({"MCG":request_data["MCG"]})
    UE_Information.update({"SCG":request_data["SCG"]})
    UE_Information.update({"Connected_Primary_Cell_Name":gNB_Name})
    UE_Information.update({"Connected_Primary_Cell_IP":request_data["gNB_IP"]})
    UE_Information.update({"Connected_Secondary_Cell_Name":request_data["SC"]})
    UE_Information.update({"Connected_Secondary_Cell_IP":request_data["gNB_IP"]})
    UE_Information.update({"gNB_DU_UE_F1AP_ID":gNB_DU_UE_F1AP_ID})
    UE_Information.update({"Connected_Secondary_Cell_IP":gNB_CU_UE_F1AP_ID})
    Update_UEs_Configurations_WHOLE(request_data["UE_Name"],UE_Information)
    response_data.update({"UE_Information":UE_Information})

    return response_data


#Recive RSRP from UE
@app.route("/RecievegNB_Information", methods=['POST'])
def RecievegNB_Information():
    request_data=request.get_json()
    Update_Information_gNBs(request_data)
    return "RECIEVE SUCCESS"

#Recive RSRP from UE
@app.route("/INITIAL_UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def INITIAL_UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    response_data=DL_RRC_MESSAGE_TRANSFER(request_data)
    response_data.update({"RRC":"RRCSetUp"})
    return jsonify(response_data)

#Recive RSRP from UE
@app.route("/Recieve_RSRP", methods=['POST'])
def Recieve_RSRP():
    request_data=request.get_json()
    UE_Position_X,UE_Position_Y=Calculate_RSRPs_Threephase_Stator(request_data)
    UE_Name=request_data["UE_Name"]
    Update_UEs_Configurations(UE_Name,{"UE_Position_X":UE_Position_X})
    Update_UEs_Configurations(UE_Name,{"UE_Position_Y":UE_Position_Y})
    Update_UEs_Configurations(UE_Name,{"RSRP":request_data["RSRP"]})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Name":request_data["Connected_Primary_Cell_Name"]})
    Update_UEs_Configurations(UE_Name,{"Connected_Secondary_Cell_Name":request_data["Connected_Secondary_Cell_Name"]})

    Primary_Cell=Obtain_gNB_Information(request_data["Connected_Primary_Cell_Name"])
    Connected_Primary_gNB_Position_X=Primary_Cell["gNB_Position_X"]
    Connected_Primary_gNB_Position_Y=Primary_Cell["gNB_Position_Y"]

    Update_UEs_Configurations(UE_Name,{"Connected_Primary_gNB_Position_X":Connected_Primary_gNB_Position_X})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_gNB_Position_Y":Connected_Primary_gNB_Position_Y})

    Secondary_Cell=Obtain_gNB_Information(request_data["Connected_Secondary_Cell_Name"])
    Connected_Secondary_gNB_Position_X=Secondary_Cell["gNB_Position_X"]
    Connected_Secondary_gNB_Position_Y=Secondary_Cell["gNB_Position_Y"]

    Update_UEs_Configurations(UE_Name,{"Connected_Secondary_gNB_Position_X":Connected_Secondary_gNB_Position_X})
    Update_UEs_Configurations(UE_Name,{"Connected_Secondary_gNB_Position_Y":Connected_Secondary_gNB_Position_Y})
    UE_OUT_OF_RANGE(UE_Name,UE_Position_X,UE_Position_Y)
    return jsonify({"msg":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)

