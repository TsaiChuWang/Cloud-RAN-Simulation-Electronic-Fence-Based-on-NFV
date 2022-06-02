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