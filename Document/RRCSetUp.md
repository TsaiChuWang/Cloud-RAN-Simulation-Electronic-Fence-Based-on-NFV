# RRCSetUp for MUltiple gNBs System

![RRCSetUp Flow Chart](img/RRCSetUp.png)

>[See ETSI TS 138 331 V16.3.1 (2021-01) 5G NR Radio Resource Control (RRC) Protocol specification (3GPP TS 38.331 version 16.3.1 Release 16)](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/16.03.01_60/ts_138331v160301p.pdf)

Generally speaking, there will be two results in this stage: RRCSetUp and RRCReject, but it is certain that RRCReject will be returned in the DU, and the exceptions to the subsequent F1AP agreement will be written Not applicable. (Not applicable). According to this theorem, We simulate this process and try to comply with the 3GPP TS, because this is the first step to access the core network, and the signaling is SRB0 at this time.

## Iinitalization

When the UE is in RRC_IDLE and has acquired the necessary system information, the UE initiates this process when the upper layer requests to establish an RRC connection.

In the system, we set a parameter called "RRC". It indicates the RRC status of the UE, like it is real in our life. For some Samsung mobile phones, you can enter `*#0011#`  in the mobile phone to get some signal information. We use *Samsung Glaxy A53* mobile phone with 5G solution to check the RRC status as follows

![RRC STATUS](img/RRCSTATUS.png)

It should be noted that LTE did not originally have the RRC_INACTIVE state. It was introduced after the R13 specification of 5G in order to reduce signaling and power consumption, because 5G technology will generate a lot of power consumption, and RRC is hobby in the case of high speed. The key to electricity, a large number of devices transmitting a small amount of data will generate excessive signaling consumption.

In a word, in the RRC_IDLE state (idle state), initialization will be performed, and then the UE will send the RRCSetupRequest through the Common Control Channel (hereinafter referred to as CCCH) channel.

The following is the flow chart of the Initiation, the gray indicates that the system has not implemented it or will keep it.

![RRC_INITALIZATION](img/RRCINITIAL.png)

In the Single gNB System, we will simulate the high physical layer of the main control UE, but based on NFV technology, we will focus on the content of the protocol, the focus here is to configure the part of CCCH and protocol 5.3. 14 content, strictly enforce the simulation. In the Multiple gNBs System, we will focus on CellGroupConfiguration, because here we need to configure the UE's MCG and SCG, here we do not consider SPCell.
Pay attention to the number at the back, you can use it to compare the content of the agreement, and our attachment here also mentions the part.

### Apply the CCCH configuration

#### **Parameters**

| Name | Value | Semantics description |
| :--: | :--:  | :--: |
| SDAP configuration | NOTUSED | - |
| PDCP configuration | NOTUSED | - |
| RLC configuration | TM | - |
| Logical channel configuration | - | - |
| >priority | 1 | Highest priority |
| >prioritisedBitRate | INFINITY | - |
| >bucketSizeDuration | ms1000  | - |
| >logicalChannelGroup | 0 | - |

Single LOS CCCH configuration part code

![Single LOS CCCH configuration part code](img/CCCHConfigurationCode.png)

For configuration, refer to Chunghwa Telecom and general agreement content.

### Apply the default MAC Cell Group configuration

#### **Parameter**

| Name | Value | Semantics description |
| :--: | :--:  | :--: |
| MAC Cell Group configuration | - | - |
| bsr-Config  | - | - |
| >periodicBSR-Timer  | sf10 | - |
| >retxBSR-Timer  | sf80 | - |
| phr-Config  | - | - |
| >phr-PeriodicTimer  | sf10 | - |
| >phr-ProhibitTimer  | sf10  | - |
| >phr-Tx-PowerFactorChange | dB1 | - |

In the Single gNB System, we do not pay attention to this part, because for a system simulated by a base station, there will not be more than one base station, and the CellGroup is ignored, but it is still symbolic in our setting The existence of multiple simulators may also be configured in a system. We try to retain these dynamic configurations without affecting performance. They are independent files in the system and are flexible in design.

However, in the Multiple gNBs System, its meaning is different. For cells that are divided into different groups (referred to as gNBs here), the gNBs to be accessed may be different, and the configurations of the MCG and SCG are different. Here we will first set a primary access PCell, and then let RRCSetUp return the new MCG configuration after access.

## ***RRCSetupRequest (RRC Protocal)***

>[See ETSI TS 138 331 V16.3.1 (2021-01) 5G NR Radio Resource Control (RRC) Protocol specification (3GPP TS 38.331 version 16.3.1 Release 16)(5.3.3)](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/16.03.01_60/ts_138331v160301p.pdf)

Purpose: Request to establish an RRC connection. 
Carrying message: UE identity, RRC connection establishment reason
Here, if the upper layer carries 5G-S-TMSI, UE_Identity shall return ng-5G-S-TMSI-Part1, otherwise, a 32-bit identifier shall be randomly generated (unique in this Cell).

![UE Identity Flow Chart](img/5G_S_TMSI.png)

As shown in the table below, the parameter table will be represented by three values: Name is the IE name, Value is the default value (usually the main UE configured in the Single gNB LOS Uma), and Characteristic represents the generation method of the configuration in the system.
**Parameter**
| Name | Value | Characteristic |
| :--: | :--:  | :--: |
| UE_Identity | | Dynamic/Allocated |
| establishmentCause | mo-Signalling | Static  |
| UE_Name | UE_A | in UE Configuration |
| UE_IP | 10.0.2.100 | in UE Configuration |

