# Injection



## dependency
 1. selenium
 2. seleniumrequests
 3. parmap
 4. pymongo
 5. requests

## 실행
 python Injection.py -url {url} -l -id {id} -pw {pw} -login {login}

 * -url : 대상 사이트의 홈 URL
 * -l : URL에 접근하기 위해 로그인 인증이 필요한 지 여부 (default = False)
 * -id : 로그인 인증 필요 시 id
 * -pw : 로그인 인증 필요 시 pw
 * -login : 로그인 인증 필요 시 인증 페이지 URL

## P.S
 * 현재 로그인 기능 막아두었음
 * 테스트는 http://demo.testfire.net/ , http://testphp.vulnweb.com/ 에서 진행하였음