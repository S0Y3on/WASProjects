import time
import requests

success = 0

def requestPart(param):
    URL = "https://soy3on.pythonanywhere.com" + "/" + param + "/"
    global success
    header = ""
    response = requests.get(URL)
    if response.status_code == 200 :
        print("Target page : " + response.url)
        success +=1
    time.sleep(0.01)

#dictionary
with open("dic.txt", "r") as f:
    for line in f.readlines():
        requestPart(line.strip())

#random regex (a~z,length=5)
print("Success : ", success)