def kulasis_login_get_api_keys(ecs_id, password):
    return

# import json
# from bs4 import BeautifulSoup
# import urllib.parse
# import requests
# 
# 
# # kulasis api によるお知らせ，メールの取得
# # アクセスに必要なキーの取得
# def kulasis_login_get_api_keys(ecs_id, password):
#     """
#         succeeeded: {'accessToken': '422c9c...', 'account': '0000000000'}
#         failed:   {}
#     """
#     step1 = "https://www.k.kyoto-u.ac.jp/api/app/v1/auth/get_j_session_complete"
#     step2 = "https://www.k.kyoto-u.ac.jp/secure/student/shibboleth_account_list?keep=true"
#     step5 = "https://www.k.kyoto-u.ac.jp/api/app/v1/auth/get_shibboleth_session"
#     step6 = "https://www.k.kyoto-u.ac.jp/secure/student/shibboleth_account_list?keep=true"
#     # 1
#     rp1 = requests.get(step1)
#     jsession = rp1.json().get('jsession')
#     location = rp1.json().get('location')
#     # 2
#     jsession_id = jsession.replace("JSESSIONID=", "")
#     cookies2 = {"JSESSIONID":jsession_id,"cserver":"ku_europa"}
#     # 不要かも？
#     rp2 = requests.get(step2, cookies=cookies2)
#     # 3
#     cookies3 = {"JSESSIONID":jsession_id}
#     rp3 = requests.post(location, 
#                         data = f"j_username={ecs_id}&j_password={password}&_eventId_proceed=",
#                         headers={"Content-Type":"application/x-www-form-urlencoded"},
#                         cookies=cookies3)
#     # 4
#     soup = BeautifulSoup(rp3.text, "html.parser")
#     input_tags = soup.find_all("input")
#     RelayState = ""
#     SAMLResponse = ""
#     for input_tag in input_tags:
#         if input_tag.attrs.get("name") == "RelayState":
#             RelayState = input_tag.attrs.get("value")
#         elif input_tag.attrs.get("name") == "SAMLResponse":
#             SAMLResponse = input_tag.attrs.get("value")
#     # 5
#     rp5 = requests.post(step5,
#                         data = f"RelayState={urllib.parse.quote(RelayState)}&SAMLResponse={urllib.parse.quote(SAMLResponse)}&requestUrl=https%3A%2F%2Fwww.k.kyoto-u.ac.jp%2FShibboleth.sso%2FSAML2%2FPOST",
#                         headers={"Content-Type":"application/x-www-form-urlencoded"},
#                         cookies = cookies2)
#     try:
#         shibsession = rp5.json().get("cookie")
#         shibsession_sp = shibsession.split("=")
#         cookies6 = {shibsession_sp[0]:shibsession_sp[1], "cserver":"ku_europa"}
#         # 6
#         rp6 = requests.get(step6, cookies=cookies6)
#         accessToken = rp6.json().get("accessToken")
#         account = rp6.json().get("account")
#         if accessToken == None or account == None:
#             return {}
#         else:
#             return {'accessToken':accessToken, 'account':account}
#     except json.JSONDecodeError as e:
#         return {}