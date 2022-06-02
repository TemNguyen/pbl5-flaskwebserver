from datetime import datetime
import requests
import json
with open("./config.json", "r") as file:
    config = json.load(file)
# url = 'http://127.0.0.1:8000/userRequest'

user_reIndentify = {
        "userid": "testapi",
        "timestamps": str(datetime.now()),
        "imageUri": "img_url",
        "response": "False",
    }
# print(user_history["timestamps"])
# print(type(user_history["timestamps"]))
# user_history = json.dumps(user_history)
x = requests.post(config["api_url"]+"userRequest", json=user_reIndentify)
print(x.status_code)
