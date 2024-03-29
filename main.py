from utils import (recognition, save_recognition_history, save_reIndentify_request,
                   mongo_2_json, save_feature_vector, retrain_svm, send_back)
from ResponseModel import ResponseModel
from flask import jsonify, request
from Response import Response
from app import app
from _thread import *
import threading
import socket
import struct
import io

dic = dict()
list_recognition = []
reIndentify_userId = ''

def recognition_handle(connection, image):
    global list_recognition
    global reIndentify_userId
    
    identity, distance = recognition(image)
    print(identity, distance)
    list_recognition.append(identity)

    if (len(list_recognition) >= 5):
        identity = max(set(list_recognition), key = list_recognition.count)
        print("-->" + identity)
        # New thread: Send command to Raspberry Pi
        if identity == "NOFACE":
            return
        elif identity != "UNKNOWN":
            resp = Response('open-door', 'mo_cua')
            start_new_thread(send_back, (connection, resp))
        else:
            resp = Response('failure', 'nhan_dang_sai')
            start_new_thread(send_back, (connection, resp))

        list_recognition = []

        # New thread: Call API to save recognition history
        start_new_thread(save_recognition_history, (identity, image))

        if (reIndentify_userId != ''):
            start_new_thread(save_reIndentify_request, (reIndentify_userId, image))
            reIndentify_userId = ''


def thread_client(connection):
    conn = connection.makefile('rb')
    while True:
        cnn = conn.read(4)
        if cnn != b'':
            image_len = struct.unpack('<L', cnn)[0]

            image_stream = io.BytesIO()
            image_stream.write(conn.read(image_len))
            
            image_stream.seek(0)
            start_new_thread(recognition_handle, (connection, image_stream.read()))

def tcp_server():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 9000))
    server_socket.listen(0)
    while True:
        connection, _ = server_socket.accept()
        dic['connection'] = connection
        if connection:
            start_new_thread(thread_client, (connection, ))

############################## MOBILE'S GENERAL API ##########################

@app.route('/', methods=['GET'])
def home():
    return ResponseModel("Server running successfully.", 200, "success", False)

@app.route('/open-door')
def open():
    conn = dic.get('connection')
    resp = Response('open-door', 'mo cua')
    start_new_thread(send_back, (conn, resp))
    return ResponseModel("Open the door successfully.", 200, "success", False)

############################## MOBILE'S USER API ##########################

# Add jwt
@app.route('/re-identify/<id>')
def reRecognize(id: str):
    global reIndentify_userId
    conn = dic.get('connection')
    resp = Response('re-identify', 'nhan dang lai')
    reIndentify_userId = id
    start_new_thread(send_back, (conn, resp))
    return ResponseModel("reIndentify request be sent.", 200, "success", False)

############################## MOBILE'S ADMIN API ##########################

# Add jwt
@app.route('/manage/save-feature-vector/<id>')
def save_vector(id: str):
    len_vector = save_feature_vector(id)
    return ResponseModel(f'Save {len_vector} vector successfully!', 200, "success", False)

@app.route('/manage/re-train')
def retrain_model():
    mongo_2_json()
    train_acc, test_acc = retrain_svm()
    return ResponseModel(f'Retrain SVM with {train_acc} and {test_acc}!', 200, "success", False)

############################## FLASK INITIATION ##########################

if __name__ == "__main__":
    t = threading.Thread(target=tcp_server)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)
