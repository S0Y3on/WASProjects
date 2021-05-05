import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import requests

success = fail = 0

def requestPart(param):
    URL = "https://soy3on.pythonanywhere.com" + param
    global success
    global fail
    header = ""
    #response = requests.post(URL,headers=header)
    response = requests.get(URL)
    if response.url == URL:
        print("OK URL: " + URL)
        success += 1
    else:
        print("Fail URL : " + URL)
        fail += 1


#chrome 드라이버 경로
chrome_driver_path = "E:/WASProjects/chromedriver_win32/chromedriver.exe"

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

print("Success : " , success, "Fail : " , fail)