import requests
import json
import numpy
import time

def Obtain_UEConfig_Parameters(key):
    UE_Config={}
    with open('./config/UE.json', 'r') as UE_Config_file:
        UE_Config = json.load(UE_Config_file)
        UE_Config_file.close()
    return UE_Config[key]
    
def UEConfig_Update(dict_new):
    UEConfig={}
    with open('./config/UE.json', 'r') as UEConfig_file:
        UEConfig = json.load(UEConfig_file)
        UEConfig_file.close()

    with open('./config/UE.json', 'w') as UEConfig_file:
        UEConfig.update(dict_new)
        json.dump(UEConfig, UEConfig_file, ensure_ascii=False)
        UEConfig_file.close()

def RRCSetup_Config_Update(dict_new):
    RRCSetup_Config={}
    with open('./config/RRCSetup_Config.json', 'r') as RRCSetup_Config_file:
        RRCSetup_Config = json.load(RRCSetup_Config_file)
        RRCSetup_Config_file.close()

    with open('./config/RRCSetup_Config.json', 'w') as RRCSetup_Config_file:
        RRCSetup_Config.update(dict_new)
        json.dump(RRCSetup_Config, RRCSetup_Config_file, ensure_ascii=False)
        RRCSetup_Config_file.close()

def Obtain_RRCSetup_Config(key):
    RRCSetup_Config={}
    with open('./config/RRCSetup_Config.json', 'r') as RRCSetup_Config_file:
        RRCSetup_Config = json.load(RRCSetup_Config_file)
        RRCSetup_Config_file.close()
    return RRCSetup_Config[key]

def CLOSE_TIMER_RRCSetUP(TIMER):
    if(Obtain_RRCSetup_Config(TIMER)=='RUN'):
        print("CLOSE THE TIMER "+TIMER+".")
        RRCSetup_Config_Update({"T380":"STOP"})
    else:
        print("THE TIMER "+TIMER+" ON CLOSE.")

def RRCReestablishmentRequest():
    RRCSetup_Config={}
    CLOSE_TIMER_RRCSetUP("T380")
    CLOSE_TIMER_RRCSetUP("T390")
    CLOSE_TIMER_RRCSetUP("T300")
    CLOSE_TIMER_RRCSetUP("T301")
    CLOSE_TIMER_RRCSetUP("T319")
    CLOSE_TIMER_RRCSetUP("T320")
    CLOSE_TIMER_RRCSetUP("T302")
    return RRCSetup_Config

def RRCSetupRequest_client():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Access_Action_UE.py Function:RRCSetupRequest_client")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1440/RRCSetupRequest"

    payload={
        "UE_Name": Obtain_UEConfig_Parameters("UE_Name"),
        "UE_IP": Obtain_UEConfig_Parameters("UE_IP"),
        "UE_MAC": Obtain_UEConfig_Parameters("UE_MAC"),

        "5G-S-TMSI":  Obtain_UEConfig_Parameters("5G-S-TMSI"),
        "UE_Identity":Obtain_UEConfig_Parameters("UE_Identity"),
        "establishmentCause":"mo-Signalling"
    }

    if(Obtain_UEConfig_Parameters("5G-S-TMSI")==""):
        print("The Upper Level provides not 5G-S-TMSI:UE_Identity is a random value.")
        print("UE_Identity: "+payload['UE_Identity'])
    else:
        print("The Upper Level provides 5G-S-TMSI:UE_Identity is ng-5G-S-TMSI-Part1.")
        payload['UE_Identity']=Obtain_UEConfig_Parameters("ng-5G-S-TMSI-Part1")
        print("UE_Identity: "+payload['UE_Identity'])
        
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print("This point is keep")
    print(response.text)
    #RRCSetup_Config_Update({"CU_Distibuted_SRB_ID":json.loads(response.text)['radioBearerConfig']['srb_ToAddModList']['SRB_ID']})
    if(json.loads(response.text)['RRCSetup']=="RRCReestablishmentRequest"):
        print("RRCSetup:RRCReestablishmentRequest")
        RRCSetup_Config_Update({"RRC_CONNECTED":True})
        RRCSetup_Config_Update({"PCell":json.loads(response.text)['gNB_IP']})
        print("Current PCell: "+Obtain_RRCSetup_Config("PCell"))
        RRCReestablishmentRequest()
        if(Obtain_UEConfig_Parameters("5G-S-TMSI")==""):
            print("The Upper Level provides not 5G-S-TMSI:set the ng-5G-S-TMSI-Value to ng-5G-S-TMSI.")
            UEConfig_Update({"5G-S-TMSI":Obtain_UEConfig_Parameters("ng-5G-S-TMSI-Value")})
        else:
            print("The Upper Level provides 5G-S-TMSI:set the ng-5G-S-TMSI-Value to ng-5G-S-TMSI-Part2.")
            UEConfig_Update({"5G-S-TMSI":Obtain_UEConfig_Parameters("ng-5G-S-TMSI-Part2")})

        PLMN_IdentityList=Obtain_RRCSetup_Config("PLMN-IdentityList")
        PLMN_IdentityList.append(json.loads(response.text)['PLMN'])
        PLMN_IdentityList=list(set((PLMN_IdentityList)))
        RRCSetup_Config_Update({"PLMN-IdentityList":PLMN_IdentityList})
        print("PLMN-IdentityList Update Complete")
    else:
        print("RRCSetup:RRCReject")
        RRCSetup_Config_Update({"RRC_CONNECTED":False})
        print("RRC_CONNECTED CLOSE")
        print("RESTART RRCSetupRequest_client")
        print()

