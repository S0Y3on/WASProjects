import datetime

from django.shortcuts import render
from django.http import Http404
from .mongoManager import *
import sys
sys.path.insert(0,'/root/WASProjects/')
from main import startApp
# Create your views here.

def error(req) :
    return Http404("Not Found")

def home(req) :
    return render(req, "index.html")

def input(req) :
    return render(req, 'input.html')

def check(req) :
    return render(req, 'check.html')
    
def idpw(req) :
    return render(req, 'idpw.html')

def res(req) :
    return render(req, 'res.html')

def getURL(req) :
    url = ''
    if req.method == "POST" :
        url = req.POST.get("url")
    return render(req, 'check.html', {'url' : url})

def selectTools(req) :
    idpw = True
    isEmpty = True
    user = {
        "id" : '',
        "password" : ''
    }
    if req.method == "POST" :
        tools = req.POST.getlist("tools")
        url = req.POST.get("url")
        if len(tools) >= 1 :
            isEmpty = False
        if not isEmpty and (tools[-1] == "XXE" or tools[-1] == "Injection") :
            idpw = False
    if not isEmpty :
        if idpw :
            return render(req, 'idpw.html', {'tools' : tools, 'url' : url})
        else :
            startApp(url, tools, user)
            data = mongoManage(url)
            return render(req, 'res.html', {'tools' : tools, 'data' : data})
    else :
        return render(req, 'check.html')

