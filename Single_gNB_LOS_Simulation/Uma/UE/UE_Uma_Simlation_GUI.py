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

#Setting Log 
logname='./log/UE_Uma_Simlation_GUI.log'
logging.basicConfig(filename=logname,filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.DEBUG)

"""
Functions Related to Parameters:
1.Current Time
2.UE_Configuration
3.Timer_Configuration
4.System_Field_Configuration
"""

#Return Now Time in String Format [0.631s]
def getCurrentTime():
    return str(datetime.datetime.now())

#Return UE_Cofiguration [0.562s] for key [0.595s]
def Obtain_UE_Configuration():
    UE_Config={}
    with open('./configuration/UE_Configuration.json', 'r') as UE_Config_file:
        UE_Config = json.load(UE_Config_file)
        UE_Config_file.close()
    return UE_Config

#Update UE_Cofiguration [0.570s]
def Update_UE_Configuration(data):
    UE_Config=Obtain_UE_Configuration()
    UE_Config.update(data)
    with open('./configuration/UE_Configuration.json', 'w') as UEConfig_file:
        json.dump(UE_Config, UEConfig_file, ensure_ascii=False)
        UEConfig_file.close()

#Return Timer_Configuration for key [0.595s]
def Obtain_Timer_Configuration(key):
    Timer_Config={}
    with open('./configuration/Timer_Configuration.json', 'r') as Timer_Config_file:
        Timer_Config = json.load(Timer_Config_file)
        Timer_Config_file.close()
    return Timer_Config[key]

#Update Timer_Configuration for key 
def Update_Timer_Configuration(data):
    Timer_Config={}
    with open('./configuration/Timer_Configuration.json', 'r') as Timer_Config_file:
        Timer_Config = json.load(Timer_Config_file)
        Timer_Config_file.close()
    Timer_Config.update(data)
    with open('./configuration/Timer_Configuration.json', 'w') as Timer_Config_file:
        json.dump(Timer_Config, Timer_Config_file, ensure_ascii=False)
        Timer_Config_file.close()

#Obtain System Field Configuration
def Obtain_System_Field_Configuration(key):
    System_Field_Configuration={}
    with open('./configuration/System_Field_Configuration.json', 'r') as System_Field_Configuration_file:
        System_Field_Configuration = json.load(System_Field_Configuration_file)
        System_Field_Configuration_file.close()
    if(key==""):
        return System_Field_Configuration
    return System_Field_Configuration[key]

#Update System Field Configuration
def Update_System_Field_Configuration(data):
    System_Field_Configuration=Obtain_System_Field_Configuration("")
    System_Field_Configuration.update(data)
    with open('./configuration/System_Field_Configuration.json', 'w') as System_Field_Configuration_file:
        json.dump(System_Field_Configuration, System_Field_Configuration_file, ensure_ascii=False)
        System_Field_Configuration_file.close()


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
def Obtain_UE_Identity(G_S_TMSI):
    UE_Identity=""
    if(G_S_TMSI==""):
        ID=random.randint(0,2**39)
        UE_Identity="{0:b}".format(ID)
        Update_UE_Configuration({"UE_Identity":UE_Identity})
    else:
        UE_Identity=Obtain_UE_Configuration()["ng-5G-S-TMSI-Part1"]
    return UE_Identity

# Reception of the RRCSetup by the UE for RRCSetupRequest
def Reception_RRCSetup_UE():
    logging.info(Obtain_UE_Configuration()["UE_Name"]+" recieve RRCSetup.")
    Update_UE_Configuration({"UE_Inactive_AS_Context":{}})
    Update_UE_Configuration({"SuspendConfig":{}})
    Update_UE_Configuration({"AS_Security_Context":{}})
    Update_Timer_Configuration({"T380":"STOP"})
    Perform_Cell_Group_Configuration()
    Perform_Radio_Bearer_Configuration()
    Update_Timer_Configuration({"T300":"STOP"})
    Update_Timer_Configuration({"T301":"STOP"})
    Update_Timer_Configuration({"T319":"STOP"})
    Update_Timer_Configuration({"T390":"STOP"})
    Update_Timer_Configuration({"T302":"STOP"})
    Update_Timer_Configuration({"T320":"STOP"})
    Update_Timer_Configuration({"T331":"STOP"})
    Update_UE_Configuration({"RRC":"RRC_CONNECTED"})
    Update_UE_Configuration({"Connected_Primary_Cell_Name":"gNB_A"})
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
def Reception_RRCReject_UE():
    logging.info(Obtain_UE_Configuration()["UE_Name"]+" recieve RRCReject.")
    Update_Timer_Configuration({"T300":"STOP"})
    Update_Timer_Configuration({"T319":"STOP"})
    Update_Timer_Configuration({"T302":"STOP"})
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
    Update_UE_Configuration({"MAC_Cell_Group_Configuration":MAC_Cell_Group_Configuration})

