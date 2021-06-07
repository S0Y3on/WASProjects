from pymongo import MongoClient
from AccessControl import *
from Injection import *
from XSS import manage
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

MONGOURL = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:"
MONGOPORT = "27017"
ATTACKSERVER = ""
ATTACKPORT = "1000"
def startApp(url : str, tools : list, user : dict) :
    client = MongoClient(MONGOURL+MONGOPORT)
    db = client['WAS']
    coll = db[url]
    print(1111)
    for tool in tools :
        if tool == "XSS" :
        #    manage.XSSPoint(url, user)
            pass
        elif tool == "Injection":
            pass
        elif tool == "XXE" :
            pass
        elif tool == "Broken Access Control" :
            pass
        elif tool == "Broken Authentication" :
            pass
    return True

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    startpoint()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