def getIDPW(req) :
    user = {
        "id" : '',
        "password" : ''
    }
    url = ''
    tools = []
    data = {}
    if req.method == "POST":
        user["id"] = req.POST.get("id")
        user["password"] = req.POST.get("pw")
        url = req.POST.get("url")
        tools = req.POST.getlist("tools")
    print(1)
    if user["id"] != '' and user["password"] != '':
        startApp(url, tools, user)
        datas = mongoManage(url)
        # datas = {'XXE': None, 'Injection': {'injection_charts': {'urls': ['http://testphp.vulnweb.com/search.php?test=query', 'http://testphp.vulnweb.com/guestbook.php', 'http://testphp.vulnweb.com/userinfo.php'], 'parameters': [2, 3, 3], 'suspicious_parameters': [0, 0, 2]}, 'injection_tables': [{'Method': 'POST', 'Page_URL': 'http://testphp.vulnweb.com/userinfo.php', 'Parameters': 3, 'Suspicious_Parameters': None, 'Payload': {'uname': {'SQL_Injection': ['{\'uname\': "\' or 0=0 #", \'pass\': \'USER_INPUT\', \'submit\': \'login\'}', '{\'uname\': "\' or 1=1 or \'\'=\'", \'pass\': \'USER_INPUT\', \'submit\': \'login\'}', '{\'uname\': "x\' or 1=1 or \'x\'=\'y", \'pass\': \'USER_INPUT\', \'submit\': \'login\'}'], 'Command_Injection': []}, 'pass': {'SQL_Injection': ['{\'uname\': \'USER_INPUT\', \'pass\': "\' or 0=0 #", \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': \'"\\\' or 1 --\\\'"\', \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': "\' or 1=1 or \'\'=\'", \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': "hi\' or \'a\'=\'a", \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': "\' or uname like \'%", \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': "\' or \'\'=\'", \'submit\': \'login\'}', '{\'uname\': \'USER_INPUT\', \'pass\': "x\' or 1=1 or \'x\'=\'y", \'submit\': \'login\'}'], 'Command_Injection': []}, 'submit': {'SQL_Injection': [], 'Command_Injection': []}}, 'Suspicious Parameters': 2}]}, 'XSS': {'charTotcnt': {'tot_try': 28, 'tot_success': 10}, 'charClassification': {'stored': 0, 'reflect': 2}, 'tableRes': [{'method': 'GET', 'URL': 'http://soy3on.pythonanywhere.com/post_search', 'Total Attack': 14, 'Succeed Attack': 10, 'Attack Code': ['>"<script>alert(\'XSS\');</script>', "<script>alert('XSS')</script>", '<svg/whatthe=""onload=alert(\'XSS\')>', '"\'><svg/whatthe=""onload=alert(\'XSS\')>', "<script>alert('XSS')</script>", "<img src=0 onerror=alert('XSS')>", "<svg/onload=alert('XSS')>", "<body data-rsssl=1 onload=alert('XSS')>", '<iframe src="javascript:alert(\'XSS\')"></iframe>', '<details/open/ontoggle=a=alert,a("XSS")>']}, {'method': 'GET', 'URL': 'http://soy3on.pythonanywhere.com/post_search', 'Total Attack': 14, 'Succeed Attack': 10, 'Attack Code': ['>"<script>alert(\'XSS\');</script>', "<script>alert('XSS')</script>", '<svg/whatthe=""onload=alert(\'XSS\')>', '"\'><svg/whatthe=""onload=alert(\'XSS\')>', "<script>alert('XSS')</script>", "<img src=0 onerror=alert('XSS')>", "<svg/onload=alert('XSS')>", "<body data-rsssl=1 onload=alert('XSS')>", '<iframe src="javascript:alert(\'XSS\')"></iframe>', '<details/open/ontoggle=a=alert,a("XSS")>']}]}, 'Authentication': {'table': {'Session ID': 'q5eezg30x49e9z98t31hqjwgta5odifn', 'Source IP': '192.168.25.1', 'Logined IP': '', 'Secure': 'False', 'Discard': 'True', 'HTTP Only': ' None', 'samesite': ' Lax'}, 'chart': {'Standard': 600, 'Target': None, 'Expires': 'None'}}, 'AccessControl': {'dict_table': [{'dictpage_Destination': None, 'dictpage_Info': ['Indy_admin', 'admin', 'banneradmin', 'bbadmin', 'bigadmin', 'ccp14admin', 'cmsadmin', 'directadmin', 'ezsqliteadmin', 'fileadmin', 'globes_admin', 'hpwebjetadmin', 'irc-macadmin', 'logo_sysadmin', 'macadmin', 'myadmin', 'newsadmin', 'openvpnadmin', 'pgadmin', 'phpldapadmin', 'phpmyadmin', 'phppgadmin', 'pureadmin', 'sql-admin', 'sshadmin', 'staradmin', 'sys-admin', 'sysadmin', 'ur-admin', 'useradmin', 'vmailadmin', 'webadmin', 'wizmysqladmin', 'wp-admin'], 'dictpage_Success': 34, 'dictpage_Fail': 473, 'dictpage_Destination_Page': 'https://soy3on.pythonanywhere.com'}], 'admin_table': [{'adminpage_Destination': None, 'adminpage_Info': ['/'], 'adminpage_Success': 1, 'adminpage_Fail': 32, 'adminpage_Destination Page': 'https://soy3on.pythonanywhere.com/admin/login/?next=/admin/'}], 'login_chart': [{'logincount_TargetPage': 'https://soy3on.pythonanywhere.com/accounts/login/', 'logincount_Count': 6, 'logincount_Policy': 'O', 'logincount_Time': datetime.datetime(2021, 6, 10, 11, 55, 5, 852000)}, {'logincount_TargetPage': 'https://soy3on.pythonanywhere.com/accounts/login/', 'logincount_Count': 6, 'logincount_Policy': 'O', 'logincount_Time': datetime.datetime(2021, 6, 10, 11, 55, 5, 852000)}]}}

        data['tools'] = tools
        data['XXE'] = datas['XXE']
        data['Injection'] = datas['Injection']
        data['XSS'] = datas['XSS']
        data['Authentication'] = datas['Authentication']
        data['AccessControl'] = datas['AccessControl']

        # print(data['Injection'])
        return render(req, 'res.html', data)
    return render(req, 'idpw.html')

def mongoManage(url) :
    coll = mongoManager(url)
    data = coll.searchDB()
    # asdf = coll.testSample()
    # print(data)
    print(4)
    # data = {}
    return data