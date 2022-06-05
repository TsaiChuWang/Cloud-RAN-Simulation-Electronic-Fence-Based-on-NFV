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

figure=plt.figure(figsize=(8,8))


#Animation
def animate(i):
    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of Multiple gNBs LOS Uma System \n')
    figure.add_axes(axes)
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
    gNBs_List=Obtain_gNB_Information("gNBs_List")
    for gNB_Name in gNBs_List:
        gNB=Obtain_gNB_Information(gNB_Name)
        # print(gNB["gNB_Position_X"])
        # print(gNB["gNB_Position_Y"])
        # print(gNB["gNB_Center_Color"])
        gNB_Center_Point= plt.Circle((gNB["gNB_Position_X"],gNB["gNB_Position_Y"]), 10,color=gNB["gNB_Center_Color"])
        axes.add_artist(gNB_Center_Point)
        plt.text(gNB["gNB_Position_X"]-150, gNB["gNB_Position_Y"],gNB_Name, fontsize=10, color=gNB["gNB_Center_Color"])
    
    Range_Type=Obtain_System_Field_Configuration("Range_Type")
    if(Range_Type=="Rectangle"):
        axes.add_patch(
            patches.Rectangle(
                (Obtain_System_Field_Configuration("Rectangle_Start_X"), Obtain_System_Field_Configuration("Rectangle_Start_Y")),
                Obtain_System_Field_Configuration("Rectangle_Width"),
                Obtain_System_Field_Configuration("Rectangle_Length"),    

                edgecolor=Obtain_System_Field_Configuration("Range_Color"),
                fill=False
            )
        )
        plt.text(Obtain_System_Field_Configuration("Rectangle_Start_X"), Obtain_System_Field_Configuration("Rectangle_Start_Y")-25,"Range_Type: "+Range_Type, fontsize=10, color=Obtain_System_Field_Configuration("Range_Color"))
    
    UEs_List=Obtain_UEs_Configurations("UEs_List")
    for index,UE_Name in enumerate(UEs_List):
        UE=Obtain_UEs_Configurations(UE_Name)
        UE_Position_X=UE["UE_Position_X"]
        UE_Position_Y=UE["UE_Position_Y"]
        UE_Color=UE["UE_Color"]
        UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 10,color=UE_Color)
        axes.add_artist(UE_Point)

        PCell=Obtain_gNB_Information(UE["Connected_Primary_Cell_Name"])
        PCell_X=PCell["gNB_Position_X"]
        PCell_Y=PCell["gNB_Position_Y"]
        print(UE_Name+": "+str(UE["RSRP"])+ "dBm")
        SCell=Obtain_gNB_Information(UE["Connected_Secondary_Cell_Name"])
        SCell_X=SCell["gNB_Position_X"]
        SCell_Y=SCell["gNB_Position_Y"]
        plt.plot([UE_Position_X,PCell_X], [UE_Position_Y, PCell_Y],color=UE_Color,linewidth=0.8)
        plt.plot([UE_Position_X,SCell_X], [UE_Position_Y, SCell_Y],color=UE_Color,linewidth=0.8,linestyle=':')
        # if(UE["UE_OUT_OF_RANGE"]):
        #     UE_Color="#ff0000"
        plt.text(Obtain_System_Field_Configuration("X_RANGE")-400, 0-Obtain_System_Field_Configuration("Y_RANGE")+300-(index*30), UE_Name+": "+"{:.7f}".format(UE["RSRP"])+ "dBm", fontsize=10, color=UE_Color)
        


anim = animation.FuncAnimation(figure, animate, interval=5000) 
plt.show()