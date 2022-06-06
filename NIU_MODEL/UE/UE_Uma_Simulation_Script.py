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
2.gNB_Information
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

def Update_UEs_Configurations_WHOLE(UE_Name,data):
    UEs_Configurations=Obtain_UEs_Configurations("")
    UEs_Configurations.update({UE_Name:data})
    with open('./configuration/UEs_Configurations.json', 'w') as UEs_Configurations_file:
        json.dump(UEs_Configurations, UEs_Configurations_file, ensure_ascii=False)
        UEs_Configurations_file.close()

#Initialization of Configuration
def INITIALIZE_CONFIGURATION():
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for UE_Name in UEs_List:
        UE_Position_X=random.randint(-2800,2000)
        UE_Position_Y=random.randint(-1200,1200)
        # gNB=Find_Primary_Cell(UE_Position_X,UE_Position_Y)
        Script_Line_Origin_Array=[0,0,0,0,1,-1]
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
            },
            "Script_Line":[random.choice(Script_Line_Origin_Array) for i in range(180)],
            "Script_Direct":[random.choice([0,1]) for i in range(180)]
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
    # Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Name":"gNB_A"})
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
            Update_UEs_Configurations_WHOLE(UE_Name,response_data["UE_Information"])
            Reception_RRCSetup_UE(UE_Name)
        else:
            Reception_RRCReject_UE(UE_Name)
            Update_UEs_Configurations(UE_Name,{"RRC":"RRC_IDLE"})
    else:
        print("HTTP STATUS: "+str(response.status_code))
        logging.warn("HTTP STATUS: "+str(response.status_code))


#CLEAN UP IN CONFIGURATION
def CLEAN_UP():
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for UE_Name in UEs_List:
        Update_UEs_Configurations(UE_Name,{"RRC": "RRC_IDLE"})

"""
Functions of RSRP Detection
1.Require gNB Informations
2.Update gNB-UEs Pairs
3.RSRPTRANSFERgNB
4.Movement
"""

#Require the Information of gNBs
def Require_Information_gNBs():
    url = "http://"+Connected_Primary_Cell_IP+":1441/gNB_Information_Request"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_data=json.loads(response.text)
    Update_Information_gNBs(response_data)

#Update gNB-UEs Pairs
def Update_gNB_UEs_Pairs(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)

    Connected_Primary_Cell_Name=UE["Connected_Primary_Cell_Name"]
    Primary_Cell=Obtain_gNB_Information(Connected_Primary_Cell_Name)
    Connected_Primary_Cell_Position_X=Primary_Cell["gNB_Position_X"]
    Connected_Primary_Cell_Position_Y=Primary_Cell["gNB_Position_Y"]
    Connected_Primary_Cell_gNB_Antenna_Power=Primary_Cell["gNB_Antenna_Power"]
    Connected_Primary_Cell_gNB_Center_Frequency=Primary_Cell["gNB_Center_Frequency"]
    Connected_Secondary_Cell_Name=UE["Connected_Secondary_Cell_Name"]
    Secondary_Cell=Obtain_gNB_Information(Connected_Secondary_Cell_Name)
    Connected_Secondary_Cell_Position_X=Secondary_Cell["gNB_Position_X"]
    Connected_Secondary_Cell_Position_Y=Secondary_Cell["gNB_Position_Y"]
    
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Position_X":Connected_Primary_Cell_Position_X})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Position_Y":Connected_Primary_Cell_Position_Y})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_gNB_Antenna_Power":Connected_Primary_Cell_gNB_Antenna_Power})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_gNB_Center_Frequency":Connected_Primary_Cell_gNB_Center_Frequency})
    Update_UEs_Configurations(UE_Name,{"Connected_Secondary_Cell_Position_X":Connected_Secondary_Cell_Position_X})
    Update_UEs_Configurations(UE_Name,{"Connected_Secondary_Cell_Position_Y":Connected_Secondary_Cell_Position_Y})
    Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_gNB_BS_Height":Primary_Cell["gNB_BS_Height"]})

