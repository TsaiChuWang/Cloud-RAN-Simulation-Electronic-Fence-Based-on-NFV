from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json
import socket
import random
import requests

app = Flask(__name__)
PORT = 1441
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_Uma_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)

"""
Functions about Parameters in Configuraiotn:
1.Cell_Group_Configuration (Obtain/Obtain[gNB]/Update[gNB])
"""

gNB_IP=""
CU_IP="10.0.2.99"

#Initialize Parameter
def Initialize():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    gNB_IP=s.getsockname()[0]

def RANDOMVREATEGNBS():
    CellGroup_List=Obtain_Cell_Group_Configuration("CellGroup_List")
    for CellGroup_Name in CellGroup_List:
        gNB_List=Obtain_Cell_Group_Configuration_gNB(CellGroup_Name,"gNBs_List")
        for gNB_Name in gNB_List:
            gNB_Identity="{0:b}".format(random.randint(0,2**22))
            Cell_Identity="{0:b}".format(random.randint(0,2**14))
            max_x=0
            max_y=0
            if(CellGroup_Name=="Cell_Group_A"):
                max_x=0
                max_y=0
            if(CellGroup_Name=="Cell_Group_B"):
                max_x=-600
                max_y=-600
            if(CellGroup_Name=="Cell_Group_C"):
                max_x=0
                max_y=-600
            data={
                "gNB_Name": gNB_Name,
                "gNB_IP": gNB_IP,
                "MAC": "080027B457A5",
                "gNB_Identity":gNB_Identity,
                "Cell_Identity":Cell_Identity,
                "PLMN":"46692",
                "MCC":466,
                "MNC":92,
                "NR_CGI":"46692"+gNB_Identity+Cell_Identity,
                "Telecommunications":"Chunghwa",
                "Frequency_Band_Name":"GSM 900 / UMTS 2100",
                "Bit_Length_gNB_ID":22,
                "Bit_Length_Cell_ID":14,

                "gNB_Position_X":random.randint(max_x,max_x+600),
                "gNB_Position_Y":random.randint(max_y,max_y+600),
                "gNB_BS_Height":25,

                "NR_Operating_Band":"n78",
                "FRaster":30,
                "Uplink_NR_ARFCN":"",
                "Downlink_NR_ARFCN": 627573,
                "Duplex_Mode":"TDD",
                "gNB_Center_Frequency": random.uniform(3300,3800),

                "Bandwidth": 20,
                "gNB_Antenna_model": "C2D2F030404X6",
                "gNB_Antenna_gain": 17,

                "feeder_system": "LTE",
                "feeder_loss_per_hunrad": 12.1,
                "feeder_distance":100,
                "feeder_line_loss":12.1,

                "gNB_Antenna_Power": random.uniform(20,35),

                "NR-ARFCN": 653333,
                "eNodeB_Admission_Control": True,
                "gNB_Limit_Range": 500,
                "gNB_Center_Color": "#2CD8C1",
                "gNB_Range_Color": "#40F8DF"
            }
            Update_Cell_Group_Configuration_gNB(CellGroup_Name,gNB_Name,data)
            print(gNB_Name)
        print(CellGroup_Name)

# Obtain Cell Group Configuration
def Obtain_Cell_Group_Configuration(CellGroup_Name):
    Cell_Group_Configuration={}
    with open('./configuration/Cell_Group_Configuration.json') as Cell_Group_Configuration_file:
        Cell_Group_Configuration = json.load(Cell_Group_Configuration_file)
        Cell_Group_Configuration_file.close()
    if(CellGroup_Name==""):
        return Cell_Group_Configuration
    return Cell_Group_Configuration[CellGroup_Name]

