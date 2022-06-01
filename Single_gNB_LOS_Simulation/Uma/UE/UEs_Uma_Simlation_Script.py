#import library
import sys
import numpy as np
import json
import math
import datetime
import logging

import requests
import time
from flask import jsonify
import random

#Setting Log 
logname='./log/UEs_Uma_Simlation_Script.log'
logging.basicConfig(filename=logname,filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

"""
Functions about parameters
1.UEs Objects
2.UE_Identity
3.System_Field_Configuration
"""

#Obtain Specified UE Config
def Obtain_Specified_UE_Config(UE_Name):
    UEs_Config={}
    with open('./configuration/UEs_Script_Configuration.json', 'r') as UEs_Config_file:
        UEs_Config = json.load(UEs_Config_file)
        UEs_Config_file.close()
    if(UE_Name==""):
        return UEs_Config
    return UEs_Config[UE_Name]

#Update Specified UE Config
def Update_Specified_UE_Config(UE_Name,data):
    UEs_Config=Obtain_Specified_UE_Config("")
    UE_Config=Obtain_Specified_UE_Config(UE_Name)
    UE_Config.update(data)
    UEs_Config.update({UE_Name:UE_Config})
    with open('./configuration/UEs_Script_Configuration.json', 'w') as UEsConfig_file:
        json.dump(UEs_Config, UEsConfig_file, ensure_ascii=False)
        UEsConfig_file.close()

#Get Obtain_UE_Identity for RRCSetupRequest
def Obtain_UE_Identity(UE_Name,G_S_TMSI):
    UE_Identity=""
    if(G_S_TMSI==""):
        ID=random.randint(0,2**39)
        UE_Identity="{0:b}".format(ID)
        Update_Specified_UE_Config(UE_Name,{"UE_Identity":UE_Identity})
    else:
        UE_Identity=Obtain_Specified_UE_Config(UE_Name)["ng-5G-S-TMSI-Part1"]
    return UE_Identity

#Obtain System Field Configuration
def Obtain_System_Field_Configuration(key):
    System_Field_Configuration={}
    with open('./configuration/System_Field_Configuration.json', 'r') as System_Field_Configuration_file:
        System_Field_Configuration = json.load(System_Field_Configuration_file)
        System_Field_Configuration_file.close()
    if(key==""):
        return System_Field_Configuration
    return System_Field_Configuration[key]

def CLEAN_UP():
    UEs_List=Obtain_Specified_UE_Config("UEs_List")
    for name in UEs_List:
        Update_Specified_UE_Config(name,{"RRC":"RRC_IDLE"})

"""
RRCSet Up
0.RRCInitialization
1.RRCSetupRequest
"""
#Check before RRCSetupRequest
def RRCInitialization(UE_Name):
    logging.info(UE_Name+" perform RRCInitialization to RRCSetupRequest.")
    PCell_IP=Obtain_Specified_UE_Config(UE_Name)["Connected_Primary_Cell_IP"]
    if(PCell_IP==""):
        logging.warning('PCell Not Settng')
        Connected_Primary_Cell_IP=input()
        Update_Specified_UE_Config(UE_Name,{"Connected_Primary_Cell_IP":Connected_Primary_Cell_IP})
    else:
        logging.info("PCell has existed.")
    
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
    Update_Specified_UE_Config(UE_Name,{"MAC_Cell_Group_Configuration":MAC_Cell_Group_Configuration})

    CCCH_Configuration={
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
    Update_Specified_UE_Config(UE_Name,{"CCCH_Configuration":CCCH_Configuration})
    return 0

#Step(1) When RRC_IDLE send request to primary gNB
def RRCSetupRequest(UE_Name):
    logging.info(UE_Name+" send RRCSetupRequest to "+Obtain_Specified_UE_Config(UE_Name)["Connected_Primary_Cell_IP"])
    url = "http://"+Obtain_Specified_UE_Config(UE_Name)["Connected_Primary_Cell_IP"]+":1440/RRCSetupRequest"
    G_S_TMSI=Obtain_Specified_UE_Config(UE_Name)["5G-S-TMSI"]
    payload={
        "UE_Name":Obtain_Specified_UE_Config(UE_Name)["UE_Name"],
        "UE_IP":Obtain_Specified_UE_Config(UE_Name)["UE_IP"],
        "5G-S-TMSI":G_S_TMSI,
        "UE_Identity":Obtain_UE_Identity(UE_Name,G_S_TMSI),
        "establishmentCause":"mo-Signalling"
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
            Update_Specified_UE_Config(UE_Name,{"RRC":"RRC_IDLE"})
    else:
        print("HTTP STATUS: "+str(response.status_code))
        logging.warn("HTTP STATUS: "+str(response.status_code))

# Reception of the RRCSetup by the UE for RRCSetupRequest
def Reception_RRCSetup_UE(UE_Name):
    logging.info(UE_Name+" recieve RRCSetup.")
    Update_Specified_UE_Config(UE_Name,{"UE_Inactive_AS_Context":{}})
    Update_Specified_UE_Config(UE_Name,{"SuspendConfig":{}})
    Update_Specified_UE_Config(UE_Name,{"AS_Security_Context":{}})
    Perform_Cell_Group_Configuration()
    Perform_Radio_Bearer_Configuration()
    Update_Specified_UE_Config(UE_Name,{"RRC":"RRC_CONNECTED"})
    Update_Specified_UE_Config(UE_Name,{"Connected_Primary_Cell_Name":"gNB_A"})
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
    Update_Specified_UE_Config(UE_Name,{"MAC_Cell_Group_Configuration":MAC_Cell_Group_Configuration})

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
    Delta_X=Obtain_System_Field_Configuration("gNB_A")["gNB_Position_X"]-Obtain_Specified_UE_Config(UE_Name)["UE_Position_X"]
    Delta_Y=Obtain_System_Field_Configuration("gNB_A")["gNB_Position_Y"]-Obtain_Specified_UE_Config(UE_Name)["UE_Position_Y"]
    Distance_2D=math.sqrt((Delta_X*Delta_X)+(Delta_Y*Delta_Y))
    Update_Specified_UE_Config(UE_Name,{"Distance_2D":Distance_2D})

def Calculate_Distance_Break_Point(UE_Name):
    Distance_Break_Point=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]*Obtain_Specified_UE_Config(UE_Name)["User_Terminal_Height"]
    Distance_Break_Point=Distance_Break_Point*2*math.pi*Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]*1000000
    Distance_Break_Point=Distance_Break_Point/(3*100000000)
    Update_Specified_UE_Config(UE_Name,{"Distance_Break_Point":Distance_Break_Point})

def Calculate_Distance_3D(UE_Name):
    Distance_2D=Obtain_Specified_UE_Config(UE_Name)["Distance_2D"]
    Delta_H=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]-Obtain_Specified_UE_Config(UE_Name)["User_Terminal_Height"]
    Distance_3D=math.sqrt((Distance_2D*Distance_2D)+(Delta_H*Delta_H))
    Update_Specified_UE_Config(UE_Name,{"Distance_3D":Distance_3D})

