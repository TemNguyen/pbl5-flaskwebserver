from utils import (recognition, save_recognition_history,
                   mongo_2_json, save_feature_vector, retrain_svm, send_back)
from flask import jsonify, request
from Response import Response
from app import app
from _thread import *
import threading
import socket
import struct
import io


dic = dict()


def thread_client(connection):
    conn = connection.makefile('rb')
    while True:
        cnn = conn.read(4)
        if cnn != b'':
            image_len = struct.unpack('<L', cnn)[0]

            image_stream = io.BytesIO()
            image_stream.write(conn.read(image_len))
            image_stream.seek(0)

            # Face recognition module
            identity, _ = recognition(image_stream.read())

            # async: send back to client
            if identity != "UNKNOWN":
                resp = Response('success', 'mo_cua')
                start_new_thread(send_back, (connection, resp))
            else:
                resp = Response('failure', 'nhan_dang_sai')
                start_new_thread(send_back, (connection, resp))
            # Goi API luu user request
            start_new_thread(save_recognition_history, (identity, image_stream.read()))
        else:
            break

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
    return jsonify('Server running successfully!')

@app.route('/open')
def open():
    conn = dic.get('connection')
    resp = Response('success', 'mo cua')
    start_new_thread(send_back, (conn, resp))
    return jsonify('Open the door successfully!')

@app.route('/close')
def close():
    conn = dic.get('connection')
    resp = Response('fail', 'dong cua')
    start_new_thread(send_back, (conn, resp))
    return jsonify('Close the door successfully!')

############################## MOBILE'S USER API ##########################

@app.route('/re-identify')
def reRecognize():
    conn = dic.get('connection')
    resp = Response('recognize', 'nhan dang lai')
    start_new_thread(send_back, (conn, resp))
    return jsonify('reIndentify request be sent')

############################## MOBILE'S ADMIN API ##########################

@app.route('/save-feature-vector/<id>')
def save_vector(id: str):
    len_vector = save_feature_vector(id)
    return jsonify(f'Save {len_vector} vector successfully!')

@app.route('/re-train')
def retrain_model():
    mongo_2_json()
    train_acc, test_acc = retrain_svm()
    return jsonify(f'Retrain SVM with {train_acc} and {test_acc}!')

############################## FLASK INITIATION ##########################

if __name__ == "__main__":
    t = threading.Thread(target=tcp_server)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)
