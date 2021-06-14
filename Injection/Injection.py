import argparse
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from seleniumrequests import Chrome
import time
from multiprocessing import Manager
import multiprocessing
import parmap
import numpy as np
from pymongo import MongoClient
# 로그인이 필요한 경우 로그인 페이지 주소와 계정정보 받아서 세션 아이디 획득
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("headless")
    options.add_argument("window-size=1920x1080")  # 화면크기(전체화면)
    options.add_argument("disable-gpu")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    driver = Chrome('chromedriver.exe', chrome_options=options)
    return driver

# url_table에 저장된 url에 접속하여 파라미터 수집
def get_param(keys, url_table):
    # 멀티프로세싱 적용시 각 프로세스마다 driver를 새로 만들어야 하는 문제 -> 세션관리 문제
    driver = get_driver()
    lists = keys
    domain_parse = re.compile('^https?:\/\/[^\/]+/')
    for url in lists:
        curr_domain = domain_parse.search(url).group()
        # 현재 url이 쿼리파라미터를 포함하고 있다면 쿼리파라미터를 분리해서 url_table에 입력py
        if url_table[url][0] == 'G':
            if url.find('?') != -1:
                div = url.split('?')
                request_url = div[0]
                if div[1].find('&') != -1:
                    queries = div[1].split("&")
                    queries.insert(0, 'G')
                else:
                    queries = ['G', div[1]]
                if request_url in url_table.keys():
                    if len(url_table[request_url]) < len(queries):
                        url_table[request_url] = queries
                else:
                    url_table[request_url] = queries
        if url.find("logout") != -1 or url.find("Logout") != -1 or url.find('LogOut') != -1:
            continue
        driver.get(url)
        time.sleep(1)
        try:
            driver.switch_to_alert().dismiss()
        except:
            "There is no alert"
        # url get방식으로 접속 후 해당 페이지에서 모든 form태그 요소를 수집
        forms = driver.find_elements_by_xpath("//form")
        time.sleep(0.1)
        for form in forms:
            if len(form.get_attribute('method')) == 3:
                form_params = ['G']
            else:
                form_params = ['P']
            try:
                action = form.get_attribute('action')
                if action.find('http') == -1 and action.find('https') == -1 and action.find('javascript')== -1:
                    # action 속성이 상대주소이고, javascript:()가 아닐 때
                    if action[0] != '/':
                        action_url = curr_domain + '/' + action
                    else:
                        action_url = curr_domain + action
                else:
                    action_url = action
                    if action.find('javascript') != -1 :
                        continue
                inputs = form.find_elements_by_xpath(".//input")
                time.sleep(0.1)
                for input in inputs:
                    name = input.get_attribute('name')
                    if len(name) == 0:
                        name = input.get_attribute('id')
                        if len(name) == 0:
                            name = input.get_attribute('type')
                            if len(name) == 0:
                                continue
                    if len(input.get_attribute('value')) > 0:
                        value = input.get_attribute('value')
                    else:
                        value = "USER_INPUT"
                    param = str(name) + "=" + str(value)
                    form_params.append(param)

                areas = form.find_elements_by_xpath(".//textarea")
                time.sleep(0.1)
                for area in areas:
                    name = area.get_attribute('name')
                    if len(name) == 0:
                        name = area.get_attribute('id')
                        if len(name) == 0:
                            continue
                    if len(area.get_attribute('value')) > 0:
                        value = area.get_attribute('value')
                    else:
                        value = "USER_INPUT"
                    param = str(name) + "=" + str(value)
                    form_params.append(param)

                selects = form.find_elements_by_xpath(".//select")
                time.sleep(0.1)
                for select in selects:
                    value = ""
                    name = select.get_attribute('name')
                    if len(name) == 0:
                        name = area.get_attribute('id')
                        if len(name) == 0:
                            continue
                    options = select.find_elements_by_xpath('.//option')
                    for option in options:
                        value = value + option.get_attribute('value') + "|"
                    param = name + "=" + "SELECT:" + value[0:len(value) - 1]
                    form_params.append(param)

                if action_url not in url_table.keys() or len(url_table[action_url]) <= 1:
                    url_table[action_url] = form_params

            except Exception as e:
                print(e)
                continue


    return url_table

