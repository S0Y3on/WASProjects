from _typeshed import NoneType
from requests.api import options
from AccessControl.adminpage_AccessControl import adminPoint
from pymongo import MongoClient
from . import adminpage_AccessControl
from . import dictpage_AccessControl
from . import logincount_AccessControl
from selenium import webdriver


def insertMongo(coll : MongoClient, datas : dict) :
    coll.insert_many(datas)

def setBrowser(PATH : str) -> webdriver :
    options = webdriver.ChromeOptions()
    options.add_argumnet("headless")
    browser = webdriver.Chrome(PATH, options=options)
    return browser

def accPoint(coll : MongoClient, urls : list, user : dict) :
    datas = []
    #이하로 각 type의 시작포인트
    browser = setBrowser('../chromedriver_win32/chromedriver.exe')
    datas.append(adminpage_AccessControl.adminPoint(urls, user, browser))
    datas.append(dictpage_AccessControl.dictPoint(urls, user))
    datas.append(logincount_AccessControl.cntPoint(urls, user, browser))
    insertMongo(coll, datas)

if __name__ == "__main__" : 
    MONGOURL = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:"
    MONGOPORT = "27017"
    client = MongoClient(MONGOURL+MONGOPORT)
    db = client['WAS']
    coll = db["test"]
    urls = []
    user = {
        "id" : None,
        "password" : None
    }
    accPoint(coll, urls, user)

