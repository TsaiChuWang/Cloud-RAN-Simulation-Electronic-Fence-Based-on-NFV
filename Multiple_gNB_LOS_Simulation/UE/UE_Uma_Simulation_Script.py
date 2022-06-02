#import library
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
import math
import matplotlib.animation as animation
import mpl_toolkits.axisartist as axisartist 
import matplotlib.patches as patches
import datetime
import logging

import requests
import time
from flask import jsonify
import random

logname='./log/UE_Uma_Simulation_Script.log'
logging.basicConfig(filename=logname,filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)
Connected_Primary_Cell_IP="10.0.2.100"

"""
Functions of parameters in Configurations
1.UEs_Configurations(Obtain/Update/INITIALIZE)
2.
"""
def Obtain_UEs_Configurations(UE_Name):
    UEs_Configurations={}
    with open('./configuration/UEs_Configurations.json') as UEs_Configurations_file:
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
    with open('./configuration/UEs_Configurations.json', 'w') as UEs_Configurations_file:
        json.dump(UEs_Configurations, UEs_Configurations_file, ensure_ascii=False)
        UEs_Configurations_file.close()

#Initialization of Configuration
def INITIALIZE_CONFIGURATION():
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for UE_Name in UEs_List:
        UE_Position_X=random.randint(-400,400)
        UE_Position_Y=random.randint(-400,400)
        # gNB=Find_Primary_Cell(UE_Position_X,UE_Position_Y)
        data={
            "UE_Name": UE_Name,
            "UE_IP": "10.0.2.121",
            "Connected_Primary_Cell_Name":"gNB_A",
            "Connected_Primary_Cell_IP":"10.0.2.100",
            "Connected_Primary_Cell_Position_X":0,
            "Connected_Primary_Cell_Position_Y":0,
            "Connected_Primary_Cell_gNB_Antenna_Power":0,
            "Connected_Primary_Cell_gNB_Center_Frequency":0,
            "5G-S-TMSI": "",
            "Access_Category": 0,
            "RRC":"RRC_IDLE",
            "UE_Identity": "11101001001100001011000010001000011000",
            "ng-5G-S-TMSI-Part1": "",
            "ng-5G-S-TMSI-Part2": "",
            "ng-5G-S-TMSI-Value": "",
            "UE_Color": str("#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])),
            "Motion_Speed": random.randint(8,22),
            "UE_Position_X": UE_Position_X,
            "UE_Position_Y": UE_Position_Y,
            "User_Terminal_Height": 1.7,
            "Distance_Break_Point": 0,
            "Distance_2D": 0,
            "Distance_3D": 0,
            "PathLoss": 0,
            "PathLoss_Model": 1,
            "RSRP": 0,
            "Connected_Primary_Cell_Position_X":0,
            "Connected_Primary_Cell_Position_Y":0,
            "Connected_Secondary_Cell_Position_X":0,
            "Connected_Secondary_Cell_Position_Y":0,
            "MAC_Cell_Group_Configuration":{
                "bsr_Config":{
                    "periodicBSR_Timer":"sf10",
                    "retxBSR_Timer":"sf80"
                },
                "phr_Config":{
                    "phr_PeriodicTimer":"sf10",
                    "phr_ProhibitTimer ":"sf10",
                    "phr_Tx_PowerFactorChange":"dB1"
                }
            },
            "CCCH_Configuration":{
                "SDAP_Configuration":"NOT_USED",
                "PDCP_Configuration":"NOT_USED",
                "RLC_Configuration":"TM",
                "Logical_Channel_Configuration":{
                    "Priority":1,#Highest priority
                    "PrioritisedBitRate":"INFINITY",
                    "BucketSizeDuration_ms":1000,
                    "LogicalChannelGroup":0
                }
            }

        }
        Update_UEs_Configurations(UE_Name,data)

"""
Functions of Sub Process for UE Accessing to Core Network
1.Get_UE_Identity
2.Reception of the RRCSetup by the UE 
  2.1.Perform Cell Group Configuration
  2.2.Perform_Radio_Bearer_Configuration
  2.3.Set_Content_RRCSetupComplete_Message
3.Reception of the RRCReject by the UE
"""

#Get Obtain_UE_Identity for RRCSetupRequest
def Obtain_UE_Identity(UE_Name,G_S_TMSI):
    UE_Identity=""
    if(G_S_TMSI==""):
        ID=random.randint(0,2**39)
        UE_Identity="{0:b}".format(ID)
        Update_UEs_Configurations(UE_Name,{"UE_Identity":UE_Identity})
    else:
        UE_Identity=Obtain_UEs_Configurations(UE_Name)["ng-5G-S-TMSI-Part1"]
    return UE_Identity

# Reception of the RRCSetup by the UE for RRCSetupRequest
def Reception_RRCSetup_UE(UE_Name):
    logging.info(UE_Name+" recieve RRCSetup.")
    Update_UEs_Configurations(UE_Name,{"UE_Inactive_AS_Context":{}})
    Update_UEs_Configurations(UE_Name,{"SuspendConfig":{}})
    Update_UEs_Configurations(UE_Name,{"AS_Security_Context":{}})
    Perform_Cell_Group_Configuration()
    Perform_Radio_Bearer_Configuration()
    Update_UEs_Configurations(UE_Name,{"RRC":"RRC_CONNECTED"})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Name":"gNB_A"})
    Set_Content_RRCSetupComplete_Message()

#Perform the cell group configuration procedure in accordance with the received masterCellGroup
def Perform_Cell_Group_Configuration():
    logging.info("Cell_Group_Configuration waiting update")
    return -1

#Perform the radio bearer configuration procedure in accordance with the received radioBearerConfig
def Perform_Radio_Bearer_Configuration():
    logging.info("Cell_Group_Configuration waiting update")
    return -1

#Set the content of RRCSetupComplete message
def Set_Content_RRCSetupComplete_Message():
    logging.info("Set_Content_RRCSetupComplete_Message waiting update")
    return -1

#Reception of the RRCReject by the UE
def Reception_RRCReject_UE(UE_Name):
    logging.info(UE_Name+" recieve RRCReject.")
    MAC_Cell_Group_Configuration={
        "bsr_Config":{
            "periodicBSR_Timer":"sf10",
            "retxBSR_Timer":"sf80"
        },
        "phr_Config":{
            "phr_PeriodicTimer":"sf10",
            "phr_ProhibitTimer ":"sf10",
            "phr_Tx_PowerFactorChange":"dB1"
        }
    }
    Update_UEs_Configurations(UE_Name,{"MAC_Cell_Group_Configuration":MAC_Cell_Group_Configuration})

"""
Functions of UE Access to Core Network
1.RRCSetupRequest
"""

#Step(1) When RRC_IDLE send request to primary gNB
def RRCSetupRequest(UE_Name):
    logging.info(UE_Name+" send RRCSetupRequest to "+Obtain_UEs_Configurations(UE_Name)["Connected_Primary_Cell_IP"])
    url = "http://"+Obtain_UEs_Configurations(UE_Name)["Connected_Primary_Cell_IP"]+":1441/RRCSetupRequest"
    G_S_TMSI=Obtain_UEs_Configurations(UE_Name)["5G-S-TMSI"]
    payload={
        "UE_Name":Obtain_UEs_Configurations(UE_Name)["UE_Name"],
        "UE_IP":Obtain_UEs_Configurations(UE_Name)["UE_IP"],
        "5G-S-TMSI":G_S_TMSI,
        "UE_Identity":Obtain_UE_Identity(UE_Name,G_S_TMSI),
        "establishmentCause":"mo-Signalling",
        "UE_Position_X":Obtain_UEs_Configurations(UE_Name)["UE_Position_X"],
        "UE_Position_Y":Obtain_UEs_Configurations(UE_Name)["UE_Position_Y"],
        "UE_Information":Obtain_UEs_Configurations(UE_Name)
    }
    payload=json.dumps(payload)
    
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code==200):
        response_data=json.loads(response.text)
        if(response_data['RRC']=="RRCSetUp"):
            Reception_RRCSetup_UE(UE_Name)
        else:
            Reception_RRCReject_UE(UE_Name)
            Update_UEs_Configurations(UE_Name,{"RRC":"RRC_IDLE"})
    else:
        print("HTTP STATUS: "+str(response.status_code))
        logging.warn("HTTP STATUS: "+str(response.status_code))


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

#Require the Information of gNBs
def Require_Information_gNBs():
    url = "http://"+Connected_Primary_Cell_IP+":1441/gNB_Information_Request"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_data=json.loads(response.text)
    print(response_data)
    Update_Information_gNBs(response_data)

#CLEAN UP IN CONFIGURATION
def CLEAN_UP():
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for UE_Name in UEs_List:
        Update_UEs_Configurations(UE_Name,{"RRC": "RRC_IDLE"})

CLEAN_UP()
# INITIALIZE_CONFIGURATION()
UEs_List=Obtain_UEs_Configurations("UEs_List")
for UE_Name in UEs_List:
    while(True):
        if(Obtain_UEs_Configurations(UE_Name)["RRC"]=="RRC_IDLE"):
            RRCSetupRequest(UE_Name)
            continue
        elif(Obtain_UEs_Configurations(UE_Name)["RRC"]=="RRC_CONNECTED"):
            break;