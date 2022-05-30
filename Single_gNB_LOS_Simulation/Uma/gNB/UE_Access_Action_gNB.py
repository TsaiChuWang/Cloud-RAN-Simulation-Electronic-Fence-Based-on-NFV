#!flask/bin/python
from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json

app = Flask(__name__)
PORT = 1440
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/UE_Access_Action_gNB.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)

import random
import datetime
ISOTIMEFORMAT = '%Y/%m/%d,%H:%M:%S'
import requests

#Initialize Public Parameter
gNB_Name=""
gNB_IP=""

with open('./config/gNB.json') as gNB_Config_file:
    gNB_Config = json.load(gNB_Config_file)
    gNB_Name=gNB_Config['gNB_Name']
    gNB_IP=gNB_Config['gNB_IP']

    gNB_Config_file.close()

eNodeB_Admission_Control=False

antenna_Power=0
center_Frequency=0
CU_Distibuted_SRB_ID=-1

"""
Functions of Configuration(Obtain/Update/Allocate)
1.gNB_DU_UE_F1AP_ID
2.gNBConfig
3.RNTI
"""

#Obtain Specified gNB_DU_UE_F1AP_ID to UE_Name
def Obtain_gNB_DU_UE_F1AP_ID(UE_Name):
    gNB_DU_UE_F1AP_ID=""
    with open('./config/gNB_DU_UE_F1AP_ID.json') as gNB_DU_UE_F1AP_ID_file:
        gNB_DU_UE_F1AP_ID_Config = json.load(gNB_DU_UE_F1AP_ID_file)
        gNB_DU_UE_F1AP_ID=gNB_DU_UE_F1AP_ID_Config[UE_Name]
        gNB_DU_UE_F1AP_ID_file.close()
    
    if(gNB_DU_UE_F1AP_ID==""):
        print("Allocate gNB_DU_UE_F1AP_ID to "+UE_Name)
        logging.warning("Allocate gNB_DU_UE_F1AP_ID to "+UE_Name)
        ID=random.randint(0,(2**32))
        gNB_DU_UE_F1AP_ID="{0:b}".format(ID)
        Update_gNB_DU_UE_F1AP_ID({UE_Name:gNB_DU_UE_F1AP_ID})

    return gNB_DU_UE_F1AP_ID

#Update Specified gNB_DU_UE_F1AP_ID to UE_Name
def Update_gNB_DU_UE_F1AP_ID(dict_new):
    gNB_DU_UE_F1AP_ID=""
    with open('./config/gNB_DU_UE_F1AP_ID.json', 'r') as gNB_DU_UE_F1AP_ID_file:
        gNB_DU_UE_F1AP_ID = json.load(gNB_DU_UE_F1AP_ID_file)
        gNB_DU_UE_F1AP_ID_file.close()

    with open('./config/gNB_DU_UE_F1AP_ID.json', 'w') as gNB_DU_UE_F1AP_ID_file:
        gNB_DU_UE_F1AP_ID.update(dict_new)
        json.dump(gNB_DU_UE_F1AP_ID, gNB_DU_UE_F1AP_ID_file, ensure_ascii=False)
        gNB_DU_UE_F1AP_ID_file.close()

#Obtain gNB Coniguration Parameters
def Obtain_gNBConfig_Parameters(key):
    gNB_Config={}
    with open('./config/gNB.json') as gNB_Config_file:
        gNB_Config = json.load(gNB_Config_file)
        gNB_Config_file.close()
    return  gNB_Config[key]