def PathLoss_1(UE_Name):
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(Obtain_Specified_UE_Config(UE_Name)["Distance_3D"])
    PathLoss=PathLoss+20.0*np.log10(Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]/1000)
    Update_Specified_UE_Config(UE_Name,{"PathLoss":PathLoss})

def PathLoss_2(UE_Name):
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(Obtain_Specified_UE_Config(UE_Name)["Distance_3D"])
    PathLoss=PathLoss+20.0*np.log10(Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]/1000)
    Delta_H=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]-Obtain_Specified_UE_Config(UE_Name)["User_Terminal_Height"]
    PathLoss=PathLoss-9*np.log10((Delta_H*Delta_H)+(Obtain_Specified_UE_Config(UE_Name)["Distance_Break_Point"]*Obtain_Specified_UE_Config(UE_Name)["Distance_Break_Point"]))
    Update_Specified_UE_Config(UE_Name,{"PathLoss":PathLoss})

def Calculate_RSRP(UE_Name):
    gNB_Antenna_Power=Obtain_System_Field_Configuration('gNB_A')['gNB_Antenna_Power']
    PathLoss=Obtain_Specified_UE_Config(UE_Name)['PathLoss']
    RSRP=gNB_Antenna_Power-PathLoss
    Update_Specified_UE_Config(UE_Name,{"RSRP":RSRP})

