# Background

## Development of Electronic Fence in Taiwain

At beginning of 2021,COVID-19 ravaged the world.Inthe face of this highly contagious disease,the Tainwain government stipulated that people infected with the epicdemic or those who were framed need to be quarantined,and jiontly developed an electronic epidemic prevention platform wuth the Health Bureau,the five major telecommunications companies and NCC().Whether the SIM Card is in the fixed range of the base station to detected whether the quarantined person has left the quarantine range.

![Electronic Fence Advertisement](img/electronic_fence.jpg)

When the mobile phone is connected to a nearby base station, in addition to the door number information, there is also the mobile phone IMEI information, which can be used to bind the door number, mobile phone, and personal data. As long as you have a mobile phone or SIM card, it can be detected. your approximate location. Therefore, the command center can track the door number, IMEI code and other information to confirm which base station the home quarantine person is near, and then find the location of the home quarantine person and the autonomous health manager.

We can see in this phenomenon that it used in this situation and playing an important role in the epidemic.***But you may asked:***

***"But it only works in this case."***

We can imagine more applications of it, such as boarding schools, or workplaces. If it is more open to imagination, it can be "avoid entering certain areas" rather than "prohibit leaving certain areas", which can mark hazardous substances or Dangerous places, so that we can immediately go over and take action when others enter the area, we think this is a feasible idea, after all, who said fences are for keeping others in?

---

## The relationship between electronic fence and 5G

Why is 5G-based electronic fence suitable for development? We explain why 5G is suitable for the development of electronic fences based on several characteristics

1. **Deployment of small base stations to increase handover frequency** 
   The density of base stations increases, which means that in a limited area (here, it can be regarded as a base station that can receive signals within the  fence range), the frequency of handover becomes higher. Positioning accuracy.
    See the picture below, the following is the signal distribution of Chunghwa Telecom 5G base station.
    See: Mobile broadband system 5G NR+4G LTE covered Website <https://coverage.cht.com.tw/coverage/tw.html>

    ![signal distribution of Chunghwa Telecom 5G base station](img/Signal_Distribution.png)
2. **Beam pointing problem caused by mmWave (26 GHz) communication, which requires user's location information** 
   Positioning and 5G are mutually complementary links. Signal positioning technology will be valued in the future, and the classic "electronic fence" used in its application will also be technically improved.
3. **The low-latency requirement of IoV communication also introduces the requirement of mutual positioning between workshops** 
   If a larger area is selected, such as a city, then people may move with vehicles, and the signal positioning will become very complicated. In terms of the Doppler effect alone, the uncertainty of the calculation will become higher, and the calculation The vehicle may be moved to another location within the required time.
    For this we need the low latency of 5G, and edge computing technology to avoid this.
4. **The rise of MEC technology**
    MEC technology is a technology to improve the speed of 5G. Edge computing allows different blocks to do different tasks so that the access network does not need to calculate other things to slow down performance.

---

## Problems with current electronic fences

### Frequent errors still occur

As you can see, the search results are based on whether or not the base station outside the range has an IMEI code with a Converse registration number, and are not precise, so errors can still occur.

### Human Rights Privacy? Technology enforcement issues?

China's SkyNet system is considered to be an infringement of people's privacy, but in reality, the electronic fence is the same in nature as the SkyNet, and the constitution protects people's freedom of residence and movement, which would normally make the system unconstitutional, and this part of the system is also controversial.
In the event of an epidemic, people can compromise for the safety of others, but after that it is a matter of concern for those who give their freedom to examine whether the electronic fence system is really working as it should.

---

## What could be improved?

1. **Improving precision**
   We can try to reduce the error as much as possible by using MEC to calculate the range, if we can get the error of 1 in the same way as GPS.
2. **Irregularities in scope**
   Determine the extent of bounded, irregular shapes through algorithms
3. **Positioning in three dimensions**
   For Apartment we can know whether specified user left his leyer.
4. **Encryption algorithms for personal data security**
    Ensure the flow of personal data, its use and the lack of easy access to third parties