# 점검대상페이지의 url을 입력받아 연결된 페이지 획득
def linked_page(url, table, driver):
    url_table = table
    domain_parse = re.compile('^https?:\/\/[^\/]+/')
    curr_domain = domain_parse.search(url).group()
    driver.get(url)
    try:
        driver.switch_to_alert().dismiss()
    except:
        "There is no alert"
    scripts = driver.find_elements_by_xpath('//*')
    # 현재 페이지에서 display : none 옵션을 전부 block으로 바꿈
    for script in scripts:
        try:
            driver.execute_script("arguments[0].style.display = 'block';", script)
        except Exception:
            continue
    # url get방식으로 접속 후 해당 페이지에서 모든 form태그 요소를 links
    forms = driver.find_elements_by_xpath("//form")
    for form in forms:
        form_params = []
        try:
            method = form.get_attribute('method')
            # method가 get, Get, GET의 모든 경우에 대해서 GET, POST 구분할 수 있도록 길이로 구분
            if len(method) == 3:
                method = "G"
                form_params.append(method)
            else:
                method = "P"
                form_params.append(method)

            # form의 정보를 요청으로 보낼 주소
            action = form.get_attribute('action')
            # action이 상대주소일 경우
            if action.find('http') == -1 and action.find('https') == -1:
                action_url = str(curr_domain) + str(action)
            else:
                action_url = action

            # action_url의 도메인이 현재 도메인과 같다면
            if curr_domain == domain_parse.search(action_url).group():
                inputs = form.find_elements_by_xpath(".//input")
                for input in inputs:
                    name = input.get_attribute('name')
                    if len(name) == 0:
                        name = input.get_attribute('id')
                        if len(name) == 0:
                            continue
                    if len(input.get_attribute('value')) > 0:
                        value = input.get_attribute('value')
                    else:
                        value = "USER_INPUT"
                    param = str(name) + "=" + str(value)
                    form_params.append(param)
                # action_url이 url_table의 keys에 없거나 파라미터 정보가 없는 경우 url_table에 추가
                if action_url not in url_table.keys() or len(url_table[action_url]) == 1:
                    url_table[action_url] = form_params

        except Exception as e:
            print(e)
            continue
    # url에 get방식으로 접속 후 해당 페이지에서 모든 a태그 요소를 links
    links = driver.find_elements_by_xpath("//a")
    for link in links:
        try:
            href = link.get_attribute('href')
            # href에 절대 URL이 적혀있다면
            if href.find("https") != -1 or href.find("http") != -1:
                domain = domain_parse.search(href).group()
                if domain == curr_domain:
                    # GET 방식일 경우
                    if href.find("?") != -1:
                        if href not in url_table.keys():
                            url_table[href] = ["G"]
                    # POST 방식일 경우
                    else:
                        if href not in url_table.keys():
                            url_table[href] = ["P"]

            # href에 상대 URL이 적혀있다면
            else:
                relative_url = str(url) + str(href)
                # GET 방식일 경우
                if relative_url.find("?") != -1:
                    if relative_url not in url_table.keys():
                        url_table[relative_url] = ["G"]
                # POST 방식일 경우
                else:
                    if relative_url not in url_table.keys():
                        url_table[relative_url] = ["P"]

        except Exception:
            continue
    # 멀티프로세싱 적용
    for i in url_table.keys():
        print("URL:", i)
        print("parameter:", url_table[i])
    num_core = multiprocessing.cpu_count() # 코어 개수
    manager = Manager()
    test_table = manager.dict()
    for url in url_table.keys():
        test_table[url] = url_table[url]
    input_data = np.array_split(test_table.keys(), num_core)
    parmap.map(get_param, input_data, test_table, pm_pbar=True, pm_processes=int(num_core/4))
    url_table = test_table
    return url_table