def RandomStart():
    UEs_List=Obtain_Specified_UE_Config("UEs_List")
    for UE_Name in UEs_List:
        UE_Position_X=random.randint(-600,600)
        UE_Position_Y=random.randint(-600,600)
        Update_Specified_UE_Config(UE_Name,{"UE_Position_X":UE_Position_X})
        Update_Specified_UE_Config(UE_Name,{"UE_Position_Y":UE_Position_Y})
        Motion_Speed=random.randint(15,35)
        Update_Specified_UE_Config(UE_Name,{"Motion_Speed":Motion_Speed})
        array=[0,0,0,0,1,-1]
        Script_Line=[random.choice(array) for i in range(180)]
        Update_Specified_UE_Config(UE_Name,{"Script_Line":Script_Line})
        direct_array=[0,1]
        Script_Direct=[random.choice(direct_array) for i in range(180)]
        Update_Specified_UE_Config(UE_Name,{"Script_Direct":Script_Direct})

def RSRP_Response(UE_Name):
    url = "http://"+Obtain_Specified_UE_Config(UE_Name)["Connected_Primary_Cell_IP"]+":1440/RecieveRSRPResponse"
    payload={
        "UE_Name":UE_Name,
        "UE_IP":Obtain_Specified_UE_Config(UE_Name)["UE_IP"],
        "RSRP":Obtain_Specified_UE_Config(UE_Name)['RSRP']
    }
    payload=json.dumps(payload)
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)

RandomStart()
CLEAN_UP()
UEs_List=Obtain_Specified_UE_Config("UEs_List")
for UE_Name in UEs_List:
    while(True):
        if(Obtain_Specified_UE_Config(UE_Name)["RRC"]=="RRC_IDLE"):
            RRCInitialization(UE_Name)
            RRCSetupRequest(UE_Name)
            continue
        if(Obtain_Specified_UE_Config(UE_Name)["RRC"]=="RRC_CONNECTED"):
            break
        print("UE_Name: "+UE_Name)

index=0
while(index<180):
    for UE_Name in UEs_List:
        if(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]==0):
            continue
        else:
            if(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]==0):
                UE_Position_X=Obtain_Specified_UE_Config(UE_Name)["UE_Position_X"]
                UE_Position_X=UE_Position_X+(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]*Obtain_Specified_UE_Config(UE_Name)["Motion_Speed"])
            else:
                UE_Position_Y=Obtain_Specified_UE_Config(UE_Name)["UE_Position_Y"]
                UE_Position_Y=UE_Position_Y+(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]*Obtain_Specified_UE_Config(UE_Name)["Motion_Speed"])
                Update_Specified_UE_Config(UE_Name,{"UE_Position_Y":UE_Position_Y})

            Calculate_Distance_2D(UE_Name)
            Calculate_Distance_Break_Point(UE_Name)
            Calculate_Distance_3D(UE_Name)
            if(Obtain_Specified_UE_Config(UE_Name)["Distance_2D"]<Obtain_Specified_UE_Config(UE_Name)["Distance_Break_Point"]):
                Update_Specified_UE_Config(UE_Name,{"PathLoss_Model":1})
                PathLoss_1(UE_Name)
            else:
                Update_Specified_UE_Config(UE_Name,{"PathLoss_Model":2})
                PathLoss_2(UE_Name)
            Calculate_RSRP(UE_Name)
            RSRP_Response(UE_Name)
            # print(UE_Name+": ("+str(Obtain_Specified_UE_Config(UE_Name)["UE_Position_X"])+", "+str(Obtain_Specified_UE_Config(UE_Name)["UE_Position_Y"])+")")
    time.sleep(2)
    index=index+1