"""
Functions of UE Access to Core Network
0.RRCInitialization
1.RRCSetupRequest
"""

#Check before RRCSetupRequest
def RRCInitialization():
    logging.info(Obtain_UE_Configuration()["UE_Name"]+" perform RRCInitialization to RRCSetupRequest.")
    PCell_IP=Obtain_UE_Configuration()["Connected_Primary_Cell_IP"]
    if(PCell_IP==""):
        logging.warning('PCell Not Settng')
        Connected_Primary_Cell_IP=input()
        Update_UE_Configuration({"Connected_Primary_Cell_IP":Connected_Primary_Cell_IP})
    else:
        logging.info("PCell has existed.")
    
    if(Obtain_Timer_Configuration('T390')=='RUNNING'):
        logging.warning("Access attempt is barred")
        return  -1
    
    if(Obtain_Timer_Configuration('T302')=='RUNNING'):
        if(Obtain_UE_Configuration()["Access_Category"]==2):
            logging("Too Complex QAQ")
        elif(Obtain_UE_Configuration()["Access_Category"]!=0):
            logging.warning("Access attempt is barred")
    
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
    Update_UE_Configuration({"MAC_Cell_Group_Configuration":MAC_Cell_Group_Configuration})
    Update_Timer_Configuration({"sf10":"OCCUPIED"})
    Update_Timer_Configuration({"sf80":"OCCUPIED"})

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
    Update_UE_Configuration({"CCCH_Configuration":CCCH_Configuration})
    Update_Timer_Configuration({"T300":"RUNNING"})
    return 0

#Step(1) When RRC_IDLE send request to primary gNB
def RRCSetupRequest():
    logging.info(Obtain_UE_Configuration()["UE_Name"]+" send RRCSetupRequest to "+Obtain_UE_Configuration()["Connected_Primary_Cell_IP"])
    url = "http://"+Obtain_UE_Configuration()["Connected_Primary_Cell_IP"]+":1440/RRCSetupRequest"
    G_S_TMSI=Obtain_UE_Configuration()["5G-S-TMSI"]
    payload={
        "UE_Name":Obtain_UE_Configuration()["UE_Name"],
        "UE_IP":Obtain_UE_Configuration()["UE_IP"],
        "5G-S-TMSI":G_S_TMSI,
        "UE_Identity":Obtain_UE_Identity(G_S_TMSI),
        "establishmentCause":"mo-Signalling"
    }
    payload=json.dumps(payload)
    
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code==200):
        response_data=json.loads(response.text)
        if(response_data['RRC']=="RRCSetUp"):
            Reception_RRCSetup_UE()
        else:
            Reception_RRCReject_UE()
            Update_UE_Configuration({"RRC":"RRC_IDLE"})
    else:
        print("HTTP STATUS: "+str(response.status_code))
        logging.warn("HTTP STATUS: "+str(response.status_code))

"""
Functions of RSRP Request and Response
1.gNB_Information_Request
"""

#gNB_Information_Request to calculate RSRP
def gNB_Information_Request():
    url = "http://"+Obtain_UE_Configuration()["Connected_Primary_Cell_IP"]+":1440/gNB_Information_Request"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    response_data=json.loads(response.text)
    Update_System_Field_Configuration({response_data["gNB_Name"]:response_data})

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
def Calculate_Distance_2D():
    Delta_X=Obtain_System_Field_Configuration("gNB_A")["gNB_Position_X"]-Obtain_System_Field_Configuration("UE_Position_X")
    Delta_Y=Obtain_System_Field_Configuration("gNB_A")["gNB_Position_Y"]-Obtain_System_Field_Configuration("UE_Position_Y")
    Distance_2D=math.sqrt((Delta_X*Delta_X)+(Delta_Y*Delta_Y))
    Update_System_Field_Configuration({"Distance_2D":Distance_2D})

