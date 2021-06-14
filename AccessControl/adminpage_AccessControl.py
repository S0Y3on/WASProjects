import sys
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.cursor import CursorType
from datetime import datetime
import requests


# DB관련 함수
class Schema:
    def __init__(self):
        self.vulname = "Broken Access Control"
        self.success = 0
        self.fail = 0
        self.result = ""
        self.type = "adminpage"
        self.info = []
        self.url = ""
        self.client = MongoClient("127.0.0.1", 27017)

    def insertDB(self, data, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_one(data).inserted_id
        return result


class adminpage:
    def __init__(self, urls, user, chromedriverPATH):
        # Setting WebDriver Option
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.chromedriverPATH = chromedriverPATH
        self.url = urls
        self.user = user
        self.mongo = Schema()

    def requestPart(self, param):
        URL = self.url + param
        self.mongo.url = self.url
        header = ""
        response = requests.get(URL)
        if response.url == URL:
            print("OK URL: " + URL)
            self.mongo.result = "O"
            date = datetime.utcnow()
            print(date)
            print("Result : ", self.mongo.result)
            self.mongo.success += 1
            self.mongo.info.append(param)
        else:
            print("Fail URL : " + URL)
            self.mongo.result = "X"
            date = datetime.utcnow()
            print(date)
            print("Result : ", self.mongo.result)
            self.mongo.fail += 1

    def adminpage_login(self):
        browser = webdriver.Chrome(self.chromedriverPATH, options=self.options)
        browser.get(self.url + "/accounts/login")
        print(browser.current_url)
        # 로그인 정보 입력할 칸 찾기
        input_id = browser.find_element_by_css_selector("#id_login")
        input_pw = browser.find_element_by_css_selector("#id_password")

        # 로그인 정보 값 입력
        input_id.send_keys(self.user['login'])
        input_pw.send_keys(self.user['password'])

        # 로그인 클릭
        browser.find_element_by_css_selector("body > form > button").click()
        print(browser.current_url)

        # 관리자 페이지 로그인 후, 접근 가능한 페이지 찾기
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.select('a')

        # 출력 관리자 페이지 로그인 후 접근 가능한 페이지 목록
        af = open('AccessPage.txt', 'w')
        sys.stdout = af

        for n in link:
            print(n.get('href'))

        sys.stdout = sys.__stdout__
        af.close()

        # dictionary
        with open("AccessPage.txt", "r") as f:
            for line in f.readlines():
                self.requestPart(line.strip())
        browser.close()

        self.mongo.insertDB({"vulname": self.mongo.vulname,
                             "Type": self.mongo.type,
                             "adminpage_Destination Page": self.mongo.url,
                             "adminpage_info": self.mongo.info,
                             "adminpage_Success": self.mongo.success,
                             "adminpage_Fail": self.mongo.fail},
                            "WAS", "test")
        # "testdb","adminTest3")

        print("Success : ", self.mongo.success, "Fail : ", self.mongo.fail)


def adminPoint(coll: MongoClient, urls: str, user: dict, chromedriverPATH: str):
    # 이 지점을 스타트 포인트로 잡고 짜시면 될거같습니다
    run = adminpage(urls, user, chromedriverPATH)
    run.adminpage_login()
    pass