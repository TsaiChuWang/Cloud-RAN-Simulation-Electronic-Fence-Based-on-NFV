import sys
from turtle import distance
import numpy as np
import matplotlib.pyplot as plt
import math
import matplotlib.animation as animation
import mpl_toolkits.axisartist as axisartist 
import matplotlib.patches as patches
import json

figure=plt.figure(figsize=(8,8))

#Obtain gNB_UEs_RSRP_Configs of specified gNB
def Obtain_gNB_RSRP(gNB_Name):
    gNB_Config={}
    with open('./gNB_Configs/gNB_UEs_RSRP.json', 'r') as gNB_UEs_RSRP_file:
        gNB_Configs = json.load(gNB_UEs_RSRP_file)
        gNB_Config=gNB_Configs[gNB_Name]
        gNB_UEs_RSRP_file.close()
    return gNB_Config

def Obtain_UEs_RSSI_Distance(gNB_Name,UE_Name):
    RSRP=Obtain_gNB_RSRP(gNB_Name)[UE_Name]
    Pathloss=Obtain_Field_Config('gNB_Config')['gNB_Antenna_Power']-RSRP
    Pathloss=Pathloss-28-(20*np.log10(Obtain_Field_Config('gNB_Config')['gNB_Center_Frequency']*0.001))
    distance=np.power(10,Pathloss/22)
    Delta_Height=Obtain_Field_Config('gNB_Config')['gNB_BS_Height']-1.7
    Delta_Height_2=Delta_Height*Delta_Height
    distance=distance*distance
    distance=distance-Delta_Height_2
    distance=math.sqrt(distance)
    print("RSRP="+str(RSRP))
    print("Pathloss="+str(Pathloss))
    print("distance="+str(distance))
    return RSRP,distance

def Obtain_UE_Color(UE_Name):
    UE_Name_Index=-1
    List_UEs_Name=Obtain_Field_Config('List_UEs_Name')
    for ind,val in enumerate(List_UEs_Name):
        if(val==UE_Name):
            UE_Name_Index=ind
    if(UE_Name_Index==-1):
        print("No data for "+UE_Name+" in Field")
    return Obtain_Field_Config('List_UEs_Color')[UE_Name_Index]

def Obtain_Field_Config(key):
    Field_Config={}
    with open('./gNB_Configs/Field.json') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()
    return Field_Config[key]

def animate(i):
    # Motion_Event()
    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of RSSP with '+Obtain_Field_Config('gNB_Config')['gNB_Name']+'\n')
    figure.add_axes(axes)
    # figure.canvas.mpl_connect('key_press_event', on_press)
    axes.axis[:].set_visible(False)

    axes.axis["x"]=axes.new_floating_axis(0,0,axis_direction="bottom")
    axes.axis["y"]=axes.new_floating_axis(1,0,axis_direction="bottom")

    axes.axis["x"].set_axisline_style("->",size=1.0)
    axes.axis["y"].set_axisline_style("->",size=1.0)

    plt.xlim((-1)*Obtain_Field_Config("X_RANGE"),Obtain_Field_Config("X_RANGE"))
    plt.ylim((-1)*Obtain_Field_Config("Y_RANGE"),Obtain_Field_Config("Y_RANGE")) 

    # plt.text(200, -320, "Distance_2D: "+"{:.7f}".format(Obtain_Field_Paramter_Num("Distance_2D")), fontsize=8, color=Obtain_Field_Paramter("UE_Color"))
    # plt.text(200, -350, "Pathloss: "+"{:.7f}".format(Obtain_Field_Paramter_Num("Pathloss")), fontsize=10, color=Obtain_Field_Paramter("UE_Color"))
    # plt.text(200, -380, "RSRP: "+"{:.7f}".format(Obtain_Field_Paramter_Num("RSRP")), fontsize=10, color=Obtain_Field_Paramter("UE_Color"))
    
    axes.add_patch(
        patches.Rectangle(
            ((-1)*Obtain_Field_Config("X_RANGE"), (-1)*Obtain_Field_Config("Y_RANGE")),
            Obtain_Field_Config("X_RANGE")*2,
            Obtain_Field_Config("X_RANGE")*2,    
            color="white",
            edgecolor="white"
        )
    )
    gNB_Center_Point= plt.Circle((Obtain_Field_Config('gNB_Config')["gNB_Position_X"],Obtain_Field_Config('gNB_Config')["gNB_Position_Y"]), 5,color=Obtain_Field_Config('gNB_Config')["gNB_Center_Color"])
    axes.add_artist(gNB_Center_Point)

    gNB_Range_Point= plt.Circle((Obtain_Field_Config('gNB_Config')["gNB_Position_X"],Obtain_Field_Config('gNB_Config')["gNB_Position_Y"]), Obtain_Field_Config('gNB_Config')["gNB_Limit_Range"],color=Obtain_Field_Config('gNB_Config')["gNB_Range_Color"],fill=False)
    axes.add_artist(gNB_Range_Point)

    plt.text(Obtain_Field_Config('gNB_Config')["gNB_Position_X"]-70, Obtain_Field_Config('gNB_Config')["gNB_Position_Y"]+10,Obtain_Field_Config('gNB_Config')["gNB_Name"], fontsize=10, color=Obtain_Field_Config('gNB_Config')["gNB_Center_Color"])
    
    for name in Obtain_Field_Config('List_UEs_Name'):
        print("name="+name)
        RSRP,distance=Obtain_UEs_RSSI_Distance(Obtain_Field_Config('gNB_Config')['gNB_Name'],name)
        color=Obtain_UE_Color(name)
        UE_Point = plt.Circle((Obtain_Field_Config('gNB_Config')["gNB_Position_X"],Obtain_Field_Config('gNB_Config')["gNB_Position_Y"]), distance,color=color,fill=False)
        axes.add_artist(UE_Point)
anim = animation.FuncAnimation(figure, animate, interval=1000) 
plt.show()
