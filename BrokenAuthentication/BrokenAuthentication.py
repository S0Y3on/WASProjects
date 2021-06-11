import requests.cookies
import requests
from bs4 import BeautifulSoup
import requests.utils
import re
from pymongo import MongoClient
from pymongo.cursor import CursorType
import socket
import datetime



class DBHandler:
    def __init__(self):
        host = "127.0.0.1"
        port = "29675"
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
        result = self.client[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True, \
                                                            cursor_type=CursorType.EXHAUST)
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




if __name__ == "__main__" :
    #url입력
    userUrl = (input("url : "))

    #타겟페이지 접속
    access = requests.get(userUrl)


    #main page에서 loginpage 추출
    pagesoup = BeautifulSoup(access.text, 'html.parser')
    parse = pagesoup.select("a[href*='login']")
    for b in parse :
        href = b.attrs['href'] #accounts/login/

    loginpage = userUrl+href #accounts/login 페이지!


    #header 정보입력
    headers = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/90.0.4430.85 Safari/537.36',
   'Referer': loginpage
    }


    #login 페이지 login/password 입력칸 찾기
    t= requests.get(loginpage)
    loginsoup = BeautifulSoup(t.text,'html.parser')
    x = loginsoup.select("input[type*='text']")
    for y in x:
        reqid = y.attrs['name'] #대상 페이지의 id입력칸 name = "login"

    z = loginsoup.select("input[type*='password']")
    for f in z :
        reqpw = f.attrs['name'] # 대상 페이지의 pw입력칸 name = "password"


    #유저 id pw 입력
    userID = (input("ID : "))
    userPW = (input("PW : "))


    #post requests data 완성
    payload = {
        reqid : userID,
        reqpw : userPW
    }


    #post request process
    req = requests.get(userUrl+href)
    session = requests.session()
    login = session.post(userUrl + href, headers = headers, \
                    data=payload)
    response = session.get(userUrl)


    # 대상 웹페이지가 사용하고 있는 세션id 이름을 파싱
    r = session.cookies.keys()
    for value in r:
        if 'id' in value:
            rr = session.cookies.get(value)

    #sessionid = (value)
    result = (value + "=" + rr)



    #user's data for attacker server
    data = {
        'url' : userUrl,
        'sessionID' : result
    }

    # showing sessionid Settings
    def makeCookieDict(data):
        cookie_dict = {}
        data = data.split('Cookie(')[2].split(')')[0]
        data = data.split(', ')
        for i in data:
            if '{' in i:
                i = i.split('{')[1]
            elif '}' in i:
                i = i.replace('}','')
            i = i.replace('\'', '')
            i = re.split(r':|=', i)
        #print(i)
            cookie_dict[i[0]] = i[1]
        return cookie_dict
    #cookie_dict는 전체 설정값
    cookie_dict = makeCookieDict(str(session.cookies.keys))
    if 'maxAge' not in cookie_dict.keys():
        cookie_dict['maxAge'] = cookie_dict.get('maxAge', )


    '''
    print("<"+userID+"'s Session Settings>")
    for key, value in cookie_dict.items():
    print(' ' + key + " = " + value)
    '''

    #access time
    access_time = datetime.datetime.utcnow()


    #source ip
    source = socket.gethostbyname(socket.getfqdn())

    #logined ip
    #logined_ip =


    #ui에 표출할 특정 값 골라내기 + vulname 구별
    data = {
        'vulname' : 'Broken Authentication',
        'access_time' : access_time,
        'name' : cookie_dict['name'],
        'value' : cookie_dict['value'],
        'source_ip' : source,
        'logined_ip' : '',
        'max-age' : cookie_dict['maxAge'],
        'expires' : cookie_dict['expires'],
        'secure' : cookie_dict['secure'],
        'discard' : cookie_dict['discard'],
        'httponly' : cookie_dict['HttpOnly'],
        'samesite' : cookie_dict['SameSite'],
    }

    print(data)
    f = open('Broken_Authentication.txt', 'w')
    f.write(userUrl + '\n' + result + '\n' + str(data))
    f.close()




    #mongodb 연결
    my_client = MongoClient("mongodb://127.0.0.1:29675/")
    print(my_client)

    #insert dict to mongo
    db = my_client['WAS']
    collection = db['test']
    collection.insert_one(data)



