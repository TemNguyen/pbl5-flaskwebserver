from app import app, mongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request
from _thread import *
from Response import Response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import threading, socket, struct, io
import urllib.request, json
import requests

dic = dict()
base_api_url = 'http://127.0.0.1:8000'

def thread_client(connection):
    conn = connection.makefile('rb')
    while True:
        cnn = conn.read(4)
        if cnn != b'':
            image_len = struct.unpack('<L', cnn)[0]

            image_stream = io.BytesIO()
            image_stream.write(conn.read(image_len))
            
            image_stream.seek(0)

            # image = Image.open(image_stream)
            # np_arr = np.array(image)
            # print(np_arr.shape)
            # print('Image is %dx%d' % image.size)
            # image.save('abc.jpeg')

            # Face detection module

            # async: Call api to save data
            resp = Response('save_data', 'Luu du lieu nhan dang')
            # start_new_thread(call_api, ('post', resp))

            # # async: send back to client
            if face_detection(resp) == True:
                resp = Response('success', 'mo_cua')
                start_new_thread(send_back, (connection, resp))
            else:
                resp = Response('failure', 'nhan_dang_sai')
                start_new_thread(send_back, (connection, resp))
        else:
            break

#init tcp socket server
def tcp_server():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 9000))
    server_socket.listen(0)
    while True:
        connection, _ = server_socket.accept()
        dic['connection'] = connection
        if connection:
            start_new_thread(thread_client, (connection, ))

# Call api
def call_api(method, response):
    # Create indentify history object

    # Convert to json/bson

    # Call api to save data
    pass

# Call face detection module
def face_detection(resp):
    return True

# Send back to client
def send_back(connection: socket, resp: Response):
    connection.sendall(resp.encode())

# Example flask api
@app.route('/')
def home():
    res = urllib.request.urlopen(base_api_url + '/user/6246d7fbe5065d8a35eb2dca')
    data = res.read()
    dict = json.loads(data)
    return jsonify(dict['username'])

# Test, bên mobile sẽ lo phần này
@app.route('/login', methods=['post'])
def login():
    req = request.get_json()
    #call login
    user = mongo.db.user.find_one({'username': req['username'], 'password': req['password']})

    if user:
        access_token = create_access_token(identity=user['_id'])
        return jsonify(access_token=access_token), 200
    
    return jsonify({'msg': 'The username or password is incorrect'}), 200

#GET: /users
@app.route('/open', methods=['GET'])
@jwt_required()
def open():
    user = mongo.db.user.find_one({'_id': get_jwt_identity()})

    if user:
        conn = dic.get('connection')
        resp = Response('success', 'mo cua')
        start_new_thread(send_back, (conn, resp))
        return jsonify('Open the door successfully!'), 200
    else:
        return jsonify('User not found'), 200

@app.route('/close')
@jwt_required()
def close():
    user = mongo.db.user.find_one({'_id': get_jwt_identity()})

    if user:
        conn = dic.get('connection')
        resp = Response('fail', 'dong cua')
        start_new_thread(send_back, (conn, resp))
        return jsonify('Close the door successfully!')
    else:
        return jsonify('User not found'), 200

#POST /create
@app.route('/create', methods=['POST'])
@jwt_required()
def create():
    _json = request.json
    _name = _json['name']
    _address = _json['address']

    id = mongo.db.User.insert_one({'name': _name, 'address': _address})
    response = jsonify('Create successfully')
    response.status_code = 200
    return response    

if __name__ == "__main__":
    t = threading.Thread(target=tcp_server)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)