#Obtain Specified C_RNTI to UE_Name
def Obtain_C_RNTI(UE_Name):
    C_RNTI=""
    C_RNTI_Config={}
    with open('./config/C_RNTI.json') as C_RNTI_file:
        C_RNTI_Config = json.load(C_RNTI_file)
        C_RNTI=C_RNTI_Config[UE_Name]
        C_RNTI_file.close()

    if(C_RNTI==""):
        with open('./config/C_RNTI.json', 'w') as C_RNTI_file:
            print("Allocate C_RNTI to "+UE_Name)
            logging.warning("Allocate C_RNTI to "+UE_Name)
            ID=random.randint(0,(2**16))
            C_RNTI="{0:b}".format(ID)
            C_RNTI_Config.update({UE_Name:C_RNTI})
            json.dump(C_RNTI_Config, C_RNTI_file, ensure_ascii=False)
            C_RNTI_file.close()

    return C_RNTI


def Obtain_gNB_CU_UE_F1AP_ID(UE_Name):
    gNB_CU_UE_F1AP_ID=""
    with open('./config/gNB_CU_UE_F1AP_ID.json', 'r') as gNB_CU_UE_F1AP_ID_file:
        gNB_CU_UE_F1AP_ID = json.load(gNB_CU_UE_F1AP_ID_file)[UE_Name]
        gNB_CU_UE_F1AP_ID_file.close()
    return gNB_CU_UE_F1AP_ID
    
def Updatge_gNB_CU_UE_F1AP_ID(dict_new):
    gNB_CU_UE_F1AP_ID=""
    with open('./config/gNB_CU_UE_F1AP_ID.json', 'r') as gNB_CU_UE_F1AP_ID_file:
        gNB_CU_UE_F1AP_ID = json.load(gNB_CU_UE_F1AP_ID_file)
        gNB_CU_UE_F1AP_ID_file.close()

    with open('./config/gNB_CU_UE_F1AP_ID.json', 'w') as gNB_CU_UE_F1AP_ID_file:
        gNB_CU_UE_F1AP_ID.update(dict_new)
        json.dump(gNB_CU_UE_F1AP_ID, gNB_CU_UE_F1AP_ID_file, ensure_ascii=False)
        gNB_CU_UE_F1AP_ID_file.close()

def Obtain_DU_to_CU_RRC_Information():
    DU_to_CU_RRC_Information={}
    with open('./config/DU_to_CU_RRC_Information.json', 'r') as DU_to_CU_RRC_Information_file:
        DU_to_CU_RRC_Information = json.load(DU_to_CU_RRC_Information_file)
        DU_to_CU_RRC_Information_file.close()
    return DU_to_CU_RRC_Information

"""
Functions of response data to UE
1.RRCSetup
"""

