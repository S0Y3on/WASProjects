from selenium import webdriver
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime
from bs4 import BeautifulSoup

vulname = "AccessControl"
type = "logincount"

#MongoDB 관련 함수
class DBHandler:
    def __init__(self):
        #Local Test
        #host = "localhost"
        #port = "27017"
        host = "127.0.0.1"
        port = "29666"
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

# chrome driver 경로
chrome_driver_path = "E:\WASProjects\chromedriver_win32\chromedriver_win32\chromedriver.exe"

# 옵션 생성
options = webdriver.ChromeOptions()
options.add_argument("headless")

# login할 admin 페이지 경로
login_url = 'https://soy3on.pythonanywhere.com/accounts/login/'
#mongo.insert_item_one({"logincount_TargetPage":login_url},"testdb","adminTest3")

# 관리자 계정 정보
login_id = "dream"
login_pw = "nana0813"
login_failpw = "yejiJJANG123"

browser = webdriver.Chrome(chrome_driver_path, options=options)

def logincheck(pw):
    browser.get(login_url)

    # 로그인 정보 입력할 칸 찾기
    input_id = browser.find_element_by_css_selector("#id_login")
    input_pw = browser.find_element_by_css_selector("#id_password")

    # 로그인 정보 값 입력
    input_id.send_keys(login_id)
    input_pw.send_keys(pw)

    # 로그인 클릭
    browser.find_element_by_css_selector("body > form > button").click()

count = int(input("로그인 횟수 제한 테스트, 몇회 수행하시겠습니까? (5회 이상 권장) "))
if count <= 0:
    count=int(input("[Error] 다시 입력하세요. "))

# n번 실패하기
for i in range(0, count):
    logincheck(login_failpw)
    date = datetime.utcnow()
    print(date)

# 진짜 패스워드 넣기
logincheck(login_pw)
date = datetime.utcnow()
    #date = date[:date.rfind(':')].replace(' ', ' ')
    #date = date.replace(':', ':')
if (browser.current_url != login_url):
    print("Success Login")
    print(date)
    print("Result = Success(로그인 횟수 제한되지 않음)")
    limit = "X"
    mongo.insert_item_one({"vulname":vulname,
                           "Type":type,
                           "logincount_TargetPage":login_url,
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
                           "logincount_TargetPage":login_url,
                           "logincount_Count": count,
                           "logincount_Policy":limit,
                           "logincount_Time":date},
                            "WAS", "test")
                            #"testdb","adminTest3")