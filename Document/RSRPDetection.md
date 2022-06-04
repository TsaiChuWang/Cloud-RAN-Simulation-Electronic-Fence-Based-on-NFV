# **RSRP Detection System**

## ***Single gNB System***

These are LOS Uma Model  Flow Chart in Single gNB System and Multiple gNB System

![Single gNB System](img/RSRP_Detection_SIngle_gNB.png)

The UE requests information from the gNB. You can think of it as in real life, the UE requests the gNB. In the system, we will obtain the gNB data and obtain the parameters used to calculate the RSRP, because in fact, the RSRP is received by the received parameters, which are fed back to the gNB by the UE

This is the flow chart of the calculation of Pathloss at the beginning. Because the Pathloss model is divided into two parts according to the distance, it is very important to calculate the breakpoint and establish a suitable model for the distance range. It should be noted that the center frequency of our parameter is set in MHz The unit needs to be multiplied by one million. At the beginning, it was stuck here for a long time, because it was divided by the speed of light (the document stated that it was 3*10 to the 8th power), but that was the interruption point. If you want to calculate Pathloss needs to be divided by one thousand and calculated in GHz.

However, calculating the interruption point all the time will slow down the efficiency. In the main UE, it is especially important to pay attention to this: the immediacy of user control, our system field setting is (-800,800) This setting can be dynamically set, but this means that Within this range, the furthest distance between two points is $\ce{1600*2sqrt{2}}$
16002, which is about 2262.74169979695, which is lower than the calculated breakpoint distance of 3038.5020760604075, so we add the Path_Loss_Permanentg parameter to indicate the permanence of the PathLoss Model, and omit the calculation of the breakpoint each time the RSRP is updated.

Each update has to be recalculated, but the calculation time is second, the focus is on the dynamic read and write actions from the configuration file, so we designed the flexibility of the program to ensure that under the safety of the configuration file, reduce Minimal movement for reading and writing.

## ***Multuiple gNB System***

![Multuiple gNB System](img/RSRP_Detection_Multiple_gNB.png)

Unlike the Single gNB system, which has the main control UE, the Multiple gNBs system does not have the main UE and adopts a symmetric architecture, so in our simulation, the gNB and the UE are randomly generated at the beginning, we call it For Initialization, this creates a very important problem: because of randomness, the process and algorithm must be set to elastic.

However, our gNB does not move, so the algorithmic points of the two are different. The comparison is as follows:

| | gNB | UE |
| :--: | :--: | :--: |
| Fixed information | Location,Antenna power,Center frequency | Name,IP location
| Dynamic information | Currently connected UE | Location,Currently connected PCell and SCell,RSRP |
| static variable | User Terminal High | |
| algorithm focus | Correspondence between MCG and SCG | Instant dynamic updates |

After that, we will allocate a new CellGroup setting through the RRC request, and determine the PCell and SCell of each UE here, which is an important basis for our next calculation.