# 파라미터 정보까지 수집한 url_table을 사용해서 워드리스트에 있는 공격코드를 각 파라미터에 대입
# 각 공격에 대한 요청 길이를 표준화하여 z_score가 +- 3보다 큰 경우 이상반응(성공)으로 간주함
def fuzzing(keys, url_table, attack_info):
    driver = get_driver()
    #lists = keys.tolist() # 프로세스에게 할당된 url
    lists = keys
    cookies = driver.get_cookies()
    f = open("Payload/Payload.TXT", 'r')
    Payloads = f.readlines()
    f.close()
    with requests.Session() as s:
        # s에 쿠키 세팅
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        # url_table에 수집된 URL마다
        for url in lists:
            data = {}
            succeed = 0
            param_payload = {}
            if len(url_table[url]) <= 1:
                continue
            method = url_table[url][0]
            # url_table의 파라미터 정보를 data 딕셔너리에 삽입
            # data = { 'name' : 'value' ... }
            for parameter in url_table[url][1:]:
                name = parameter[0:parameter.find('=')]
                if len(parameter)-1 == parameter.find('='):
                    value = ""
                else:
                    value = parameter[parameter.find('=') + 1:]
                data[name] = value
            # 파라미터에 Payload 입력해서 퍼징 돌린 후엔 원래 값(origin_param)으로 파라미터 값을 바꿔 준 후 다음 파라미터를 공격해야 함
            if method == 'P':
                for param in data.keys():
                    succeed_flag = False
                    cnt = 0
                    temp = {}
                    temp['SQL_Injection'] = []
                    temp['Command_Injection'] = []
                    attack_log = {}
                    select_param = {}
                    origin_param = data[param]
                    if param == 'SUBMIT':
                        continue
                    if data[param].find('SELECT:') != -1:
                        select_param[param] = data[param][data[param].find('SELECT:')+7:]
                    # 파라미터 하나에 워드리스트만큼 반복
                    for Payload in Payloads:
                        cnt += 1
                        # station=SELECT:aaa|bbb|ccc, SELECT 타입의 경우 임의의 선택값의 뒤에 페이로드가 붙을 수 있도록 아래의 경우 data[param] = 'aaa' + Payload
                        if param in select_param.keys():
                            data[param] = select_param[param].split('|')[0] + Payload.replace("\n", "")
                        else:
                            data[param] = Payload.replace("\n", "")
                        request_url = url
                        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
                        res = s.post(request_url, data=data, headers=header)
                        time.sleep(0.05)
                        html = res.text
                        res_char = len(html)
                        if cnt == 1: # Payload가 qwerasdfzxcv 일 때
                            common_res = res_char
                            continue
                        if cnt == 2: # Payload가 qwerasdfzxcv0 일 때
                            diff = res_char-common_res # diff는 Payload 길이 12를 기준으로 한 글자 당 응답 길이의 변화량, Payload 길이가 14라면 common_res + 2diff
                            continue
                        attack_log[str(data)] = res_char - (diff * len(Payload))
                    # Payload 전부 돌리고, 공격 성공 판별
                    data[param] = origin_param
                    values = list(map(int, attack_log.values()))
                    avg = np.mean(values) # 응답 길이의 평균
                    std = np.std(values) # 응답 길이의 표준편차
                    if std != 0:
                        if std < 10:
                            std = 10 # 표준편차가 너무 작을 경우 미세한 글자수 변화에도 반응하기 때문에 최소한 10을 유지
                        log_num = 1
                        for p in attack_log.keys():
                            z_score = (attack_log[p] - avg)/std
                            # 특이점 발견 z_score +- 3
                            if z_score > 3 or z_score < -3:
                                if 1 <= log_num <= 52:
                                    temp['SQL_Injection'].append(p)
                                else:
                                    temp['Command_Injection'].append(p)
                                succeed_flag = True
                            log_num += 1
                    if succeed_flag == True:
                        succeed += 1
                    param_payload[param] = temp
            # method = 'G'
            else:
                # url의 파라미터 정보에서 조작할 파라미터 하나를 선택
                for param in data.keys():
                    succeed_flag = False
                    cnt = 0
                    temp = {}
                    temp['SQL_Injection'] = []
                    temp['Command_Injection'] = []
                    attack_log = {}
                    origin_param = data[param]
                    for Payload in Payloads:
                        cnt += 1
                        data[param] = Payload.replace("\n", "")
                        query = ""
                        for p in data.keys():
                            query += str(p) + '=' + str(data[p]) + '&'
                        query = query[:len(query)-1]
                        query = requests.utils.quote(query)
                        request_url = url + '?' + query
                        header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
                        res = s.get(request_url, headers=header)
                        time.sleep(0.05)
                        html = res.text
                        res_char = len(html)
                        if cnt == 1: # Payload가 qwerasdfzxcv 일 때
                            common_res = res_char
                            continue
                        if cnt == 2: # Payload가 qwerasdfzxcv0 일 때
                            diff = res_char-common_res # diff는 Payload 길이 12를 기준으로 한 글자 당 응답 길이의 변화량, Payload 길이가 14라면 common_res + 2diff
                            continue
                        attack_log[str(data)] = res_char - (diff * len(Payload))
                    data[param] = origin_param
                    values = list(map(int, attack_log.values()))
                    avg = np.mean(values)  # 응답 길이의 평균
                    std = np.std(values)  # 응답 길이의 표준편차
                    if std != 0:
                        if std < 10:
                            std = 10 # 표준편차가 너무 작을 경우 미세한 글자수 변화에도 반응하기 때문에 최소한 10을 유지
                        log_num = 1
                        for p in attack_log.keys():
                            z_score = (attack_log[p] - avg) / std
                            # 특이점 발견 z_score +- 3
                            if z_score > 3 or z_score < -3:
                                if 1 <= log_num <= 52:
                                    temp['SQL_Injection'].append(p)
                                else:
                                    temp['Command_Injection'].append(p)
                                succeed_flag = True
                            log_num += 1
                    if succeed_flag == True:
                        succeed += 1
                    param_payload[param] = temp

            # INFO : ['http://localhost:8080/WebGoat/start.mvc#attack/101829144/1100', 'P', 2, 1, {'station': ["{'station': '1010 or 1=1', 'SUBMIT': 'Go!'}", "{'station': '101or 0=0 --', 'SUBMIT': 'Go!'}", "{'station': '101or 1=1--', 'SUBMIT': 'Go!'}"]}]
            info = [url, method, len(data.keys()), succeed, param_payload]
            attack_info.append(info)
        return attack_info

