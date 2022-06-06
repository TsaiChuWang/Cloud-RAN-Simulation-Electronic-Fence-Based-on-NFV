import sys
from textwrap import fill
import numpy as np
import matplotlib.pyplot as plt
import json
import math
import matplotlib.animation as animation
import mpl_toolkits.axisartist as axisartist 
import matplotlib.patches as patches
import datetime
import logging

from matplotlib.collections import PolyCollection

import requests
import time
from flask import jsonify
import random

"""
Functions Related to Parameters:
1.System Field Configuration
2.gNB_Information
3.UEs_Configurations
"""
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

def Obtain_gNB_Information(gNB_Name):
    gNBs_Configuration={}
    with open('./configuration/gNBs_Configuration.json') as gNBs_Configuration_file:
        gNBs_Configuration = json.load(gNBs_Configuration_file)
        gNBs_Configuration_file.close()
    if(gNB_Name==""):
        return gNBs_Configuration
    return gNBs_Configuration[gNB_Name]

def Obtain_UEs_Configurations(UE_Name):
    UEs_Configurations={}
    with open('./configuration/UEs_Configuration.json') as UEs_Configurations_file:
        try:
            UEs_Configurations = json.load(UEs_Configurations_file)
        except json.decoder.JSONDecodeError:
            print(" except json.decoder.JSONDecodeError")
            time.sleep(1)
            try:
                UEs_Configurations = json.load(UEs_Configurations_file)
            except json.decoder.JSONDecodeError:
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

def INITIALZATION():
    gNBs_List=Obtain_gNB_Information("gNBs_List")

figure=plt.figure(figsize=(10,5.55))
img=plt.imread("NIU_MAP.png")
# fig,ax=plt.subplots()

def UE_OUT_OF_RANGE(UE_Position_X,UE_Position_Y):
    X_OUT=False
    Y_OUT=False
    if(UE_Position_X<=-2385 or UE_Position_X>=-1985):
        X_OUT=True
    if(UE_Position_Y<=-800 or UE_Position_Y>=-135):
        Y_OUT=True
    return X_OUT or Y_OUT
#Animation
def animate(i):
    plt.clf()
    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of Multiple gNBs LOS Uma System with NIU Models\n')

    axes.imshow(img,extent=[-3000,3000,-1600,1600])
    figure.add_axes(axes)

    gNBs_List=Obtain_gNB_Information("gNBs_List")
    for gNB_Name in gNBs_List:
        gNB=Obtain_gNB_Information(gNB_Name)
        gNB_Center_Point= plt.Circle((gNB["gNB_Position_X"],gNB["gNB_Position_Y"]), 15,color="#FF359A")
        axes.add_artist(gNB_Center_Point)
        plt.text(gNB["gNB_Position_X"]-260, gNB["gNB_Position_Y"]-20,gNB_Name, fontsize=11, color="#FF359A")
    
    Dormitory=Obtain_System_Field_Configuration("Dormitory")
    if(Dormitory=="Male"):
        plt.plot([Obtain_System_Field_Configuration("Male_Start_X"),Obtain_System_Field_Configuration("Male_Second_X")], [Obtain_System_Field_Configuration("Male_Start_Y"),Obtain_System_Field_Configuration("Male_Second_Y")],color=Obtain_System_Field_Configuration("Male_Color"),linewidth=1)
        plt.plot([Obtain_System_Field_Configuration("Male_Third_X"),Obtain_System_Field_Configuration("Male_Second_X")], [Obtain_System_Field_Configuration("Male_Third_Y"),Obtain_System_Field_Configuration("Male_Second_Y")],color=Obtain_System_Field_Configuration("Male_Color"),linewidth=1)
        plt.plot([Obtain_System_Field_Configuration("Male_Third_X"),Obtain_System_Field_Configuration("Male_End_X")], [Obtain_System_Field_Configuration("Male_Third_Y"),Obtain_System_Field_Configuration("Male_End_Y")],color=Obtain_System_Field_Configuration("Male_Color"),linewidth=1)
        plt.plot([Obtain_System_Field_Configuration("Male_Start_X"),Obtain_System_Field_Configuration("Male_End_X")], [Obtain_System_Field_Configuration("Male_Start_Y"),Obtain_System_Field_Configuration("Male_End_Y")],color=Obtain_System_Field_Configuration("Male_Color"),linewidth=1)
        
        plt.text(Obtain_System_Field_Configuration("Male_Start_X"),Obtain_System_Field_Configuration("Male_Start_Y")-55,"Range :Student Dormitory", fontsize=10, color=Obtain_System_Field_Configuration("Male_Color"))

    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for index,UE_Name in enumerate(UEs_List):
        UE=Obtain_UEs_Configurations(UE_Name)
        UE_Position_X=UE["UE_Position_X"]
        UE_Position_Y=UE["UE_Position_Y"]
        UE_Color=UE["UE_Color"]
        if(UE_OUT_OF_RANGE(UE_Position_X,UE_Position_Y)):
            UE_Color="#ff0000"
        UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 12,color=UE_Color)
        axes.add_artist(UE_Point)

        PCell=Obtain_gNB_Information(UE["Connected_Primary_Cell_Name"])
        PCell_X=PCell["gNB_Position_X"]
        PCell_Y=PCell["gNB_Position_Y"]
        print(UE_Name+": "+str(UE["RSRP"])+ "dBm")
        SCell=Obtain_gNB_Information(UE["Connected_Secondary_Cell_Name"])
        SCell_X=SCell["gNB_Position_X"]
        SCell_Y=SCell["gNB_Position_Y"]
        plt.plot([UE_Position_X,PCell_X], [UE_Position_Y, PCell_Y],color=UE_Color,linewidth=1)
        plt.plot([UE_Position_X,SCell_X], [UE_Position_Y, SCell_Y],color=UE_Color,linewidth=1,linestyle=':')
        plt.text(Obtain_System_Field_Configuration("X_RANGE"),0-Obtain_System_Field_Configuration("Y_RANGE")+600-(index*50), UE_Name+": "+"{:.7f}".format(UE["RSRP"])+ "dBm", fontsize=10, color=UE_Color)
        


anim = animation.FuncAnimation(figure, animate, interval=1500) 
plt.show()