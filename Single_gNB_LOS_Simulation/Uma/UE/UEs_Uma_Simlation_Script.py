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
    print(response.text)
    if(response.status_code==200):
        response_data=json.loads(response.text)
        if(response_data['RRC']=="RRCSetUp"):
            Reception_RRCSetup_UE()
    #     else:
    #         Reception_RRCReject_UE()
    #         Update_UE_Configuration({"RRC":"RRC_IDLE"})
    # else:
    #     print("HTTP STATUS: "+str(response.status_code))
    #     logging.warn("HTTP STATUS: "+str(response.status_code))
CLEAN_UP()
UEs_List=Obtain_Specified_UE_Config("UEs_List")
for UE_Name in UEs_List:
    while(True):
        if(Obtain_Specified_UE_Config(UE_Name)["RRC"]=="RRC_IDLE"):
            RRCInitialization(UE_Name)
            RRCSetupRequest(UE_Name)
            break
        if(Obtain_Specified_UE_Config(UE_Name)=="RRC_CONNECTED"):
            break
        print("UE_Name: "+UE_Name)