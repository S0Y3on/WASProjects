from XSS import xss


def XSSPoint(url, user, coll):
    try:
        run = xss.XssFuzzer(url, user)

        # href 파서 (return list)
        Href = run.findHref()

        # 프로그램 실행
        run.insertAttackCode(Href, coll)
        print('Success')
    except:
        print("Error")


if __name__ == '__main__':
    url, id, passwd = input('사용자 입력 값 : ').split()
    user = {
        'login': id,
        'password': passwd
    }
    XSSPoint(url, user)
