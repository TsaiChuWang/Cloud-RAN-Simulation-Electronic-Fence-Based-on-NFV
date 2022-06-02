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

logname='./log/UE_Position_Control_GUI.log'
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def getCurrentTime():
    return str(datetime.datetime.now())
    
def on_press(event):
    #print('press', event.key)
    sys.stdout.flush()

    if event.key == 'x':
        visible = xl.get_visible()
        xl.set_visible(not visible)
        fig.canvas.draw()
    if event.key == 'up':
        print(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head North with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        logging.info(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head North with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        UE_Position_X,UE_Position_Y=Obtain_UE_Position()
        UE_Position_Update({"UE_Position_Y":UE_Position_Y+Obtain_Field_Paramter_Num("Motion_Speed")})
    if event.key == 'down':
        print(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head South with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        logging.info(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head South with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        UE_Position_X,UE_Position_Y=Obtain_UE_Position()
        UE_Position_Update({"UE_Position_Y":UE_Position_Y-Obtain_Field_Paramter_Num("Motion_Speed")})
    if event.key == 'right':
        logging.info(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head East with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        print(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head East with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        UE_Position_X,UE_Position_Y=Obtain_UE_Position()
        UE_Position_Update({"UE_Position_X":UE_Position_X+Obtain_Field_Paramter_Num("Motion_Speed")})
    if event.key == 'left':
        print(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head West with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        logging.info(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" move head West with speed "+str(Obtain_Field_Paramter_Num('Motion_Speed'))+" m/s.")
        UE_Position_X,UE_Position_Y=Obtain_UE_Position()
        UE_Position_Update({"UE_Position_X":UE_Position_X-Obtain_Field_Paramter_Num("Motion_Speed")})

def update_UE_Config(dict_new):
    UE_Config={}
    with open('./config/UE.json', 'r') as UE_Config_file:
        UE_Config = json.load(UE_Config_file)
        UE_Config_file.close()

    UE_Config.update(dict_new)
    with open('./config/UE.json', 'w') as f:
        f.write(json.dumps(UE_Config))
    
def Obtain_UE_Position():
    UE_Config={}
    with open('./config/UE.json', 'r') as UE_Config_file:
        UE_Config = json.load(UE_Config_file)
        UE_Config_file.close()
    return int(UE_Config['UE_Position_X']),int(UE_Config['UE_Position_Y'])

def UE_Position_Update(dict_new):
    UE_Position_Config={}
    with open('./config/UE.json', 'r') as UE_Config_file:
        UE_Position_Config = json.load(UE_Config_file)
        UE_Config_file.close()

    with open('./config/UE.json', 'w') as UE_Config_file:
        UE_Position_Config.update(dict_new)
        json.dump(UE_Position_Config, UE_Config_file, ensure_ascii=False)
        UE_Config_file.close()

def Obtain_Field_Paramter_Num(key):
    Field_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()
    return float(Field_Config[key])

def Obtain_Field_Paramter(key):
    Field_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()
    return Field_Config[key]

def Update_Field_Config(dict_new):
    Field_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()

    Field_Config.update(dict_new)
    with open('./config/Field.json', 'w') as f:
        f.write(json.dumps(Field_Config))

def Obtain_Field_gNB_Config_Paramter_Num(key):
    Field_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()
    return float(Field_Config["gNB_Config"][key])

def Obtain_Field_gNB_Config_Paramter(key):
    Field_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_Config_file.close()
    return Field_Config["gNB_Config"][key]

def Update_Field_gNB_Config(dict_new):
    Field_Config={}
    Field_gNB_Config={}
    with open('./config/Field.json', 'r') as Field_Config_file:
        Field_Config = json.load(Field_Config_file)
        Field_gNB_Config=Field_Config['gNB_Config']
        Field_Config_file.close()

    Field_gNB_Config.update(dict_new)
    Field_Config.update({"gNB_Config":Field_gNB_Config})
    with open('./config/Field.json', 'w') as f:
        f.write(json.dumps(Field_Config))
    print("Field_gNB_Config Update Complete")

def Obtain_UEConfig_Parameters(key):
    UE_Config={}
    with open('./config/UE.json', 'r') as UE_Config_file:
        UE_Config = json.load(UE_Config_file)
        UE_Config_file.close()
    return UE_Config[key]
    
def gNB_Information_Request():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Position_Control_Panel.py Function:gNB_Information_Request")
    logging.info("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Position_Control_Panel.py Function:gNB_Information_Request")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1445/gNB_Information_Request"
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(datetime.datetime.now())
    print(response.text)
    return json.loads(response.text)

def gNB_Connection_Ready_Request():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Position_Control_Panel.py Function:gNB_Connection_Ready_Request")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1445/gNB_Connection_Ready_Request"
    payload={
        "UE_Name": Obtain_UEConfig_Parameters("UE_Name"),
        "UE_IP": Obtain_UEConfig_Parameters("UE_IP"),
        "UE_Identity":Obtain_UEConfig_Parameters("UE_Identity")
    }
    headers = {}
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    print(json.loads(response.text)['msg'])

    if(str(json.loads(response.text)['msg']) is not "error"):
        update_UE_Config({"Connection_Ready":1})
    else:
        update_UE_Config({"Connection_Ready":0})
        print("error:Restart function")

def Calculate_Distance_Breakpoint():
    User_Terminal_Height=Obtain_UEConfig_Parameters('User_Terminal_Height')
    gNB_BS_Height=Obtain_Field_gNB_Config_Paramter_Num('gNB_BS_Height')
    gNB_Center_Frequency=Obtain_Field_gNB_Config_Paramter_Num('gNB_Center_Frequency')
   
    print("User_Terminal_Height="+str(User_Terminal_Height))
    print("gNB_BS_Height="+str(gNB_BS_Height))
    print("gNB_Center_Frequency="+str(gNB_Center_Frequency))
    
    Distance_Breakpoint=2*math.pi
    Distance_Breakpoint=Distance_Breakpoint*User_Terminal_Height
    Distance_Breakpoint=Distance_Breakpoint*gNB_BS_Height
    Distance_Breakpoint=Distance_Breakpoint*gNB_Center_Frequency
    Distance_Breakpoint=Distance_Breakpoint/(300000000.0)
    Distance_Breakpoint=Distance_Breakpoint*1000000
    Update_Field_Config({"Distance_Breakpoint":Distance_Breakpoint})

figure=plt.figure(figsize=(8,8))

def animate(i):
    UE_Position_X,UE_Position_Y=Obtain_UE_Position()
    print(getCurrentTime()+" "+Obtain_UEConfig_Parameters("UE_Name")+" Current POsition: "+str(Obtain_UE_Position()))
    axes=axisartist.Subplot(figure,111) 
    axes.set_title('Plot of '+Obtain_UEConfig_Parameters('UE_Name')+' Realtive Position with '+Obtain_Field_gNB_Config_Paramter('gNB_Name')+'\n')
    figure.add_axes(axes)
    figure.canvas.mpl_connect('key_press_event', on_press)
    axes.axis[:].set_visible(False)

    axes.axis["x"]=axes.new_floating_axis(0,0,axis_direction="bottom")
    axes.axis["y"]=axes.new_floating_axis(1,0,axis_direction="bottom")

    axes.axis["x"].set_axisline_style("->",size=1.0)
    axes.axis["y"].set_axisline_style("->",size=1.0)

    plt.xlim((-1)*Obtain_Field_Paramter_Num("X_RANGE"),Obtain_Field_Paramter_Num("X_RANGE"))
    plt.ylim((-1)*Obtain_Field_Paramter_Num("Y_RANGE"),Obtain_Field_Paramter_Num("Y_RANGE")) 

    axes.add_patch(
        patches.Rectangle(
            ((-1)*Obtain_Field_Paramter_Num("X_RANGE"), (-1)*Obtain_Field_Paramter_Num("Y_RANGE")),
            Obtain_Field_Paramter_Num("X_RANGE")*2,
            Obtain_Field_Paramter_Num("X_RANGE")*2,    
            color="white",
            edgecolor="white"
        )
    )
    gNB_Center_Point= plt.Circle((Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_X"),Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_X")), 5,color=Obtain_Field_gNB_Config_Paramter("gNB_Center_Color"))
    axes.add_artist(gNB_Center_Point)

    gNB_Range_Point= plt.Circle((Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_X"),Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_X")), Obtain_Field_gNB_Config_Paramter_Num("gNB_Limit_Range"),color=Obtain_Field_gNB_Config_Paramter("gNB_Range_Color"),fill=False)
    axes.add_artist(gNB_Range_Point)

    plt.text(Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_X")-70, Obtain_Field_gNB_Config_Paramter_Num("gNB_Position_Y")+10, Obtain_Field_gNB_Config_Paramter('gNB_Name'), fontsize=10, color=Obtain_Field_gNB_Config_Paramter("gNB_Center_Color"))
    UE_Point = plt.Circle((UE_Position_X,UE_Position_Y), 5,color=Obtain_Field_Paramter("UE_Color"))
    axes.add_artist(UE_Point)
    
def CLEAN_UP():
    update_UE_Config({"Connection_Ready":0})

CLEAN_UP() 
while True:
    if(Obtain_UEConfig_Parameters("Connection_Ready")):
        gNB_Config=gNB_Information_Request()
        Update_Field_gNB_Config(gNB_Config)
        Calculate_Distance_Breakpoint()
        break
    else:
        print("ConnectionNOT Ready YET")
        logging.info("ConnectionNOT Ready YET")
        gNB_Connection_Ready_Request()
        
anim = animation.FuncAnimation(figure, animate, interval=1000) 
plt.show()