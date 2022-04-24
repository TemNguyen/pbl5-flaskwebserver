from flask import Flask
from flask_pymongo import PyMongo
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDb"
mongo = PyMongo(app)