import json
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from pymongo import MongoClient




class Schema:
    def __init__(self, coll):
        try:
            self.client = coll
        except:
            print('DB connect error')
        self.vulname = 'XSS'
        self.method = ''
        self.url = ''
        self.isHack = False
        self.totalHack = 0
        self.hackCode = []
        self.vultype = ''
        self.timestamp = datetime.utcnow()

    def addTotalHack(self):
        self.totalHack += 1

    def setHackInformation(self, url, method, hackCode):
        self.url = url
        self.method = method
        self.hackCode.append(hackCode)
        self.isHack = True
        if method == 'GET':
            self.vultype = 'Reflected'
        else:
            self.vultype = 'Stored'

    def insertDB(self, data, client):
        result = self.client.insert_one(data).inserted_id
        return result


class XssFuzzer:
    def __init__(self, url, user):
        self.url = url
        # Set Login Session
        self.session = requests.session()
        self.session.post(url + "/accounts/login/", data=user)
        self.res = self.session.get(url)
        self.bs = BeautifulSoup(self.res.text, 'html.parser')

        # Setting WebDriver Option
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1920,1080')

        # Read Attack Code
        self.scripts = []
        with open("script.txt", "r") as f:
            for line in f.readlines():
                self.scripts.append(line.strip())

    def findHref(self):
        # 검사하는 url에서 이동할 수 있는 href 찾아서 공격
        href_link = []
        for link in self.bs.findAll('a'):
            # 이동할 수 있는 url이 있는 경우
            if 'href' in link.attrs:
                href_link.append(link.attrs['href'])
            else:
                print("No Hyperlink Link")

        for link in self.bs.findAll('form'):
            if 'action' in link.attrs:
                href_link.append(link.attrs['action'])
            else:
                print("No form tag")
        return href_link

    def insertAttackCode(self, href_link, coll):
        # Chrome WebDriver
        try:
            driver = webdriver.Chrome('/root/test/WASProjects/XSS/chromedriver', chrome_options=self.options)
        except:
            print('driver road error')
        # Link 하나 씩 검사
        for link in href_link:
            Hack = Schema(coll)
            input_resp = self.session.post(self.url + link)
            # input 태그 유무검사
            if input_resp.text.find('input') > 0:
                input_bs = BeautifulSoup(input_resp.text, 'html.parser')
                for script in self.scripts:
                    if not input_bs.find('form'):
                        print('No Form')
                        self.checkScriptForm(input_bs)

                    elif input_bs.find('form').get('method').casefold() == 'post':
                        Hack.addTotalHack()
                        # 큰 사이즈의 text가 들어가는 textarea 태그가 있는지 확인하여 있다면 공격 코드 설정
                        input_script = {
                            str(input_bs.find('textarea').get('name')): script,
                        }

                        # input 태그에 공격코드 설정
                        for input_tag in input_bs.find_all('input'):
                            input_script[input_tag.get('name')] = script

                        attack_resp = self.session.post(self.url + link, data=input_script)
                        driver.get(attack_resp.url)
                        self.alertCheck(driver, Hack, input_bs.find('form').get('method'), link, script)

                    elif input_bs.find('form').get('method').casefold() == 'get':
                        Hack.addTotalHack()
                        input_script = {}

                        # input 태그에 공격코드 설정
                        for input_tag in input_bs.find_all('input'):
                            input_script[input_tag.get('name')] = script

                        attack_resp = requests.get(self.url + link, params=input_script)
                        driver.get(attack_resp.url)
                        self.alertCheck(driver, Hack, input_bs.find('form').get('method'), link, script)

                    else:
                        print("Not allowed Method")
                        pass

            else:
                print('No Input Tag')
                pass
                # for script in self.scripts:
                #     Hack.addTotalHack
                #     driver.get(url + link)
                #     self.alertCheck(driver, Hack, link, script)

            if Hack.totalHack > 0:
                Hack.insertDB(data={'vulname': Hack.vulname,
                                    'method': Hack.method,
                                    'url': Hack.url,
                                    'isHack': Hack.isHack,
                                    'totalHack': Hack.totalHack,
                                    'XssType': Hack.vultype,
                                    'hackCode': Hack.hackCode,
                                    'timestamp': Hack.timestamp,
                                    })
        driver.close()

    def alertCheck(self, driver, Hack, method, link, script):
        try:
            result = driver.switch_to_alert()
            print('alert text : ' + str(result.text))
            result.accept()
            Hack.setHackInformation(self.url + link, method.upper(), script)
            print('Executed an alert')
        except:
            # 공격 실패한 경우
            # hack.isHack = False (Default)
            print('fail XSS')

    def checkScriptForm(self, soup):
        data = soup.find('script', type='text=pattern')
        print(data)