#The RRCSetup message is used to establish SRB1
def RRCSetup(UE_Name):
    SRB_ID=1
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCSetup")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCSetup")

    masterCellGroup={
        "ReconfigurationWithSync":True,
        "Rlc_BearerToReleaseList":["00000"],
        "Rlc_BearerToAddModList":[],
        "PhysicalCellGroupConfig":{
            "harq_ACK_SpatialBundlingPUCCH":True,
            "harq_ACK_SpatialBundlingPUSCH":True,
            "p_NR":16,
            "pdsch_HARQ_ACK_Codebook":"dynamic",
            "tpc_SRS_RNTI": Obtain_C_RNTI(UE_Name),
            "tpc_PUCCH_RNTI": Obtain_C_RNTI(UE_Name),
            "tpc_PUSCH_RNTI": Obtain_C_RNTI(UE_Name),
            "sp_CSI_RNTI": Obtain_C_RNTI(UE_Name),
            "cs_RNTI": Obtain_C_RNTI(UE_Name),
        },
        "Mac_CellGroupConfig":{
            "DRX_Config":{
                "DRX_onDurationTimer":"ms20",
                "DRX_nactivityTimer":"ms20",
                "DRX_HARQ_RTT_TimerDL": 36,
                "DRX_HARQ_RTT_TimerUL": 18,
                "DRX_RetransmissionTimerDL":"sl0",
                "DRX_RetransmissionTimerUL":"sl0",
                "DRX_LongCycleStartOffset":17,
                "shortDRX":{
                    "DRX_ShortCycle":"ms20",
                    "DRX_ShortCycleTimer":8
                },
                "DRX_SlotOffset":24
            },
            "SchedulingRequestConfig":{
                "schedulingRequestToAddModList":[],
                "schedulingRequestToReleaseList":[]
            },
            "BSR_Config":{
                "periodicBSR_Timer":"sf20",
                "retxBSR_Timer":"sf40",
                "logicalChannelSR_DelayTimer":"sf64"
            },
            "TAG_Config":{
                "Tag_ToReleaseList":[],
                "Tag_ToAddModList":[]
            },
            "PHR_Config":{
                "phr_PeriodicTimer":"sf10",
                "phr_ProhibitTimer":"sf0",
                "phr_Tx_PowerFactorChange":"dB1",
                "multiplePHR":True,
                "phr_Type2PCell":True,
                "phr_Type2OtherCell ":False,
                "phr_ModeOtherCG":"virtual"
            },
            "skipUplinkTxDynamic":True,
            "CS_RNTI":Obtain_C_RNTI(UE_Name)
        },
        "spCellConfig":{
            "servCellIndex":0,
            "reconfigurationWithSync":True,
            "rlf_TimersAndConstants":{},
            "rlmInSyncOutOfSyncThreshold":0,
            "spCellConfigDedicated":{
                "tdd_UL_DL_ConfigurationDedicated":{
                    "slotSpecificConfigurationsToAddModList":[],
                    "slotSpecificConfigurationsToreleaseList":[20]
                },
                "InitialDownlinkBWP":{
                    "pdcch_Config":{
                        "controlResourceSetToAddModList":[{"ControlResourceSet"}],
                        "controlResourceSetToReleaseList":["ControlResourceSetId"],
                        "searchSpacesToAddModList":["SearchSpace"],
                        "searchSpacesToReleaseList":["SearchSpaceId"],
                        "DownlinkPreemption":{},
                        "slotFormatIndicator":{ "SlotFormatIndicator" },  
                        "tpc_PUSCH":{},
                        "tpc-PUCCH":{}
                    },
                    "pdsch_Config":{"Too Many"},
                    "sps_Config":{},
                    "radioLinkMonitoringConfig":{ "RadioLinkMonitoringConfig" }
                },
                "downlinkBWP_ToReleaseList":[],
                "downlinkBWP_ToAddModList":[],
                #somthing
            }
        }
    }
    RRCSetup_Data={
        "gNB_IP":gNB_IP,
        "gNB_Name":gNB_Name,
        "PLMN":Obtain_gNBConfig_Parameters("PLMN"),
        "CellGroupId":gNB_IP,
        "rlc_BearerToAddModList":[],
        "rlc_BearerToReleaseList":[],
        "radioBearerConfig":{
            "srb_ToAddModList":{
                "SRB_ID":SRB_ID,
                "reestablishPDCP_ENUMERATED":True,
                "discardOnPDCP":True
            },
            "srb3_ToRelease_ENUMERATED":True
        },
        "masterCellGroup":{
            "mac-CellGroupConfig":{},
            "PhysicalCellGroupConfig":{
                "harq_ACK_SpatialBundlingPUCCH":True,
                "pdsch_HARQ_ACK_Codebook": "semiStatic",
                "tpc_SRS_RNTI_RNTI_Value": 0,
                "tpc_PUCCH_RNTI_RNTI_Value":0,
                "sp_CSI_RNTI_RNTI_Value":0,
                "cs_RNTI_SetupRelease":0
            },
            "spCellConfig":{}
        },
        "RRCSetup":"RRCReestablishmentRequest"
    }
    return RRCSetup_Data

"""
Functions of response to CU-CP
1.INITIAL_UL_RRC_MESSAGE_TRANSFER

"""

