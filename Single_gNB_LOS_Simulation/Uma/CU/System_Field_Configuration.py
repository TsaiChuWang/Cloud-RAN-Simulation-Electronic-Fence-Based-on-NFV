import numpy as np
import matplotlib.pyplot as plt
import json
import math
import matplotlib.animation as animation
import mpl_toolkits.axisartist as axisartist 
import matplotlib.patches as patches


gNB_Name="gNB_A"

"""
Functions of Calculations
1.RSRP_TRANSLATION_DISTANCE
"""
def RSRP_TRANSLATION_DISTANCE(UE_Name,RSRP):
    PathLoss=Obtain_System_Field_Configuration(gNB_Name)["gNB_Antenna_Power"]-RSRP
    PathLoss=PathLoss-28.0
    PathLoss=PathLoss-20.0*np.log10(Obtain_System_Field_Configuration("gNB_A")["gNB_Center_Frequency"]/1000)
    Distance3D=PathLoss/22.0
    Distance3D=math.pow(10,Distance3D)
    Delta_H=Obtain_System_Field_Configuration("gNB_A")["gNB_BS_Height"]-Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name)["User_Terminal_Height"]
    Distance3D=Distance3D*Distance3D
    Distance3D=Distance3D-(Delta_H*Delta_H)
    Distance2D=math.sqrt(Distance3D)
    return Distance2D

"""
Functions Related to Parameters:
1.CU_gNB_UEs_Configuration
2.UE_Configuration
3.Timer_Configuration
4.System_Field_Configuration
"""
def Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name):
    CU_gNB_UEs_Configuration={}
    with open('./configuration/CU_gNB_UEs_Configuration.json', 'r',encoding='utf-8',errors='ignore') as CU_gNB_UEs_Configuration_file:
        CU_gNB_UEs_Configuration = json.load(CU_gNB_UEs_Configuration_file)
        print(CU_gNB_UEs_Configuration)
        CU_gNB_UEs_Configuration_file.close()
    return CU_gNB_UEs_Configuration[gNB_Name][UE_Name]

def Obtain_System_Field_Configuration(key):
    System_Field_Configuration={}
    with open('./configuration/System_Field_Configuration.json', 'r',encoding='utf-8',errors='ignore') as System_Field_Configuration_file:
        System_Field_Configuration= json.load(System_Field_Configuration_file)
        System_Field_Configuration_file.close()
    return System_Field_Configuration[key]

figure=plt.figure(figsize=(8,8))
#Animation
def animate(i):
    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of RSRP Line with '+gNB_Name+'\n')
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
    gNB_Position_X=Obtain_System_Field_Configuration('gNB_A')["gNB_Position_X"]
    gNB_Position_Y=Obtain_System_Field_Configuration('gNB_A')["gNB_Position_Y"]
    gNB_Center_Point= plt.Circle((gNB_Position_X,gNB_Position_Y), 10,color=Obtain_System_Field_Configuration('gNB_A')["gNB_Center_Color"])
    axes.add_artist(gNB_Center_Point)

    gNB_Range_Point= plt.Circle((gNB_Position_X,gNB_Position_Y), Obtain_System_Field_Configuration('gNB_A')["gNB_Limit_Range"],color=Obtain_System_Field_Configuration('gNB_A')["gNB_Range_Color"],fill=False)
    axes.add_artist(gNB_Range_Point)

    plt.text(gNB_Position_X-100, Obtain_System_Field_Configuration('gNB_A')["gNB_Position_Y"]+20, Obtain_System_Field_Configuration('gNB_A')["gNB_Name"], fontsize=10, color=Obtain_System_Field_Configuration('gNB_A')["gNB_Center_Color"])
    UEs_List=Obtain_CU_gNB_UEs_Configuration(gNB_Name,"UEs_List")
    for UE_Name in UEs_List:
        Distance_2D=RSRP_TRANSLATION_DISTANCE(UE_Name,Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name)['RSRP'])
        
        UE_RSRP_Line = plt.Circle((gNB_Position_X,gNB_Position_Y), Distance_2D,color=Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name)['UE_Color'],fill=False)
        print(UE_Name+"[RSRP]: "+str(Obtain_CU_gNB_UEs_Configuration(gNB_Name,UE_Name)['RSRP'])+" dBm")
        if(Distance_2D>Obtain_System_Field_Configuration('gNB_A')["gNB_Limit_Range"]):
            print(UE_Name+" is out of range!!")
        axes.add_artist(UE_RSRP_Line)

anim = animation.FuncAnimation(figure, animate, interval=1000) 
plt.show()