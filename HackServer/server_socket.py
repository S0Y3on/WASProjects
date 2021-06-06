import socket
import os ,sys
import requests
from bs4 import BeautifulSoup
from time import sleep
from os.path import exists
from _thread import *

HOST = ''
PORT = ""
filename = "/var/log/apache2/access.log"

def getMsg(client_socket : socket) :
    msg = client_socket.recv(1024)
    return msg.decode('utf-8')

def sendMsg(client_socket : socket, msg : str) :
    client_socket.send(msg)

def logReset() :
    os.system("echo "" > {}".format(filename))

def XXEResult(client_socket : socket) :
    if not exists(filename) :
        print("FILE ERROR\n")
    else :
        with open(filename, 'rb') as f:
            try:
                data = f.read(1024)
                while data:
                    sendMsg(client_socket, data)
                    data = f.read(1024)
            except Exception as e:
                print(e)
        if getMsg(client_socket) :
            sendMsg(client_socket, "end".encode("utf-8"))

def getSessionID(cookies : tuple):
    try:
        with open('sessionid.txt', 'r') as file:
            global url
            url = file.readline().strip('\n')
            sessionID = file.readline()
            cookies[sessionID.split('=')[0]] = sessionID.split('=')[1]
    except Exception as e:
        print(e)

def connectSession(url : list, cookies : tuple):
    login_id = str()
    if cookies:
        session = requests.Session()
        response = session.post(url=url, cookies = cookies )
        try:
            login_result = str(BeautifulSoup(response.text, 'html.parser').find_all('p')[0])
            login_id = login_result.split(' ')[2]
            return True
        except Exception as e:
            print(e)

def brokenAuthentication(urls) :
    cookies = getMsg()
    getSessionID(cookies)
    connectSession(urls, cookies)

def doSomething(client_socket, addr) :
    #테스트시 아래 urls에 list형식으로 데이터 저장후에 이용
    urls = []
    while True :
        try :
            request_type = getMsg(client_socket)
            if(request_type == "reset") :
                logReset()
            elif(request_type == "result") :
                XXEResult(client_socket)
            elif(request_type == "broken") :
                brokenAuthentication(urls)
        except ConnectionResetError as e :
                print('Disconnected by ' + addr[0],':',addr[1])
                break
    client_socket.close()

if __name__ == "__main__" : 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True :
        try :
            client_socket, addr = server_socket.accept()
            print("new client Connected : {}\n".format(addr))
            start_new_thread(doSomething, (client_socket, addr))
        except socket.error as err:
            client_socket.close()
            print("Socket Error Detected : {}, {}\n".format(addr, err))
        except KeyboardInterrupt as key :
            server_socket.close()