def RRC_CONNECTION_SETUP_COMPLETE_client():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Access_Action_UE.py Function:RRC_CONNECTION_SETUP_COMPLETE_client")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1440/RRC_CONNECTION_SETUP_COMPLETE"
    payload={
        "UE_Name":Obtain_UEConfig_Parameters("UE_Name"),
        "UE_IP":Obtain_UEConfig_Parameters("UE_IP"),
        "selectedPLMN_Identity_Index":len(list(Obtain_RRCSetup_Config('PLMN-IdentityList')))-1,
        "RegisteredAMF":Obtain_RRCSetup_Config("RegisteredAMF"),
        "Guami_Type":"mapped",
        "s_NSSAI_List":Obtain_RRCSetup_Config("s_NSSAI_List"),
        "DedicatedNAS_Message":"Service_Request",
        "ng-5G-S-TMSI-Value":Obtain_UEConfig_Parameters("ng-5G-S-TMSI-Value"),
        "CU_Distibuted_SRB_ID":Obtain_RRCSetup_Config("CU_Distibuted_SRB_ID")
    }
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    if(json.loads(response.text)['cipheringAlgorithm']==""):
        print("SecurityMode Set UP Failed")
        UEConfig_Update({"SecurityMode_Set_UP":False})
    else:
        print("SecurityMode Set UP Success")
        UEConfig_Update({"SecurityMode_Set_UP":True})

def SecurityModeComplete():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Access_Action_UE.py Function:SecurityModeComplete")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1440/SecurityModeComplete"
    payload={
        "UE_Name":Obtain_UEConfig_Parameters("UE_Name"),
        "UE_IP":Obtain_UEConfig_Parameters("UE_IP"),
        "SecurityModeComplete":"ON",
        "Cause":""
    }
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    RRCReconfiguration=json.loads(response.text)['RRCReconfiguration']
    UEConfig_Update({"RRCReconfiguration":RRCReconfiguration})
    print(response.text)

def RRCReconfigurationComplete():
    print("Enable: UE["+Obtain_UEConfig_Parameters("UE_IP")+"] UE_Access_Action_UE.py Function:SecurityModeComplete")
    url = "http://"+Obtain_UEConfig_Parameters("Connected_gNB_IP")+":1440/RRCReconfigurationComplete"
    payload={
        "UE_Name":Obtain_UEConfig_Parameters("UE_Name"),
        "UE_IP":Obtain_UEConfig_Parameters("UE_IP"),
        "Attach_Accept":True,
        "Activate_default_EPS_bearer_context_request":"Accepted"
    }
    payload=json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def FINISH_CLEAN():
    RRCSetup_Config_Update({"RRC_CONNECTED": False})
    UEConfig_Update({"SecurityMode_Set_UP":False})


while (not Obtain_RRCSetup_Config("RRC_CONNECTED")):
    RRCSetupRequest_client()
    time.sleep(0.1)

while (not Obtain_UEConfig_Parameters("SecurityMode_Set_UP")):
    RRC_CONNECTION_SETUP_COMPLETE_client()
    time.sleep(0.1)

SecurityModeComplete()
RRCReconfigurationComplete()
FINISH_CLEAN()
