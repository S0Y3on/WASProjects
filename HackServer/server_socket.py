import socket
import os ,sys
from time import sleep
from os.path import exists
from _thread import *

# 소켓 연결할때 서버쪽에서는 자신의 로컬 ip를 적어주더라구요 ..
HOST = '192.168.200.146'
PORT = 62162
filename = "/var/log/apache2/access.log"


def getMsg(client_socket) :
    msg = client_socket.recv(1024)
    return msg.decode('utf-8')

def sendMsg(client_socket, msg) :
    client_socket.send(msg)

def logReset() :
    os.system("echo "" > {}".format(filename))

def XXEResult(client_socket) :
    if not exists(filename) :
        print("Files does not exist\n")
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
        print("\n [complete] XXE\n -- %d")

def doSomething(client_socket, addr) :
    while True :
        try :
            request_type = getMsg(client_socket)
            if(request_type == "reset") :
                logReset()
            elif(request_type == "result") :
                XXEResult(client_socket)
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