def Injection(url):
    url_table = {}
    url = url

    # 만약 링크가 https://naver.com 으로 주어진다면 https://naver.com/으로 변경
    if str(url)[-1] != '/':
        if str(url).count('/') == 2:
            url = str(url) + '/'

    # 웹드라이버 객체 선언
    driver = get_driver()
    # 연결된 페이지 URL 수집 및 파라미터 정보 수집
    url_table = linked_page(url, url_table, driver)
    for i in url_table.keys():
        print("URL:", i)
        print("param:", url_table[i])
    for i in url_table.keys():
        # 파라미터가 없는 경우 url_table에서 삭제
        if len(url_table[i]) <= 1:
            del(url_table[i])
    for url in url_table:
        print("URL:", url)
        print("Parameter:", url_table[url])
    print("삭제 후 URL 개수:", len(url_table))

    num_core = multiprocessing.cpu_count()
    # 만약 url_table의 크기가 가용할 수 있는 코어 수보다 적다면 코어 수 맞춤
    if len(url_table) < num_core:
        num_core = len(url_table)
    manager = Manager()
    # 멀티프로세싱에서 사용할 수 있도록 공유 딕셔너리 mul_table
    attack_info = manager.list()
    # url_table의 url을 나누어서 각 프로세스에 할당
    input_data = np.array_split(url_table.keys(), num_core)
    start=time.time()
    parmap.map(fuzzing, input_data, url_table, attack_info, pm_pbar=True, pm_processes=num_core)
    print("멀티프로세싱 경과시간: ", time.time()-start)


    my_client = MongoClient("mongodb://localhost:27017/")
    db = my_client['testdb']
    collection = db['test2']
    n = 1
    # 몽고디비 삽입
    for info in attack_info:
        Document = {}
        Document['Number'] = n
        Document['Page_URL'] = info[0]
        Document['vulname'] = 'Injection'
        if info[1] == 'P':
            Document['Method'] = 'POST'
        else:
            Document['Method'] = 'GET'
        Document['Parameters'] = info[2]
        Document['Suspicious Parameters'] = info[3]
        # payload = { p1 : { sql : p_load, cmd : p_load}, p2 : { sql : p_load, cmd : p_load } }
        payload = {'SQL_Injection' : [], 'Command_Injection' : []}
        for p_load in info[4].values():
            payload['SQL_Injection'] = payload['SQL_Injection'] + p_load['SQL_Injection']
            payload['Command_Injection'] = payload['Command_Injection'] + p_load['Command_Injection']
        Document['Payload'] = payload
        collection.insert_one(Document)
        n +=1
    # 파라미터 15, 페이로드 127 약 250초, 인터넷 속도 30~40
    # info = ['http://localhost:8080/WebGoat/start.mvc#attack/101829144/1100', 'P', 2, 1, \
    # {'station': ["{'station': '1010 or 1=1', 'SUBMIT': 'Go!'}", "{'station': '101or 0=0 --', 'SUBMIT': 'Go!'}", "{'station': '101or 1=1--', 'SUBMIT': 'Go!'}"]}]