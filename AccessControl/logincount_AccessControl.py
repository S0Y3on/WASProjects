from selenium import webdriver
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime
from bs4 import BeautifulSoup


# MongoDB 관련 함수
class Schema:
    def __init__(self):
        self.vulname = "Broken Access Control"
        self.type = "logincount"
        self.logincount_TargetPage = ""
        self.logincount_Count = 5
        self.logincount_Policy = ""
        self.logincount_Time = ""
        self.client = MongoClient("127.0.0.1", 27017)

    def insertDB(self, data, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_one(data).inserted_id
        return result


# 옵션 생성
class logincount:
    def __init__(self, urls, user, chromedriverPATH):
        # Setting WebDriver Option
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.chromedriverPATH = chromedriverPATH
        self.url = urls + "/accounts/login/"
        self.user = user
        self.mongo = Schema()
        self.mongo.logincount_TargetPage = self.url

    def logincheck(self):
        browser = webdriver.Chrome(self.chromedriverPATH, options=self.options)
        for i in range(0, self.mongo.logincount_Count + 1):
            browser.get(self.url)
            # 로그인 정보 입력할 칸 찾기
            input_id = browser.find_element_by_css_selector("#id_login")
            input_pw = browser.find_element_by_css_selector("#id_password")
            input_id.send_keys(self.user['login'])

            if i < self.mongo.logincount_Count:
                input_pw.send_keys(self.user['login'])
            else:
                input_pw.send_keys(self.user['password'])

            browser.find_element_by_css_selector("body > form > button").click()

        if (browser.current_url != self.url):
            print("Success Login")
            print(self.mongo.logincount_Time)
            print("CurrentURL = " + browser.current_url)
            print("Result = Success(로그인 횟수 제한되지 않음)")
            self.mongo.logincount_Policy = "X"
            self.mongo.insertDB({"vulname": self.mongo.vulname,
                                 "Type": self.mongo.type,
                                 "logincount_TargetPage": self.mongo.logincount_TargetPage,
                                 "logincount_Count": self.mongo.logincount_Count,
                                 "logincount_Policy": self.mongo.logincount_Policy,
                                 "logincount_Time": self.mongo.logincount_Time},
                                "WAS", "test")
            # "testdb","adminTest3")
        else:
            print("Fail Login")
            print(self.mongo.logincount_Time)
            print("CurrentURL = " + browser.current_url)
            print("Result = Fail(로그인 횟수 %d회 제한됨)" % (self.mongo.logincount_Count))
            self.mongo.logincount_Policy = "O"
            self.mongo.insertDB({"vulname": self.mongo.vulname,
                                 "Type": self.mongo.type,
                                 "logincount_TargetPage": self.mongo.logincount_TargetPage,
                                 "logincount_Count": self.mongo.logincount_Count,
                                 "logincount_Policy": self.mongo.logincount_Policy,
                                 "logincount_Time": self.mongo.logincount_Time},
                                "WAS", "test")
            # "testdb","adminTest3")
        browser.close()

    def loginrun(self):
        self.mongo.logincount_Time = datetime.utcnow()
        self.logincheck()


def cntPoint(coll: MongoClient, urls: list, user: dict, chromedriverPATH: str):
    # 이 지점을 스타트 포인트로 잡고 짜시면 될거같습니다
    run = logincount(urls, user, chromedriverPATH)
    run.loginrun()
    pass