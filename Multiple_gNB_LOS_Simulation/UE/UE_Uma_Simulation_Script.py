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

def Find_Primary_Cell(UE_Position_X,UE_Position_Y):
    gNBs_List=Obtain_gNB_Information("gNBs_List")
    data={
        "Distance":4000,
        "Connected_Primary_Cell_Name":"",
        "Connected_Primary_Cell_IP": "",
        "Connected_Primary_Cell_Position_X":0,
        "Connected_Primary_Cell_Position_Y":0,
        "Connected_Primary_Cell_gNB_Antenna_Power":0,
        "Connected_Primary_Cell_gNB_Center_Frequency":0,
    }
    
    for gNB_Name in gNBs_List:
        gNB=Obtain_gNB_Information(gNB_Name)
        gNB_Position_X=gNB["gNB_Position_X"]
        gNB_Position_Y=gNB["gNB_Position_Y"]
        Delta_X=gNB_Position_X-UE_Position_X
        Delta_Y=gNB_Position_Y-UE_Position_Y
        Distance=(Delta_X*Delta_X)+(Delta_Y*Delta_Y)
        Distance=math.sqrt(Distance)
        if(Distance<data['Distance']):
            data['Distance']=Distance
            data['Connected_Primary_Cell_Name']=gNB['Connected_Primary_Cell_Name']
            data['Connected_Primary_Cell_IP']=gNB['Connected_Primary_Cell_IP']
            data['Connected_Primary_Cell_Position_X']=gNB_Position_X
            data['Connected_Primary_Cell_Position_Y']=gNB_Position_Y
            data['Connected_Primary_Cell_gNB_Antenna_Power']=gNB['Connected_Primary_Cell_gNB_Antenna_Power']
            data['Connected_Primary_Cell_gNB_Center_Frequency']=gNB['Connected_Primary_Cell_gNB_Center_Frequency']
    return data

#Require the Information of gNBs
def Require_Information_gNBs():
    url = "http://"+Connected_Primary_Cell_IP+":1441/gNB_Information_Request"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_data=json.loads(response.text)
    print(response_data)
    Update_Information_gNBs(response_data)

# Update_System_Field_Configuration({response_data["gNB_Name"]:response_data})




# Require_Information_gNBs()

INITIALIZE_CONFIGURATION()