def RSRPTRANSFERgNB(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    url = "http://"+UE["Connected_Primary_Cell_IP"]+":1441/RecieveRSRP"
    MCG=UE["MCG"]
    SCG=UE["SCG"]
    Connected_Primary_Cell_Name= UE["Connected_Primary_Cell_Name"]
    Connected_Secondary_Cell_Name=UE["Connected_Secondary_Cell_Name"]
    payload={
        "UE_Name": UE_Name,
        "RSRP": UE["RSRP"],
        "MCG": MCG,
        "SCG": SCG,
        "Connected_Primary_Cell_Name": Connected_Primary_Cell_Name,
        "Connected_Secondary_Cell_Name": Connected_Secondary_Cell_Name,
        "UE_Position_X":UE["UE_Position_X"],
        "UE_Position_Y":UE["UE_Position_Y"]
    }
    payload=json.dumps(payload)
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_data=json.loads(response.text)
    if(not(response_data["MCG"]==MCG)):
        Update_UEs_Configurations(UE_Name,{"MCG":response_data["MCG"]})
    
    if(not(response_data["SCG"]==MCG)):
        Update_UEs_Configurations(UE_Name,{"SCG":response_data["SCG"]})
    
    if(not(response_data["Connected_Primary_Cell_Name"]==Connected_Primary_Cell_Name)):
        Update_UEs_Configurations(UE_Name,{"Connected_Primary_Cell_Name":response_data["Connected_Primary_Cell_Name"]})
    
    if(not(response_data["Connected_Secondary_Cell_Name"]==Connected_Secondary_Cell_Name)):
        Update_UEs_Configurations(UE_Name,{"Connected_Secondary_Cell_Name":response_data["Connected_Secondary_Cell_Name"]})
        
"""
Functions of Calculation
1.Distance 2D
2.Break_Point
3.Distance 3D
4.PathLoss
4.1.PathLoss1
4.2.PathLoss2
5.RSRP
"""
def Calculate_Distance_2D(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    Delta_X=UE["Connected_Primary_Cell_Position_X"]-UE["UE_Position_X"]
    Delta_Y=UE["Connected_Primary_Cell_Position_Y"]-UE["UE_Position_Y"]
    Distance_2D=math.sqrt((Delta_X*Delta_X)+(Delta_Y*Delta_Y))
    Update_UEs_Configurations(UE_Name,{"Distance_2D":Distance_2D})

def Calculate_Distance_Break_Point(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    Distance_Break_Point=UE["Connected_Primary_Cell_gNB_BS_Height"]*UE["User_Terminal_Height"]
    Distance_Break_Point=Distance_Break_Point*2*math.pi*UE["gNB_Center_Frequency"]*1000000
    Distance_Break_Point=Distance_Break_Point/(3*100000000)
    Update_UEs_Configurations(UE_Name,{"Distance_Break_Point":Distance_Break_Point})

def Calculate_Distance_3D(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    Distance_2D=UE["Distance_2D"]
    Delta_H=UE["Connected_Primary_Cell_gNB_BS_Height"]-UE["User_Terminal_Height"]
    Distance_3D=math.sqrt((Distance_2D*Distance_2D)+(Delta_H*Delta_H))
    Update_UEs_Configurations(UE_Name,{"Distance_3D":Distance_3D})

def PathLoss_1(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(UE["Distance_3D"])
    PathLoss=PathLoss+20.0*np.log10(UE["Connected_Primary_Cell_gNB_Center_Frequency"]/1000)
    Update_UEs_Configurations(UE_Name,{"PathLoss":PathLoss})
    

def PathLoss_2(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(UE["Distance_3D"])
    PathLoss=PathLoss+20.0*np.log10(UE["Connected_Primary_Cell_gNB_Center_Frequency"]/1000)
    Delta_H=UE["Connected_Primary_Cell_gNB_BS_Height"]-UE["User_Terminal_Height"]
    PathLoss=PathLoss-9*np.log10((Delta_H*Delta_H)+(UE["Distance_Break_Point"]*UE["Distance_Break_Point"]))
    Update_UEs_Configurations(UE_Name,{"PathLoss":PathLoss})

def Calculate_RSRP(UE_Name):
    UE=Obtain_UEs_Configurations(UE_Name)
    gNB_Antenna_Power=UE['Connected_Primary_Cell_gNB_Antenna_Power']
    # print("gNB_Antenna_Power="+str(gNB_Antenna_Power))
    PathLoss=UE['PathLoss']
    # print("PathLoss="+str(PathLoss))
    RSRP=gNB_Antenna_Power-PathLoss
    # print("RSRP="+str(RSRP))
    # print("==========")
    Update_UEs_Configurations(UE_Name,{"RSRP":RSRP})


# INITIALIZE_CONFIGURATION()
CLEAN_UP()
UEs_List=Obtain_UEs_Configurations("UEs_List")
for UE_Name in UEs_List:
    while(True):
        if(Obtain_UEs_Configurations(UE_Name)["RRC"]=="RRC_IDLE"):
            RRCSetupRequest(UE_Name)
            continue
        elif(Obtain_UEs_Configurations(UE_Name)["RRC"]=="RRC_CONNECTED"):
            break;

Require_Information_gNBs()
for UE_Name in UEs_List:
    Update_gNB_UEs_Pairs(UE_Name)

for UE_Name in UEs_List:
    Update_UEs_Configurations(UE_Name,{"Script_Line":[random.choice([0,1,1,-1,-1]) for i in range(180)]})
index=0
while(index<180):
    for UE_Name in UEs_List:
        UE=Obtain_UEs_Configurations(UE_Name)
        if(UE["Script_Line"][index]!=0):
            UE_Position_X=UE["UE_Position_X"]
            UE_Position_Y=UE["UE_Position_Y"]
            if(UE["Script_Direct"][index]==0):
                UE_Position_X=UE_Position_X+(UE["Script_Line"][index]*UE["Motion_Speed"])
                Update_UEs_Configurations(UE_Name,{"UE_Position_X":UE_Position_X})
            else:
                UE_Position_Y=UE_Position_Y+(UE["Script_Line"][index]*UE["Motion_Speed"])
                Update_UEs_Configurations(UE_Name,{"UE_Position_Y":UE_Position_Y})

            Update_gNB_UEs_Pairs(UE_Name)
            Calculate_Distance_2D(UE_Name)
            Calculate_Distance_3D(UE_Name)
            PathLoss_1(UE_Name)
            Calculate_RSRP(UE_Name)
            
            RSRPTRANSFERgNB(UE_Name)
    index=index+1
    time.sleep(1.5)