from Face.Inference.FaceRecognition import FaceRecognition
from Face.Inference.FaceDetection import FaceDetection
from Face.Inference.Facenet import Facenet
from Face.Classifier.SVM import SVM
from bson.objectid import ObjectId
from pymongo import MongoClient
from Response import Response
from datetime import datetime
import cloudinary.uploader
from os.path import join
import urllib.request
import numpy as np
import cloudinary
import requests
import base64
import socket
import certifi
import json
import cv2

# Load cluster url từ file json
with open("./config.json", "r") as file:
    config = json.load(file)

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name=config["cloud_name"],
    api_key=config["api_key"],
    api_secret=config["api_secret"]
)


# detector = FaceDetection()
# recognizer = FaceRecognition()
fn = Facenet()


############################## CAO MONGO VE JSON ##########################
def mongo_2_json(DB_path="./Face/Database", DB_file="Database.json"):
    data = {}
    client = MongoClient(config["cluster"], tlsCAFile=certifi.where())
    db = client["pbl5"]
    list_user = db["user"]
    for user in list_user.find():
        data[str(user["_id"])] = user["FeatureVector"]
    # Cập nhật lại database
    with open(join(DB_path, DB_file), "w") as db:
        json.dump(data, db)
    print(">> Get Database Done")


############################## NHAN DANG ##########################
def bytes_to_cv2(img: bytes):
    # Convert bytes sang OpenCV nparray
    img = np.asarray(bytearray(img), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img


def recognition(img: bytes):
    # ByteIO ->  .read()  -> bytes
    img = bytes_to_cv2(img)
    identity = "NOFACE"
    distance = -100000
    try:
        identity, distance = fn.Get_People_Identity_SVM(img)[0]
    except:
        pass
    return identity, distance


def save_img_to_cloudinary(img: str):
    result = cloudinary.uploader.upload("data:image/jpeg;base64," + img, folder="userRequest")
    url = result.get("url")
    return url


def save_recognition_history(userid: str, img: bytes):
    # Bytes -> base64
    img = base64.b64encode(img)
    imgBS64 = img.decode("ascii")
    img_url = save_img_to_cloudinary(imgBS64)
    if userid != "UNKNOWN":
        isVerify = "Yes"
    else:
        isVerify = "No"
    user_history = {
        "timestamps": str(datetime.now()),
        "imageURi": img_url,
        "isVerify": isVerify,
        "userId": userid
    }
    requests.post(config["api_url"]+"history", json=user_history)


############################## SVM ##########################
def retrain_svm():
    svm = SVM()
    train_acc, test_acc = svm.train()
    return train_acc, test_acc


############################## TRICH VECTOR DAC TRUNG ##########################
def cv2_from_url(url):
    req = urllib.request.urlopen(url, cafile=certifi.where())
    img = np.asarray(bytearray(req.read()), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img


def image_to_vector(url):
    img = cv2_from_url(url)
    # Detect khuôn mặt
    rec = fn.detector.Detect_Face(img, resize=True, scale=4)
    # Crop ra khuôn mặt đầu tiên
    face = fn.detector.Crop_Face(img, rec)[0]
    # Vector đặc trưng
    face_embd = fn.recognizer.Get_Face_Embedding(face).flatten().tolist()
    return face_embd


def save_feature_vector(id: str):
    client = MongoClient(config["cluster"], tlsCAFile=certifi.where())
    db = client["pbl5"]
    list_user = db["user"]
    # Lấy user bằng id
    user = list_user.find_one({"_id": ObjectId(id)})
    vector = []
    for img in user["image"]:
        vector.append(image_to_vector(img))
    list_user.update_one({"_id": ObjectId(id)}, {"$set": {"FeatureVector": vector}})
    # Update user
    return len(vector)

############################## SEND TO RASPBERRY PI ##########################

def send_back(connection: socket, resp: Response):
    connection.sendall(resp.encode())