#Transform RRCSetUpRequest
def INITIAL_UL_RRC_MESSAGE_TRANSFER(UE_Name):
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:INITIAL_UL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:INITIAL_UL_RRC_MESSAGE_TRANSFER")
    payload={
        "Message_Type":{
            "Procedure_Code":"10010010",
            "Message_Type":"Initiating_Message"
        },
        "gNB_Name":gNB_Name,
        "UE_Name":UE_Name,
        "gNB_DU_UE_F1AP_ID":Obtain_gNB_DU_UE_F1AP_ID(UE_Name),
        "NR_CGI":Obtain_gNBConfig_Parameters("NR_CGI"),
        "C_RNTI":Obtain_C_RNTI(UE_Name),
        "RRC_Container":"RRCSetupRequest",
        "Transaction_ID":Obtain_gNBConfig_Parameters("Transaction_ID"),
        "SUL_Access_Indication":True
    }

    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1440/INITIAL_UL_RRC_MESSAGE_TRANSFER"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

    Updatge_gNB_CU_UE_F1AP_ID({UE_Name:json.loads(response.text)['gNB_CU_UE_F1AP_ID']})
    return json.loads(response.text)

def SecurityAlgorithmConfig():
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:SecurityAlgorithmConfig")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:SecurityAlgorithmConfig")
    SecurityAlgorithmConfig={}
    with open('./config/SecurityAlgorithmConfig.json', 'r') as SecurityAlgorithmConfig_file:
        SecurityAlgorithmConfig = json.load(SecurityAlgorithmConfig_file)
        SecurityAlgorithmConfig_file.close()
    return SecurityAlgorithmConfig

def UL_RRC_MESSAGE_TRANSFER(CU_Distibuted_SRB_ID,UE_Name,UE_IP,RegisteredAMF):
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER")
    payload={
        "gNB_Name":gNB_Name,
        "gNB_IP":gNB_IP,
        "UE_Name":UE_Name,
        "UE_IP":UE_IP,
        "CU_Distibuted_SRB_ID":CU_Distibuted_SRB_ID,
        "gNB_DU_UE_F1AP_ID":Obtain_gNB_DU_UE_F1AP_ID(UE_Name),
        "gNB_CU_UE_F1AP_ID":Obtain_gNB_CU_UE_F1AP_ID(UE_Name),
        "RRC-Container":"RRC_CONNECTION_SETUP_COMPLETE",
        "RegisteredAMF":RegisteredAMF
    }
    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1440/UL_RRC_MESSAGE_TRANSFER"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return json.loads(response.text),SecurityAlgorithmConfig()

def UE_CONTEXT_SETUP_RESPONSE(UE_Name,SetUpList):
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER")
    payload={
        "gNB_Name":gNB_Name,
        "gNB_IP":gNB_IP,
        "gNB_DU_UE_F1AP_ID":Obtain_gNB_DU_UE_F1AP_ID(UE_Name),
        "gNB_CU_UE_F1AP_ID":Obtain_gNB_CU_UE_F1AP_ID(UE_Name),
        "DU_to_CU_RRC_Information":Obtain_DU_to_CU_RRC_Information(),
        "C_RNTI":Obtain_C_RNTI(UE_Name),
        "Resource_Coordination_Transfer_Container":"Resource_Coordination_Transfer_Container",
        "Full_Configuration":{},
        "DRB_Setup_List":SetUpList['DRB to Be Setup List'],
        "DRB_Failed_to_Setup_List":[],
        "SRB_Setup_List":SetUpList['SRB to Be Setup List'],
        "SCell_Failed_To_Setup_List":[],
        "Inactivity_Monitoring":"Support"
    }
    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1440/UE_CONTEXT_SETUP_RESPONSE"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete(request_data):
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete")
    payload={
        "gNB_Name":gNB_Name,
        "gNB_IP":gNB_IP
    }
    payload.update(request_data)
    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1440/UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    # print(response.status)
    return json.loads(response.text)

def UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete(request_data):
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete")
    payload={
        "gNB_Name":gNB_Name,
        "gNB_IP":gNB_IP
    }
    payload.update(request_data)
    url = "http://"+Obtain_gNBConfig_Parameters("CU_IP")+":1440/UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete"
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    # print(response.status)
    return json.loads(response.text)

#Get RRCSetupRequest from UE in RRC Protocal
@app.route("/RRCSetupRequest", methods=['POST'])
def RRCSetupRequest():
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCSetupRequest")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCSetupRequest")

    request_data=request.get_json()
    logging.info(gNB_Name+"["+gNB_IP+"] Getting RRCSetupRequest from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    print(gNB_Name+"["+gNB_IP+"] Getting RRCSetupRequest from "+request_data['UE_Name']+"["+request_data['UE_IP']+"] with UE_Identity:"+request_data['UE_Identity'])
    
    CU_Message_DL_RRC_MESSAGE_TRANSFER=INITIAL_UL_RRC_MESSAGE_TRANSFER(request_data['UE_Name'])
    SRB_ID=CU_Message_DL_RRC_MESSAGE_TRANSFER['SRB_ID']

    if(SRB_ID==-1):
        return jsonify({"RRCSetup":" RRCReject"})

    print(request_data)
    return jsonify(RRCSetup(request_data['UE_Name']))

@app.route("/RRC_CONNECTION_SETUP_COMPLETE", methods=['POST'])
def RRC_CONNECTION_SETUP_COMPLETE():
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRC_CONNECTION_SETUP_COMPLETE")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRC_CONNECTION_SETUP_COMPLETE")
    request_data=request.get_json()
    logging.info(gNB_Name+"["+gNB_IP+"] Getting RRC_CONNECTION_SETUP_COMPLETE from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    print(gNB_Name+"["+gNB_IP+"] Getting RRC_CONNECTION_SETUP_COMPLETE from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    print(request_data)
    parameters,response_data=UL_RRC_MESSAGE_TRANSFER(request_data['CU_Distibuted_SRB_ID'],request_data['UE_Name'],request_data['UE_IP'],request_data['RegisteredAMF'])
    UE_CONTEXT_SETUP_RESPONSE(request_data['UE_Name'],parameters)
    return jsonify(response_data)

@app.route("/SecurityModeComplete", methods=['POST'])
def SecurityModeComplete():
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:SecurityModeComplete")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:SecurityModeComplete")
    request_data=request.get_json()
    logging.info(gNB_Name+"["+gNB_IP+"] Getting RRC_CONNECTION_SETUP_COMPLETE from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    print(gNB_Name+"["+gNB_IP+"] Getting RRC_CONNECTION_SETUP_COMPLETE from "+request_data['UE_Name']+"["+request_data['UE_IP']+"]")
    if(request_data['SecurityModeComplete']=='ON'):
        print(request_data['UE_Name']+" SecurityModeComplete")
        logging.info(request_data['UE_Name']+" SecurityModeComplete")
        response=UL_RRC_MESSAGE_TRANSFER_SecurityModeComplete(request_data)
        return jsonify(response)
    else:
        print(request_data['UE_Name']+" SecurityMode Failed")
        logging.info(request_data['UE_Name']+" SecurityMode Failed")
        return jsonify({"SecurityModeComplete":"Failed"})
    print(request_data)
    # return jsonify({})

@app.route("/RRCReconfigurationComplete", methods=['POST'])
def RRCReconfigurationComplete():
    print("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCReconfigurationComplete")
    logging.info("Enable: gNB["+gNB_IP+"] UE_Access_Action_gNB.py Function:RRCReconfigurationComplete")
    request_data=request.get_json()
    print(request_data)
    data={"msg":"RRCReconfigurationComplete"}
    data.update(request_data)
    UL_RRC_MESSAGE_TRANSFER_RRCReconfigurationComplete(request_data)
    return jsonify(data)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)