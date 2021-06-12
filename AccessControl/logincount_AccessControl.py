from selenium import webdriver
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime
from bs4 import BeautifulSoup

vulname = "Broken Access Control"
type = "logincount"

#MongoDB 관련 함수
class DBHandler:
    def __init__(self):
        #Local Test
        host = "localhost"
        port = "27017"
        #host = "127.0.0.1"
        #port = "29528"
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

# 옵션 생성
options = webdriver.ChromeOptions()
options.add_argument("headless")

#https://soy3on.pythonanywhere.com/accounts/login/ dream nana0813

browser = webdriver.Chrome('chromedriver.exe', options=options)
count = 5

def logincheck(login_url, user):
    browser.get(login_url)
    global count
    # 로그인 정보 입력할 칸 찾기
    input_id = browser.find_element_by_css_selector("#id_login")
    input_pw = browser.find_element_by_css_selector("#id_password")

    # 로그인 정보 값 입력
    input_id.send_keys(user['login'])
    for i in range(0, count+1):
        if i < count:
            input_pw.send_keys("hello")
        else:
            input_pw.send_keys(user['password'])

    # 로그인 클릭
    browser.find_element_by_css_selector("body > form > button").click()

#url, 관리자계정 값 받기
url, id, passwd = input('사용자 입력 값 : ').split()
user = {
    'login': id,
    'password': passwd
}

logincheck(url, user)
date = datetime.utcnow()

if (browser.current_url != url):
    print("Success Login")
    print(date)
    print("Result = Success(로그인 횟수 제한되지 않음)")
    limit = "X"
    mongo.insert_item_one({"vulname":vulname,
                           "Type":type,
                           "logincount_TargetPage":url,
                           "logincount_Count": count,
                           "logincount_Policy":limit,
                           "logincount_Time":date},
                            "WAS", "test")
                            #"testdb","adminTest3")
else:
    print("Fail Login")
    print(date)
    print("Result = Fail(로그인 횟수 %d회 제한됨)" %(count))
    limit = "O"
    mongo.insert_item_one({"vulname":vulname,
                           "Type": type,
                           "logincount_TargetPage":url,
                           "logincount_Count": count,
                           "logincount_Policy":limit,
                           "logincount_Time":date},
                            "WAS", "test")
                            #"testdb","adminTest3")

def cntPoint(coll : MongoClient, urls : list, user : dict, chromedriverPATH : str) :
    #이 지점을 스타트 포인트로 잡고 짜시면 될거같습니다
    pass