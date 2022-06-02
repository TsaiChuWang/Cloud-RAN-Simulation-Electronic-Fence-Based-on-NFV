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

# Obtain Cell Group Configuration
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
    UEs_Configurations.update(UEs_Configurations_UE)
    with open('./configuration/UEs_Configurations.json', 'w') as UEs_Configurations_file:
        json.dump(UEs_Configurations, UEs_Configurations_file, ensure_ascii=False)
        UEs_Configurations_file.close()

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

#Initialization of Configuration
def INITIALIZE_CONFIGURATION():
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for UE_Name in UEs_List:
        UE_Position_X=random.randint(-400,400)
        UE_Position_Y=random.randint(-400,400)
        data={
            "UE_Name": UE_Name,
            "UE_IP": "10.0.2.121",
            "Connected_Primary_Cell_Name":"",
            "Connected_Primary_Cell_IP": "",
            "Connected_Primary_Cell_Position_X":0,
            "Connected_Primary_Cell_Position_Y":0,
            "Connected_Primary_Cell_gNB_Antenna_Power":0,
            "Connected_Primary_Cell_gNB_Center_Frequency":0,
            "UE_Color": "#FF5733",
            "Motion_Speed": random.randint(8,22),
            "UE_Position_X": UE_Position_X,
            "UE_Position_Y": UE_Position_Y,
            "User_Terminal_Height": 1.7,
            "Distance_Break_Point": 3038.5020760604075,
            "Distance_2D": 438.7311249501225,
            "Distance_3D": 439.34939399070527,
            "PathLoss": 96.80606057195635,
            "PathLoss_Model": 1,
            "RSRP": -73.86486074495636,
            "Connected_Primary_Cell_Name_Position_X":0,
            "Connected_Primary_Cell_Name_Position_Y":0,
            "Connected_Secondary_Cell_Name_Position_X":0,
            "Connected_Secondary_Cell_Name_Position_Y":0
        }
    
Require_Information_gNBs()