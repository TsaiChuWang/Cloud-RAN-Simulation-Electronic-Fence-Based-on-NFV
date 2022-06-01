
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


figure=plt.figure(figsize=(8,8))
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
        Motion_Speed=random.randint(2,10)
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

UEs_List=Obtain_Specified_UE_Config("UEs_List")
#Animation
def animate(index):
    axes=axisartist.Subplot(figure,111) 
    figure.add_axes(axes)
    axes.axis[:].set_visible(False)

    axes.axis["x"]=axes.new_floating_axis(0,0,axis_direction="bottom")
    axes.axis["y"]=axes.new_floating_axis(1,0,axis_direction="bottom")

    axes.axis["x"].set_axisline_style("->",size=1.0)
    axes.axis["y"].set_axisline_style("->",size=1.0)

    plt.xlim((-1)*800,800)
    plt.ylim((-1)*800,800) 

    axes.add_patch(
        patches.Rectangle(
            ((-1)*800, (-1)*800),
            800*2,
            800*2,    
            color="white",
            edgecolor="white"
        )
    )
    gNB_A_Center_Point= plt.Circle((-300,-250), 10,color="#17A589")
    axes.add_artist(gNB_A_Center_Point)

    gNB_A_Range_Point= plt.Circle((-300,-250), 350,color="#17A589",fill=False)
    axes.add_artist(gNB_A_Range_Point)

    gNB_B_Center_Point= plt.Circle((-150,280), 10,color="#95A5A6")
    axes.add_artist(gNB_B_Center_Point)

    gNB_B_Range_Point= plt.Circle((-150,280), 350,color="#95A5A6",fill=False)
    axes.add_artist(gNB_B_Range_Point)

    gNB_C_Center_Point= plt.Circle((350,-227), 10,color="#884EA0")
    axes.add_artist(gNB_C_Center_Point)

    gNB_C_Range_Point= plt.Circle((350,-227), 350,color="#884EA0",fill=False)
    axes.add_artist(gNB_C_Range_Point)

    for UE_Name in UEs_List:
        UE_Position_X=Obtain_Specified_UE_Config(UE_Name)["UE_Position_X"]
        UE_Position_Y=Obtain_Specified_UE_Config(UE_Name)["UE_Position_Y"]
        if(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]==0):
            UE_Position_X=UE_Position_X+(Obtain_Specified_UE_Config(UE_Name)["Script_Line"][index]*Obtain_Specified_UE_Config(UE_Name)["Motion_Speed"])
        else:
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
        # RSRP_Response(UE_Name)
        UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 10,color=Obtain_Specified_UE_Config(UE_Name)["UE_Color"])
        axes.add_artist(UE_Point)
    # UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 5,color=Obtain_System_Field_Configuration("UE_Color"))
    # axes.add_artist(UE_Point)
        print(UE_Name+"[RSRP]: "+str(Obtain_Specified_UE_Config(UE_Name)["RSRP"])+" dBm")
    plt.text(800-600, 0-800+90, "gNB_A", fontsize=10, color="#17A589")
    plt.text(800-600, 0-800+50, "gNB_B", fontsize=10, color="#95A5A6")
    plt.text(800-600, 0-800+10, "gNB_C", fontsize=10, color="#884EA0")

    plt.plot([350,Obtain_Specified_UE_Config("UE_E")["UE_Position_X"]], [-227,Obtain_Specified_UE_Config("UE_E")["UE_Position_Y"]],color="#9C640C")
    plt.plot([-150,Obtain_Specified_UE_Config("UE_F")["UE_Position_X"]], [280,Obtain_Specified_UE_Config("UE_F")["UE_Position_Y"]],color="#D7BDE2")
    if(index<6):
        plt.plot([-300,Obtain_Specified_UE_Config("UE_D")["UE_Position_X"]], [-250,Obtain_Specified_UE_Config("UE_D")["UE_Position_Y"]],color="#2980B9")
    else:
        plt.plot([-150,Obtain_Specified_UE_Config("UE_D")["UE_Position_X"]], [280,Obtain_Specified_UE_Config("UE_D")["UE_Position_Y"]],color="#2980B9")
    plt.plot([-300,Obtain_Specified_UE_Config("UE_C")["UE_Position_X"]], [-250,Obtain_Specified_UE_Config("UE_C")["UE_Position_Y"]],color="#A9DFBF")
    plt.plot([-150,Obtain_Specified_UE_Config("UE_B")["UE_Position_X"]], [280,Obtain_Specified_UE_Config("UE_B")["UE_Position_Y"]],color="#D1F2EB")
anim = animation.FuncAnimation(figure, animate, interval=1000) 
plt.show()