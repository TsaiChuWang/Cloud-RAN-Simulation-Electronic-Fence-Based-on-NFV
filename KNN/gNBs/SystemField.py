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


def INITIALIZATION(list_len):
    gNBs_Configurations={}
    gNB_Lists=["gNB_"+chr(65+i) for i in range(list_len)]
    gNBs_Configurations.update({"gNB_Lists":gNB_Lists})
    for gNB_Name in gNB_Lists:
        gNB_Configuration={
            "gNB_Position_X": random.randint(-2600,2600),
            "gNB_Position_Y": random.randint(-1200,1200),
            "gNB_BS_Height": 25,
            "gNB_Center_Frequency": 3308.1308662294405,
            "gNB_Antenna_Power": 33.671520898470746,
            "gNB_Center_Color": "#2CD8C1",
            "gNB_Range_Color": "#40F8DF"
        }
        gNBs_Configurations.update({gNB_Name:gNB_Configuration})
    with open('./gNBs.json', 'w') as gNBs_Configurations_file:
        json.dump(gNBs_Configurations, gNBs_Configurations_file, ensure_ascii=False)
        gNBs_Configurations_file.close()
    print(gNBs_Configurations)

def Obtain_gNB_Information(gNB_Name):
    gNBs_Configuration={}
    with open('./gNBs.json') as gNBs_Configuration_file:
        gNBs_Configuration = json.load(gNBs_Configuration_file)
        gNBs_Configuration_file.close()
    if(gNB_Name==""):
        return gNBs_Configuration
    return gNBs_Configuration[gNB_Name]

def Grid(interval):
    ix=-3000+interval
    iy=-1600+interval
    while(ix<3000):
        plt.plot([ix,ix], [-1600,1600 ],color="#3F5C1D",linewidth=0.1)
        ix=ix+interval
    while(iy<1600):
        plt.plot([-3000,3000], [iy,iy],color="#3F5C1D",linewidth=0.1)
        iy=iy+interval

def Distance2D(gNB,X,Y):
    gNB_X=gNB["gNB_Position_X"]
    gNB_Y=gNB["gNB_Position_Y"]
    distance2D=math.sqrt(((gNB_X-X)**2)+((gNB_Y-Y)**2))
    return distance2D

def Pathloss(gNB,distance2D):
    distance3D=distance2D**2
    Delta_Height=25.0-(random.uniform(1.5,15))
    distance3D=distance3D+(Delta_Height**2)
    distance3D=math.sqrt(distance3D)
    pathloss=28.0+(22.0*np.log10(gNB["gNB_Center_Frequency"]))
    pathloss=pathloss+(20.0*np.log10(distance3D))
    return pathloss

def CalRSRP(gNB_Name,X,Y):
    gNB=Obtain_gNB_Information(gNB_Name)
    distance2D=Distance2D(gNB,X,Y)
    if(distance2D>650.0):
        return 0
    else:
        pathloss=Pathloss(gNB,distance2D)
        RSRP=gNB["gNB_Antenna_Power"]-pathloss
        return RSRP*random.uniform(0.85,0.98)

def writePoints(interval,gNB_Lists):
    text=""
    xs=[-3000+((interval/2)*i) for i in range(1,240)]
    ys=[-1600+((interval/2)*i) for i in range(1,128)]
    points=[]
    for i in xs:
        for j in ys:
            points.append([i,j])
    for point in points:
        line="("+str(point[0])+","+str(point[1])+") "
        max_index=1
        max=-1
        RSRPs=[]
        num=random.randint(5,20)
        for i in range(num):
            line="("+str(point[0])+","+str(point[1])+") "
            max_index=-1
            max=-1
            for gNB_Name in gNB_Lists:
                RSRP=CalRSRP(gNB_Name,point[0],point[1])
                RSRPs.append(RSRP)
                line=line+str(RSRP)+" "
            
            
            
            for ind,RSRP in enumerate(RSRPs):
                if(RSRP>max):
                    max=RSRP
                    max_index=ind
                else:
                    continue
            line=line+gNB_Lists[max_index]
            RSRPs=[]
            text=text+line+"\n"
    
    path = './points.txt'
    f = open(path, 'w')
    f.write(text)
    f.close()


figure=plt.figure(figsize=(10,5.55))
img=plt.imread("NIU_MAP.png")



# INITIALIZATION(5)

plt.clf()
axes=axisartist.Subplot(figure,111) 
axes.set_title('Plot of Multiple gNBs LOS Uma System with NIU Models\n')

axes.imshow(img,extent=[-3000,3000,-1600,1600])
figure.add_axes(axes)

gNB_Lists=Obtain_gNB_Information("gNB_Lists")
interval=50
Grid(interval)

writePoints(interval,gNB_Lists)

for gNB_Name in gNB_Lists:
    gNB=Obtain_gNB_Information(gNB_Name)
    gNB_Center_Point= plt.Circle((gNB["gNB_Position_X"],gNB["gNB_Position_Y"]), 15,color="#FF359A")
    axes.add_artist(gNB_Center_Point)
    plt.text(gNB["gNB_Position_X"]+30, gNB["gNB_Position_Y"]-20,gNB_Name, fontsize=8, color="#FF359A")

plt.show()