import time
import requests
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime

class DBHandler:
    def __init__(self):
        #Local Test
        #host = "localhost"
        #port = "27017"
        host = "127.0.0.1"
        port = "29528"
        self.client = MongoClient(host, int(port))

    def insert_item_one(self, data, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_one(data).inserted_id
        return result

    def insert_item_many(self, datas, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_many(datas).inserted_ids
        return result

    def find_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find_one(condition, {"_id": False})
        return result

    def find_item(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)
        return result

    def delete_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_one(condition)
        return result

    def delete_item_many(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_many(condition)
        return result

    def update_item_one(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_one(filter=condition, update=update_value)
        return result

    def update_item_many(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_many(filter=condition, update=update_value)
        return result

    def text_search(self, text=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find({"$text": {"$search": text}})
        return result
mongo = DBHandler()
success = 0
dic_count = 0
destination_page=""
vulname = "Broken Access Control"
type = "dictpage"
info = []

def requestPart(param):
    global destination_page
    global success
    destination_page="https://soy3on.pythonanywhere.com"
    URL = "https://soy3on.pythonanywhere.com" + "/" + param + "/"
    header = ""
    response = requests.get(URL)
    if response.status_code == 200 :
        print("Target page : " + response.url)
        #print("Cookie : ",response.cookies)
        success +=1
        result = "O"
        date = datetime.utcnow()
        print(date)
        print("Result : ",result)
        info.append(param)
    time.sleep(0.01)

#dictionary
with open("dic.txt", "r") as f:
    for line in f.readlines():
        dic_count += 1
        requestPart(line.strip())

#random regex (a~z,length=5)

fail = dic_count-success
mongo.insert_item_one({"vulname":vulname,
                       "Type":type,
                       "dictpage_Destination_Page":destination_page,
                       "dictpage_info":info,
                       "dictpage_Success":success,
                       "dictpage_Fail":fail},
                        "WAS","test")
                        #"testdb","adminTest1")
print("Success : ", success, "Fail : ", fail)


def dictPoint(coll : MongoClient, urls : list, user : dict) :
    #이 지점을 스타트 포인트로 잡고 짜시면 될거같습니다
    pass