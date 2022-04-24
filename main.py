from app import app, mongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request
import threading, socket

#init tcp socket server
def tcp_server():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 9000))
    server_socket.listen(0)
    while True:
        pass

#GET: /users
@app.route('/users')
def users():
	users = mongo.db.User.find()
	response = dumps(users)
    
	return response

#GET: /users/1
@app.route('/users/<id>')
def user(id):
    user = mongo.db.User.find_one({'_id': ObjectId(id)})
    response = dumps(user)
    return response

#POST /create
@app.route('/create', methods=['POST'])
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
    app.run(debug=False, use_reloader=False)