def Calculate_Distance_Break_Point():
    Distance_Break_Point=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]*Obtain_System_Field_Configuration("User_Terminal_Height")
    Distance_Break_Point=Distance_Break_Point*2*math.pi*Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]*1000000
    Distance_Break_Point=Distance_Break_Point/(3*100000000)
    Update_System_Field_Configuration({"Distance_Break_Point":Distance_Break_Point})

def Calculate_Distance_3D():
    Distance_2D=Obtain_System_Field_Configuration("Distance_2D")
    Delta_H=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]-Obtain_System_Field_Configuration("User_Terminal_Height")
    Distance_3D=math.sqrt((Distance_2D*Distance_2D)+(Delta_H*Delta_H))
    Update_System_Field_Configuration({"Distance_3D":Distance_3D})

def PathLoss_1():
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(Obtain_System_Field_Configuration("Distance_3D"))
    PathLoss=PathLoss+20.0*np.log10(Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]/1000)
    Update_System_Field_Configuration({"PathLoss":PathLoss})

def PathLoss_2():
    PathLoss=28.0
    PathLoss=PathLoss+22.0*np.log10(Obtain_System_Field_Configuration("Distance_3D"))
    PathLoss=PathLoss+20.0*np.log10(Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]/1000)
    Delta_H=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]-Obtain_System_Field_Configuration("User_Terminal_Height")
    PathLoss=PathLoss-9*np.log10((Delta_H*Delta_H)+(Obtain_System_Field_Configuration("Distance_Break_Point")*Obtain_System_Field_Configuration("Distance_Break_Point")))
    Update_System_Field_Configuration({"PathLoss":PathLoss})

def Calculate_RSRP():
    gNB_Antenna_Power=Obtain_System_Field_Configuration('gNB_A')['gNB_Antenna_Power']
    PathLoss=Obtain_System_Field_Configuration('PathLoss')
    RSRP=gNB_Antenna_Power-PathLoss
    Update_System_Field_Configuration({"RSRP":RSRP})

def Initial_Calculation():
    Calculate_Distance_2D()
    Calculate_Distance_Break_Point()
    Calculate_Distance_3D()
    if(Obtain_System_Field_Configuration("Distance_2D")<Obtain_System_Field_Configuration("Distance_Break_Point")):
        Update_System_Field_Configuration({"PathLoss_Model":1})
        PathLoss_1()
    else:
        Update_System_Field_Configuration({"PathLoss_Model":2})
        PathLoss_2()
    Calculate_RSRP()

"""
Plot Initailzation
1.on_press
2.MotionEvent
3.RSRP_Response
"""
figure=plt.figure(figsize=(8,8))
def on_press(event):
    #print('press', event.key)
    sys.stdout.flush()

    if event.key == 'up':
        MotionEvent(0,1)
    if event.key == 'down':
        MotionEvent(0,-1)
    if event.key == 'right':
        MotionEvent(1,0)
    if event.key == 'left':
        MotionEvent(-1,0)

def MotionEvent(x,y):
    Update_System_Field_Configuration({"UE_Position_X":Obtain_System_Field_Configuration("UE_Position_X")+(x*Obtain_System_Field_Configuration("Motion_Speed"))})
    Update_System_Field_Configuration({"UE_Position_Y":Obtain_System_Field_Configuration("UE_Position_Y")+(y*Obtain_System_Field_Configuration("Motion_Speed"))})
    Calculate_Distance_2D()
    Calculate_Distance_3D()
    if(Obtain_System_Field_Configuration("PathLoss_Model")==1):
        PathLoss_1()
    else:
        PathLoss_2()
    Calculate_RSRP()
    RSRP_Response()

def RSRP_Response():
    url = "http://"+Obtain_UE_Configuration()["Connected_Primary_Cell_IP"]+":1440/RecieveRSRPResponse"
    payload={
        "UE_Name":Obtain_UE_Configuration()["UE_Name"],
        "UE_IP":Obtain_UE_Configuration()["UE_IP"],
        "RSRP":Obtain_System_Field_Configuration('RSRP')
    }
    payload=json.dumps(payload)
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)

#For TESTING
def CLEAN_UP():
    Update_UE_Configuration({"RRC":"RRC_IDLE"})