bearer signaling:SRB0
logical channel:CCCH

See Actions related to transmission of RRCSetupRequest message [5.3.3.3] page 55

## ***INITIAL UL RRC MESSAGE TRANSFER(F1AP)***

>[See ETSI TS 138 331 V16.3.1 (2021-01) 5G NR Radio Resource Control (RRC) Protocol specification (3GPP TS 38.331 version 16.3.1 Release 16)(8.4.1)](https://www.etsi.org/deliver/etsi_ts/138300_138399/138331/16.03.01_60/ts_138331v160301p.pdf)

See Initial UL RRC Message Transfer  [8.4.1] page 58

### General

The purpose of the Initial UL RRC Message Transfer procedure is to transfer the initial RRC message to the gNB-CU.
The procedure uses non-UE-associated signaling.

### Successful operation 

The establishment of the UE-associated logical F1-connection shall be initiated as part of the procedure.

![Successful operation](img/INITIALULRRCMESSAGETRANSFERSUCCESSOPERATION.png)

If the DU to CU RRC Container IE is not included in the INITIAL UL RRC MESSAGE TRANSFER, the gNB-CU should reject the UE under the assumption that the gNB-DU is not able to serve such UE.

 If the gNB-DU is able to serve the UE, the gNB-DU shall include the DU to CU RRC Container IE and the gNB-CU shall configure the UE as specified in TS 38.331 [8].

 The gNB-DU shall not include the ReconfigurationWithSync field in the CellGroupConfig IE as defined in TS 38.331 [8] of the DU to CU RRC Container IE.

If the SUL Access Indication IE is included in the INITIAL UL RRC MESSAGE TRANSFER, the gNB-CU shall consider that the UE has performed access on SUL carrier.
(Not implemented in the system)

If the RRC-Container-RRCSetupComplete IE is included in the INITIAL UL RRC MESSAGE TRANSFER, the gNBCU shall take it into account as specified in TS 38.401 [4].

Send the first RRC message to the gNB-CU
This process will establish a UE-level F1 connection

**Parameter**

| Name | Value | Characteristic |
| :--: | :--:  | :--: |
| UE_Name | UE_Name | Dynamic form request |
| UE_IP | UE_IP | Dynamic form request |
| gNB_DU_UE_F1AP_ID | | Allocate/Request |
| NR CGI | | in Config |
| >PLMN | 46692 | in Config |
| >>MCC | 466 | in Config |
| >>MNC | 92 | in Config |
| >NR cell Identity | | in Config |
| >>gNB Identity | 1010010111000101010010 | in Config |
| >>Cell Identity | 1111001000000 | in Config |
| C-RNTI | | Allocate |
| RRC-Container| RRCSetupRequest | Static |
| DU to CU RRC Container | include CellGroupConfig | in Config |
| SUL Access Indication | True | Static |
| Transaction ID | | Allocate |

#### gNB-DU UE F1AP ID

The gNB-DU UE F1AP ID uniquely identifies the UE association over the F1 interface within the gNB-DU.
INTEGER(0,232-1)

#### C-RNTI 

Cell RNTI(Radio Network Temporary Identity)
INTEGER(0..65535, ...)

It is related to the cause and status of the UE access request. It is the most used RNTI. C-RNTI is not available at the beginning, but is allocated by the base station to the users who have successfully joined the network after the user accesses the network. If the UE is in the RRC_CONNECTED mode, it means that the C-RNTI has been allocated and needs to be reported when accessing; if the UE is in the IDLE mode, it means that there is no C-RNTI yet. Allocate a C-RNTI; when the user is handed over, the user can bring the C-RNTI allocated by this cell to the next cell, and there is no need to re-allocate the C-RNTI.

#### Transaction ID

The Transaction ID IE uniquely identifies a procedure among all ongoing parallel procedures of the same type initiated by the same protocol peer. Messages belonging to the same procedure use the same Transaction ID. 
INTEGER (0..255, ...)
The Transaction ID is determined by the initiating peer of a procedure.

![Flow Chart of INITIAL_UL_RRC_MESSAGE_TRANSFER](img/INITIAL_UL_RRC_MESSAGE_TRANSFER.png)

#### NR CGI

[Picture from 5G NR Cell Global Identity (NCGI) Planning and Calculations](https://www.techplayon.com/5g-nr-cell-global-identity-planning/)

![Picture from <https://www.techplayon.com/5g-nr-cell-global-identity-planning/>](img/NR_CGI.png)

These parameters will be set in UE Configuration, which are adjustable configuration parameters. Let’s talk about PLMN first, which is composed of mobile device country code (MCC) and mobile device network code (MNC). We set it to 466 92 according to the actual mobile phone settings. , but in addition to the mobile phone instructions, we can go through this website [Mobile country code](https://en.wikipedia.org/wiki/%E7%A7%BB%E5%8A%A8%E8%AE%BE%E5%A4%87%E7%BD%91%E7%BB%9C%E4%BB%A3%E7%A0%81) 
To check the corresponding code, Chunghwa Telecom is 466 92, Far EasTone is 466 03/01.

In addition, the UE Configuration is set with bitlength gNB ID and bitlength Cell ID. Currently, it is set to 22/14. When registering the gNB, it will dynamically assign a unique identification code to the designated area, and specify the bit length format through the bitlength gNB ID and bitlength Cell ID.