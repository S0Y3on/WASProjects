import sys
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime
import requests

#DB관련 함수
class DBHandler:
    def __init__(self):
        host = "localhost"
        port = "27017"
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

success = fail = 0
result = ""
vulname = "AccessControl"
type = "adminpage"

def requestPart(param):
    URL = "https://soy3on.pythonanywhere.com" + param
    global success
    global fail
    global result
    header = ""
    #response = requests.post(URL,headers=header)
    response = requests.get(URL)
    if response.url == URL:
        print("OK URL: " + URL)
        result = "O"
        date = datetime.utcnow()
        print(date)
        print("Result : ", result)
        success += 1
        mongo.insert_item_one({"Vulname":vulname,
                               "Type": type,
                               "adminpage_Target Page":param,
                               "adminpage_Time":date,
                               "adminpage_Result":"O"},
                                "testdb","adminTest2")
    else:
        print("Fail URL : " + URL)
        result = "X"
        date = datetime.utcnow()
        print(date)
        print("Result : ",result)
        fail += 1
        mongo.insert_item_one({"Vulname":vulname,
                               "Type": type,
                               "adminpage_Target Page":param,
                               "adminpage_Time":date,
                               "adminpage_Result":"X"},
                                "testdb","adminTest2")

#chrome 드라이버 경로
chrome_driver_path = "E:\WASProjects\chromedriver_win32\chromedriver_win32\chromedriver.exe"

# 옵션 생성
options = webdriver.ChromeOptions()
options.add_argument("headless")

#login할 admin 페이지 경로
login_url = 'https://soy3on.pythonanywhere.com/admin/login/?next=/admin/'

#관리자 계정 정보
login_id = "dream"
login_pw = "nana0813"

browser = webdriver.Chrome(chrome_driver_path,options=options)
browser.get(login_url)

#로그인 정보 입력할 칸 찾기
input_id = browser.find_element_by_css_selector("#id_username")
input_pw = browser.find_element_by_css_selector("#id_password")

#로그인 정보 값 입력
input_id.send_keys(login_id)
input_pw.send_keys(login_pw)

#로그인 클릭
browser.find_element_by_css_selector("#login-form > div.submit-row > input[type=submit]").click()
print(browser.current_url)

#관리자 페이지 로그인 후, 접근 가능한 페이지 찾기
html = browser.page_source
soup = BeautifulSoup(html,'html.parser')
link = soup.select('a')

#출력 관리자 페이지 로그인 후 접근 가능한 페이지 목록
af = open('AccessPage.txt', 'w')
sys.stdout = af

for n in link:
    print(n.get('href'))

sys.stdout = sys.__stdout__
af.close()

#dictionary
with open("AccessPage.txt", "r") as f:
    for line in f.readlines():
        requestPart(line.strip())

mongo.insert_item_one({"Vulname":vulname,
                       "Type":type,
                       "adminpage_Destination Page":login_url,
                       "adminpage_Success":success,
                       "adminpage_Fail":fail},
                        "testdb","adminTest2")

print("Success : " , success, "Fail : " , fail)
