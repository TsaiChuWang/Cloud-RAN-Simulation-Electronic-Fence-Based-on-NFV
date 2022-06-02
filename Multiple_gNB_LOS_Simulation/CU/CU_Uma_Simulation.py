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

gNB_IP=""
CU_IP="10.0.2.99"

#Recive RSRP from UE
@app.route("/RecievegNB_Information", methods=['POST'])
def RecievegNB_Information():
    request_data=request.get_json()
    print(request_data)
    return "RECIEVE SUCCESS"

#Recive RSRP from UE
@app.route("/INITIAL_UL_RRC_MESSAGE_TRANSFER", methods=['POST'])
def INITIAL_UL_RRC_MESSAGE_TRANSFER():
    request_data=request.get_json()
    print(request_data)
    return jsonify({"RRC":"RRCSetUp"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=PORT)

