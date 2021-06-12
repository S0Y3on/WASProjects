from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder

MONGOURL = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:"

# 이 부분이 compass 포트 번호 넣는 부분입니다!
MONGOPORT = 29500

# VM IP/DNS - Will depend on your VM
EC2_URL = '''ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com'''

# Mongo URI Will depende on your DocDB instances
DB_URI = '''mongodb://ubuntu:@ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com'''

# DB user and password
DB_USER = 'ubuntu'


class mongoManager :
    def __init__(self, url) -> None:
        # Create the tunnel
        server = SSHTunnelForwarder(
            (EC2_URL, 22),
            ssh_username=DB_USER,  # I used an Ubuntu VM, it will be ec2-user for you
            # 여기는 pem 파일 전체 경로 넣어주시면 됩니다
            ssh_pkey='/Users/HANSUNG/PycharmProjects/was_xss/ha.pem',  # I had to give the full path of the keyfile here
            remote_bind_address=(DB_URI, 27017),
            local_bind_address=('127.0.0.1', 27017)
        )
        # Start the tunnel
        print('SSH server start!')

        # db 연결 끝나는 부분에 server.close()도 넣어 줘야 하는데 어디 부분일지 몰라서... 나중에 참고 해주세요!
        server.start()
        client = MongoClient(host='127.0.0.1', port=MONGOPORT)
        self.coll = client['WAS']['test']

    def caseAccessControl(self) -> dict :
        datas = self.coll.find({"vulname": "Broken Access Control"})
        if datas.count() < 1 :
            datas = {
                {
                    "vulname" : None,
                    "Type" : None,
                    "adminpage_Destination" : None,
                    "adminpage_Info" : None,
                    "adminpage_Success" : 0,
                    "adminpage_Fail" : 0
                },
                {
                    "vulname" : None,
                    "Type" : None,
                    "dictpage_Destination" : None,
                    "dictpage_Info" : None,
                    "dictpage_Success" : 0,
                    "dictpage_Fail" : 0
                },
                {
                    "vulname" : None,
                    "Type" : None,
                    "logincount_TargetPage" : None,
                    "logincount_Count" : None,
                    "logincount_Policy" : 0,
                    "logincount_Time" : 0
                }
            }
        return datas
    def craftAccessControl(self, datas) -> dict :
        dict_table = []
        admin_table = []
        login_chart = []
        target_urls = []
        login_counts = []
        for data in datas :
            admin_shape = {
                "adminpage_Destination": None,
                "adminpage_Info": None,
                "adminpage_Success": 0,
                "adminpage_Fail": 0
            }
            login_shape = {
                "logincount_TargetPage": None,
                "logincount_Count": None,
                "logincount_Policy": 0,
                "logincount_Time": 0
            }
            dict_shape = {
                "dictpage_Destination": None,
                "dictpage_Info": None,
                "dictpage_Success": 0,
                "dictpage_Fail": 0
            }
            if data["Type"] != None :
                if data["Type"] == "dictpage" :
                    dict_shape["dictpage_Destination_Page"] = data["dictpage_Destination_Page"]
                    dict_shape["dictpage_Info"] = data["dictpage_Info"]
                    dict_shape["dictpage_Success"] = data["dictpage_Success"]
                    dict_shape["dictpage_Fail"] = data["dictpage_Fail"]
                    dict_table.append(dict_shape)
                elif data["Type"] == "logincount" :
                    login_shape["logincount_TargetPage"] = data["logincount_TargetPage"][8 + data["logincount_TargetPage"][8:].find('/'):]
                    login_shape["logincount_Count"] = data["logincount_Count"]
                    login_shape["logincount_Policy"] = data["logincount_Policy"]
                    login_shape["logincount_Time"] = data["logincount_Time"]
                    target_urls.append(login_shape["logincount_TargetPage"])
                    login_counts.append(int(data["logincount_Count"]))
                    login_chart.append(login_shape)
                elif data["Type"] == "adminpage" :
                    admin_shape["adminpage_Destination_Page"] = data["adminpage_Destination Page"]
                    admin_shape["adminpage_Info"] = data["adminpage_Info"]
                    admin_shape["adminpage_Success"] = data["adminpage_Success"]
                    admin_shape["adminpage_Fail"] = data["adminpage_Fail"]
                    admin_table.append(admin_shape)
        if len(dict_table) < 1 : 
            dict_table.append(dict_shape)
        if len(login_chart) < 1 :
            login_chart.append(login_shape)
        if len(admin_table) < 1 : 
            admin_table.append(admin_shape)
        return {"dict_table" : dict_table, "admin_table" : admin_table, "login_chart" : login_chart, "target_urls": target_urls, "login_counts":login_counts}
    def caseInjection(self) -> dict :
        datas = self.coll.find({"vulname": "Injection"})
        print(datas)
        if datas.count() < 1 :
            datas = {
                "Page_URL" : None,
                "vulname" : None,
                "Method" : None,
                "Parameters" : None,
                "Suspicious Parameters" : None,
                "Payload" : None
            }
        return datas

    def craftInjection(self, datas) -> dict :
        injection_charts = {
            "urls" : [],
            "parameters" : [],
            "suspicious_parameters" : [],
            "number":[],
        }
        injection_tables = []
        table = {
            'Method' : None,
            'Page_URL' : None,
            'Parameters' : None,
            'Suspicious_Parameters' : None,
            'Payload' : None
        }
        for data in datas :
            if data["vulname"] != None :
                table["Method"] = data["Method"]
                table["Page_URL"] = data["Page_URL"]
                table["Parameters"] = data["Parameters"]
                table["Suspicious Parameters"] = data["Suspicious Parameters"]
                table["Payload"] = data["Payload"]
                injection_charts["urls"].append(table["Page_URL"])
                injection_charts["parameters"].append(table["Parameters"])
                injection_charts["suspicious_parameters"].append(table["Suspicious Parameters"])
                injection_charts["number"].append(data['Number'])
        if len(injection_tables) < 1 :
            injection_tables.append(table)
        return {"injection_charts" : injection_charts, "injection_tables" : injection_tables}

    def caseXSS(self) -> dict :
        datas = self.coll.find({"vulname": "XSS"})
        if datas.count() < 1 :
            datas = {
                "vulname" : None,
                "method" : None,
                "url" : None,
                "isHack" : None, 
                "totalHack" : None,
                "XssType" : None,
                "hackCode" : None,
                "timpestamp" : None
            }
        return datas
    def craftXSS(self, datas) -> dict :
        chartTotcnt = {
            "tot_try" : 0,
            "tot_success" : 0 
        }
        chartClassification = {
            "stored" : 0,
            "reflect" : 0
        }
        tableRes = []

        for data in datas :
            res = {
                "method": None,
                "URL": None,
                "TotalAttack": None,
                "SucceedAttack": None,
                "AttackCode": None,
                "SucceedAttackRate": None,
            }

            if data["vulname"] != None :
                chartTotcnt["tot_try"] += data["totalHack"]
                if data["isHack"] :
                    if data["XssType"] == "Stored":
                        chartClassification["stored"] += 1
                        res["XssType"] = "Stored"
                    else:
                        chartClassification["reflect"] += 1
                        res["XssType"] = "Reflect"

                    res["method"] = data["method"]
                    res["URL"] = data["url"]
                    res["TotalAttack"] = data["totalHack"]
                    res["AttackCode"] = data["hackCode"]
                    res["SucceedAttack"] = len(data["hackCode"])
                    res["SucceedAttackRate"] = round(len(data["hackCode"]) / int(data["totalHack"]), 4) * 100

                    chartTotcnt["tot_success"] = res["SucceedAttack"]
            tableRes.append(res)
        return {"charTotcnt" : chartTotcnt, "charClassification" : chartClassification, "tableRes" : tableRes}

    def caseXXE(self) -> dict:
        datas = self.coll.find({"vulname": "XXE"})
        if datas.count() < 1:
            datas = {
                "vulname": None,
                "type": None,
                "url": None,
                "isHack": None,
                "totUse": None,
                "content": None
            }
        return datas

    def craftXXE(self, datas) -> dict:
        gen_chart = {
            'success': 0,
            'fail': 0
        }
        oob_chart = {
            'success': 0,
            'fail': 0
        }
        gen_tables = []
        oob_tables = []

        for data in datas:
            gen_table = {
                'url': None,
                'totUse': None,
                'content': None
            }
            oob_table = {
                'url': None,
                'totUse': None,
                'content': None
            }
            if data["vulname"] != None:
                if data["type"] == "GEN":
                    if data["isHack"]:
                        gen_chart["success"] += 1
                    else:
                        gen_chart["fail"] += 1
                    gen_table["url"] = data["url"]
                    gen_table["totUse"] = data["totUse"]
                    gen_table["content"] = data["content"]
                    gen_tables.append(gen_table)
                else:
                    if data["isHack"]:
                        oob_chart["success"] += 1
                    else:
                        oob_chart["fail"] += 1
                    oob_table["url"] = data["url"]
                    oob_table["totUse"] = data["totUse"]
                    oob_table["content"] = data["content"]
                    oob_tables.append(oob_table)
        if len(gen_tables) < 1:
            gen_tables.append(gen_table)
        if len(oob_tables) < 1:
            oob_tables.append(oob_table)
        return {"gen_chart": gen_chart, "oob_chart": oob_chart, "gen_tables": gen_tables, "oob_tables": oob_tables}

    def caseAuthentication(self) -> dict :
        data = self.coll.find({"vulname": "Broken Authentication"})
        print(data.count())
        if data.count() < 1 :
            data = {
                "vulname" : None,
                "accesstime" : None,
                "name" : None,
                "value" : None,
                "sourceIP" : None,
                "loginIP" : None,
                "max-age" : None,
                "expires" : None,
                "secure" : None,
                "discard" : None,
                "httponly" : None,
                "samesite" : None
            }
        return data
    def craftAuthentication(self, datas) -> dict :
        data = datas[0]
        table = {
            "SessionID" : data["value"],
            "SourceIP" : data["source_ip"],
            "LoginedIP" : data["logined_ip"],
            "Secure" : data["secure"],
            "Discard" : data["discard"],
            "HTTPOnly" : data["httponly"],
            "samesite" : data["samesite"]
        }

        data["max-age"] = 0 if data["max-age"] is None else data["max-age"]

        chart = {
            "Standard" : 600,
            "Target" : data["max-age"],
            "Expires" : data["expires"]
        }
        return {"table" : table, "chart" : chart}
    def searchDB(self) -> dict :
        data = {
            "XXE": self.craftXXE(self.caseXXE()),
            "Injection": self.craftInjection(self.caseInjection()),
            "XSS": self.craftXSS(self.caseXSS()),
            "Authentication": self.craftAuthentication(self.caseAuthentication()),
            "AccessControl": self.craftAccessControl(self.caseAccessControl())
        }
        return data

    def testSample(self) :
        print(2)
        self.coll.find_one(filter={'valname':"XXE"}, no_cursor_timeout=False)
        print(3)
        return None