from os import close, stat
from flask import Flask, jsonify, request
import time
import logging
import json
import socket


app = Flask(__name__)
PORT = 1440
FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
DATE_FORMAT = '%Y/%m/%d,%H:%M:%S'
logging.basicConfig(level=logging.DEBUG, filename='./log/gNB_Uma_Simulation.log', filemode='a', format=FORMAT, datefmt=DATE_FORMAT)
logging.warning('Start Server')
print('Start Server Port:', PORT)
gNB_IP=""

"""
Functions Related to Parameters:
"""

#Initialize Parameter
def Initialize():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    gNB_IP=s.getsockname()[0]

"""
Functions of APIs to UE Access
1.RRCSetupRequest
"""

#Setp(1) Get RRCSetupRequest from UE and 1.to CU 2.Response to UE
@app.route("/RRCSetupRequest", methods=['POST'])
def RRCSetupRequest():
    logging.info("Enable: gNB["+gNB_IP+"] Function:RRCSetupRequest")
    request_data=request.get_json()
    
    print(request_data)
    return jsonify({"RRC":"RRCSetUp"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)

