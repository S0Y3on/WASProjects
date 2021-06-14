import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

from Injection import Injection
from XSS import manage
from XXE import xxe
from AccessControl import main
from BrokenAuthentication import BrokenAuthentication
import socket
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

MONGOURL = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:"
MONGOPORT = "27017"

def conATK() :
    ATTACKSERVER = "172.17.0.3"
    ATTACKPORT = 1000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ATTACKSERVER, ATTACKPORT))
    return client_socket


# parser
def findHref(url):
    # 검사하는 url에서 이동할 수 있는 href 찾기
    href_link = []

    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'html.parser')

    for link in bs.findAll('a'):
        # 이동할 수 있는 url이 있는 경우
        if 'href' in link.attrs:
            href_link.append(url + link.attrs['href'])
        else:
            print("No Hyperlink Link")

    for link in bs.findAll('form'):
        if 'action' in link.attrs:
            href_link.append(url + link.attrs['action'])
        else:
            print("No form tag")
    return href_link


def startApp(url : str, tools : list, user : dict) :
    client = MongoClient(MONGOURL+MONGOPORT)
    db = client['WAS']
    coll = db[url]
    atk = conATK()
    for tool in tools :
        if tool == "XSS" :
           manage.XSSPoint(url, user, coll)
        elif tool == "Injection":
            Injection.Injection(url, coll)
        elif tool == "XXE" :
            xxe.XXEPOINT(findHref(url), coll, atk)
        elif tool == "Broken Access Control" :
            main.accPoint(coll, url, user)
        elif tool == "Broken Authentication" :
            BrokenAuthentication.brokenAuthentication(url, user)
    atk.close()
    return True

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    startApp()


