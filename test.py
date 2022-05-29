from datetime import datetime
import requests
import json

url = 'http://127.0.0.1:8000/history'

user_history = {
    "timestamps": str(datetime.now()),
    "imageURi": "http:localhost",
    "isVerify": "Yes",
    "userId": "UNKNOWN"
}
# print(user_history["timestamps"])
# print(type(user_history["timestamps"]))
# user_history = json.dumps(user_history)
x = requests.post(url, json=user_history)
print(x.status_code)
