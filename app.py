from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
import datetime


app = Flask(__name__)

# CONFIG
app.config["MONGO_URI"] = "mongodb+srv://teamDA:123@ngan.2a0oj.mongodb.net/pbl5?retryWrites=true&w=majority/pbl5"
app.config["JWT_SECRET_KEY"] = "pbl52022"

#
mongo = PyMongo(app)
jwt = JWTManager(app)

# Jwt response message
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'status': 401,
        'msg': 'Token đã hết hạn, vui lòng đăng nhập lại!'
    }), 200

@jwt.invalid_token_loader
def my_invalid_token_loader_callback(jwt_header):
    return jsonify({
        'status': 401,
        'msg': 'Token không hợp lệ'
    }), 200

@jwt.unauthorized_loader
def my_unauthorized_loader(jwt_header):
    return jsonify({
        'status': 401,
        'msg': 'Người dùng chưa được xác thực'
    }), 200