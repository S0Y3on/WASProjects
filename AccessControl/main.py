from AccessControl.adminpage_AccessControl import adminPoint
from pymongo import MongoClient
from . import adminpage_AccessControl
from . import dictpage_AccessControl
from . import logincount_AccessControl

def accPoint(coll : MongoClient, urls : list, user : dict) :
    chrome_driverPATH = '../chromedriver_win32/chromedriver.exe'
    #이하로 각 type의 시작포인트
    adminpage_AccessControl.adminPoint(coll, urls, user, chrome_driverPATH)
    dictpage_AccessControl.dictPoint(coll, urls, user)
    logincount_AccessControl.cntPoint(coll, urls, user, chrome_driverPATH)

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