#Main
CLEAN_UP()
while(True):#[0.684s]
    if(Obtain_UE_Configuration()["RRC"]=="RRC_IDLE"):
        if(RRCInitialization()==0):
            RRCSetupRequest()
            continue
    if(Obtain_UE_Configuration()["RRC"]=="RRC_CONNECTED"):
        break

gNB_Information_Request()
Initial_Calculation()

#Animation
def animate(i):
    UE_Position_X=Obtain_System_Field_Configuration("UE_Position_X")
    UE_Position_Y=Obtain_System_Field_Configuration("UE_Position_Y")

    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of '+Obtain_System_Field_Configuration('UE_Name')+' Realtive Position with '+Obtain_System_Field_Configuration('gNB_A')["gNB_Name"]+'\n')
    figure.add_axes(axes)
    figure.canvas.mpl_connect('key_press_event', on_press)
    axes.axis[:].set_visible(False)

    axes.axis["x"]=axes.new_floating_axis(0,0,axis_direction="bottom")
    axes.axis["y"]=axes.new_floating_axis(1,0,axis_direction="bottom")

    axes.axis["x"].set_axisline_style("->",size=1.0)
    axes.axis["y"].set_axisline_style("->",size=1.0)

    plt.xlim((-1)*Obtain_System_Field_Configuration("X_RANGE"),Obtain_System_Field_Configuration("X_RANGE"))
    plt.ylim((-1)*Obtain_System_Field_Configuration("Y_RANGE"),Obtain_System_Field_Configuration("Y_RANGE")) 

    axes.add_patch(
        patches.Rectangle(
            ((-1)*Obtain_System_Field_Configuration("X_RANGE"), (-1)*Obtain_System_Field_Configuration("Y_RANGE")),
            Obtain_System_Field_Configuration("X_RANGE")*2,
            Obtain_System_Field_Configuration("X_RANGE")*2,    
            color="white",
            edgecolor="white"
        )
    )
    gNB_Center_Point= plt.Circle((Obtain_System_Field_Configuration('gNB_A')["gNB_Position_X"],Obtain_System_Field_Configuration('gNB_A')["gNB_Position_Y"]), 10,color=Obtain_System_Field_Configuration('gNB_A')["gNB_Center_Color"])
    axes.add_artist(gNB_Center_Point)

    gNB_Range_Point= plt.Circle((Obtain_System_Field_Configuration('gNB_A')["gNB_Position_X"],Obtain_System_Field_Configuration('gNB_A')["gNB_Position_Y"]), Obtain_System_Field_Configuration('gNB_A')["gNB_Limit_Range"],color=Obtain_System_Field_Configuration('gNB_A')["gNB_Range_Color"],fill=False)
    axes.add_artist(gNB_Range_Point)

    plt.text(Obtain_System_Field_Configuration('gNB_A')["gNB_Position_X"]-100, Obtain_System_Field_Configuration('gNB_A')["gNB_Position_Y"]+20, Obtain_System_Field_Configuration('gNB_A')["gNB_Name"], fontsize=10, color=Obtain_System_Field_Configuration('gNB_A')["gNB_Center_Color"])
    UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 5,color=Obtain_System_Field_Configuration("UE_Color"))
    axes.add_artist(UE_Point)
    plt.text(Obtain_System_Field_Configuration("X_RANGE")-600, 0-Obtain_System_Field_Configuration("Y_RANGE")+90, "Distance: "+format(Obtain_System_Field_Configuration('Distance_2D'), '.11f'), fontsize=10, color=Obtain_System_Field_Configuration('UE_Color'))
    plt.text(Obtain_System_Field_Configuration("X_RANGE")-600, 0-Obtain_System_Field_Configuration("Y_RANGE")+50, "PathLoss: "+format(Obtain_System_Field_Configuration('PathLoss'), '.12f'), fontsize=10, color=Obtain_System_Field_Configuration('UE_Color'))
    plt.text(Obtain_System_Field_Configuration("X_RANGE")-600, 0-Obtain_System_Field_Configuration("Y_RANGE")+10, "RSRP: "+str(Obtain_System_Field_Configuration('RSRP')), fontsize=10, color=Obtain_System_Field_Configuration('UE_Color'))

anim = animation.FuncAnimation(figure, animate, interval=1500) 
plt.show()