#Obtain gNB_Informations
def Obtain_Cell_Group_Configuration_gNB(CellGroup_Name,gNB_Name):
    Cell_Group_Configuration_CellGroup=Obtain_Cell_Group_Configuration(CellGroup_Name)
    Cell_Group_Configuration_CellGroup_gNB=Cell_Group_Configuration_CellGroup[gNB_Name]
    return Cell_Group_Configuration_CellGroup_gNB

#Update gNB_Information
def Update_Cell_Group_Configuration_gNB(CellGroup_Name,gNB_Name,data):
    Cell_Group_Configuration=Obtain_Cell_Group_Configuration("")
    Cell_Group_Configuration_CellGroup=Cell_Group_Configuration[CellGroup_Name]
    Cell_Group_Configuration_CellGroup_gNB=Cell_Group_Configuration_CellGroup[gNB_Name]
    Cell_Group_Configuration_CellGroup_gNB.update(data)
    Cell_Group_Configuration_CellGroup.update({gNB_Name:Cell_Group_Configuration_CellGroup_gNB})
    Cell_Group_Configuration.update({CellGroup_Name:Cell_Group_Configuration_CellGroup})
    with open('./configuration/Cell_Group_Configuration.json', 'w') as Cell_Group_Configuration_file:
        json.dump(Cell_Group_Configuration, Cell_Group_Configuration_file, ensure_ascii=False)
        Cell_Group_Configuration_file.close()


def Response_gNB_Information(payload):
    url = "http://"+CU_IP+":1441/RecievegNB_Information"
    payload=json.dumps(payload)
    headers = { 'Content-Type': 'application/json' }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

@app.route("/gNB_Information_Request", methods=['GET'])
def gNB_Information_Request():
    logging.info("gNB Information request")
    CellGroup_List=Obtain_Cell_Group_Configuration("CellGroup_List")
    data_response={}
    gNBs_List=[]
    for CellGroup_Name in CellGroup_List:
        # cellGroup_data={}
        gNB_List=Obtain_Cell_Group_Configuration_gNB(CellGroup_Name,"gNBs_List")
        for gNB_Name in gNB_List:
            gNBs_List.append(gNB_Name)
            data=Obtain_Cell_Group_Configuration_gNB(CellGroup_Name,gNB_Name)
            gNB_data={
                "gNB_Name": data["gNB_Name"],
                "gNB_IP": "10.0.2.100",
                "gNB_Identity": data["gNB_Identity"],
                "gNB_Antenna_Power": data["gNB_Antenna_Power"],
                "gNB_Center_Frequency": data["gNB_Center_Frequency"],
                "gNB_Position_X": data["gNB_Position_X"],
                "gNB_Position_Y": data["gNB_Position_Y"],
                "gNB_BS_Height": data["gNB_BS_Height"],
                "gNB_BS_Height": data["gNB_BS_Height"]
            }
            # cellGroup_data.update({gNB_Name:gNB_data})
            data_response.update({gNB_Name:gNB_data})
        data_response.update({"gNBs_List":gNBs_List})
    Response_gNB_Information(data_response)
    print(data_response)
    return jsonify(data_response)

"""
Functions of APIs to UE Access
1.RRCSetupRequest
"""
#Setp(1) Get RRCSetupRequest from UE and 1.to CU 2.Response to UE
@app.route("/RRCSetupRequest", methods=['POST'])
def RRCSetupRequest():
    logging.info("Enable: gNB["+gNB_IP+"] Function:RRCSetupRequest")
    request_data=request.get_json()

    UE_Name=request_data['UE_Name']
    # response_data=INITIAL_UL_RRC_MESSAGE_TRANSFER(request_data)
    # Update_gNB_UEs_Configuration(UE_Name,{"gNB_DU_UE_F1AP_ID":response_data["gNB_DU_UE_F1AP_ID"]})
    # Update_gNB_UEs_Configuration(UE_Name,{"gNB_CU_UE_F1AP_ID":response_data["gNB_CU_UE_F1AP_ID"]})

    return jsonify({"RRC":"RRCSetUp"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)

