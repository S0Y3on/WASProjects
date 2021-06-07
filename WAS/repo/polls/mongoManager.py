from pymongo import MongoClient

MONGOURL = "ec2-54-180-116-84.ap-northeast-2.compute.amazonaws.com:"
MONGOPORT = 27017

class mongoManager :
    def __init__(self, url) -> None:
        client = MongoClient(host=MONGOURL, port=MONGOPORT)
        self.coll = client['WAS'][url]

    def caseAccessControl(self, index) -> dict :
        pass

    def caseInjection(self, index) -> dict :
        pass

    def caseXSS(self, index) -> dict :
        pass

    def caseXXE(self, index) -> dict :
        pass

    def caseAuthentication(self, index) -> dict :
        pass

    def searchDB(self, index) -> dict :
        data = None
        if index == "XXE" :
            data = caseXXE(index)
        elif index == "Injection" : 
            data = caseInjection(index)
        elif index == "XSS" : 
            data = caseXSS(index)
        elif index == "Broken Autentication" : 
            data = caseAuthentication(index)
        elif index == "Broken Access Control" : 
            data = caseAccessControl(index)
        return data