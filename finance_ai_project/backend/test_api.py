import requests

data = {"month_num":5}

res = requests.post(
    "http://127.0.0.1:5000/predict",
    json=data
)

print(res.json())