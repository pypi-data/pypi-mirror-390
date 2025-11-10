# -*- coding: utf-8 -*-
import copy
import http.client
import json
import time
import requests
itamheaders = {
    'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NDI1NDYyMTcsImp0aSI6ImJKMk9hV0dkanU5QStMMXciLCJpYXQiOjE3NDEyNTAyMTcsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.eHghtX4NOnD1uD65bzqv7n1J3mtnPPXJoVKIWDwl4PMZPkqc3FisH4RMXxDqeOyDCgRHYhmam7VEenl8T0UIKpzI8ad8yMiZytvAkNhclLjCdmokLB7DdwnbO1qeDLxdqjL-S3da0KHHkOT8j-rWR94XJ0N7T_snoko4Ovsp13w',
    'Content-Type': 'application/json'

}



class webapiClient():
    def __init__(self, clientin):
        """
       初始化 Client 实例,tenant_access_token 会在 Client 初始化时自动获取
        """
        headers = {
            'cookie': clientin['cookie'],
            'x-kunlun-token': clientin['x-kunlun-token'],
            'Content-Type': "application/json"
        }
        self.headers = headers
        self.itamheaders = headers
        self.conn = http.client.HTTPSConnection("apaas.feishu.cn")
        #spring_be31ab47e7__c 新
        self.aily_app_id = clientin['aily_app_id']
        if self.aily_app_id == "spring_be31ab47e7__c":
            self.conn = http.client.HTTPSConnection("apaas-spring-3bf03.aedev.feishuapp.cn")
            headers['x-kunlun-switchctxtoprod'] = True

    def intentdetaillist_cookiecheck(self):
        #检查接口的授权信息是否有效
        # 输入参数类型和范围检查
        startAt = int(time.time()) - 30 * 24 * 60 * 60
        endAt = int(time.time())
        payload = json.dumps({
            "startAt": startAt,
            "endAt": endAt,
            "matchIntentID": "",
            "matchStatus": [],
            "pageSize": 50
        })
        try:
            self.conn.request("POST",
                              f"/ai/api/v1/conversational_runtime/namespaces/{self.aily_app_id}/stats/intent_detail_list",
                              payload, self.headers)
            res = self.conn.getresponse()
            # 检查响应状态码
            if res.status != 200:
                raise http.client.HTTPException(f"请求失败，状态码: {res.status}, 原因: {res.reason}")
            data = res.read()
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)
            if data_dict.get('error_msg'):
                raise ValueError(f"接口intent_detail_list，报错{data_str},可能是cookie/x-kunlun-token无效请检查")
        except http.client.HTTPException as http_err:
            print(f"HTTP 请求错误: {http_err}")

    def get_intent_detail_list(self, startAt, pageSize):
        """
        outdata:
            对话ID 技能分发 用户输入
           res_ = {
          'intentID': 7485259579248705537,
          'userInput': "我要申请一个鼠标",
          'skillLabels': ["GUI 设备/配件申请"],
           'apply_day':"",
          'apply_num':"",
          'asset_name':"",
          'device_type':""
           }
        """
        # 输入参数类型和范围检查
        if not isinstance(startAt, int) or startAt < 0:
            raise ValueError("startAt 必须是一个非负整数")
        if not isinstance(pageSize, int) or pageSize < 0:
            raise ValueError("pageSize 必须是一个非负整数")

        endAt = int(time.time()) or 1748361600
        payload = json.dumps({
            "startAt": startAt,
            "endAt": endAt,
            "matchIntentID": "",
            "matchStatus": [],
            "pageSize": pageSize+500
        })
        try:
            self.conn.request("POST",f"/ai/api/v1/conversational_runtime/namespaces/{self.aily_app_id}/stats/intent_detail_list",payload, self.headers)
            res = self.conn.getresponse()
            # 检查响应状态码
            if res.status != 200:
                raise http.client.HTTPException(f"请求失败，状态码: {res.status}, 原因: {res.reason}")

            data = res.read()
            try:
                data = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                raise ValueError("无法将响应数据解析为 JSON 格式")

            # 检查响应数据结构
            if 'data' not in data or 'intentDetailList' not in data['data']:
                raise ValueError("响应数据缺少必要的字段 'data' 或 'intentDetailList'")

            res_list = []
            data_ = data['data']['intentDetailList']
            for i in data_:
                if i['channelType'] in ["LARK_OPEN_API"]:
                    res_list.append({
                        '对话日志/intentID': i['intentID'],
                        '用户输入/userInput': i['userInput'],
                        '数据是否有效/isdatavalid': "是",
                        '语言/language': "zh",
                        '是否 IT 问题/isITproblem': "是",
                        '业务场景/businessscenario': "NULL",
                        '分发技能/skill': i['skillLabels'],
                        '型号关键字词/asset_name': "NULL",
                        '型号类型/device_type': "NULL",
                        '匹配型号/AssetNamelist': "NULL",
                    })
            return res_list
        except http.client.HTTPException as http_err:
            print(f"HTTP 请求错误: {http_err}")
            return res_list
        except ValueError as value_err:
            print(f"值错误: {value_err}")
            return res_list
        except Exception as general_err:
            print(f"发生未知错误: {general_err}")
            return res_list

    def get_urlintentID(self, intentID):
        """
        输入：intentID
        输出：url
        """
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                payload = ''
                urlintentID = f'https://apaas.feishu.cn/ai/api/v1/conversational_runtime/namespaces/{self.aily_app_id}/intent/{intentID}?pageSize=20&statusFilter=%5B%5D&fieldFilter=_node_id&fieldFilter=status&fieldFilter=usages&fieldFilter=_node_name&fieldFilter=_node_type&fieldFilter=title_for_maker&fieldFilter=associate_id'
                response = requests.request("GET", urlintentID, headers=self.headers, data=payload)
                # 检查响应状态码
                response.raise_for_status()
                response = response.json()
                # 检查特定错误状态码
                if 'status_code' in response and response['status_code'] == "k_gw_ec_100033":
                    retries += 1
                    if retries < max_retries:
                        print(f"接口不存在，正在进行第 {retries} 次重试...")
                        continue
                    else:
                        print(f"接口不存在，已达到最大重试次数 {max_retries} 次")
                        return None
                return response
            except (requests.RequestException, json.JSONDecodeError) as e:
                retries += 1
                if retries < max_retries:
                    print(f"请求失败，原因: {e}，正在进行第 {retries} 次重试...")
                else:
                    print(f"请求失败，已达到最大重试次数 {max_retries} 次，原因: {e}")
        return None

    def get_urlnodeid(self, intentID, nodeid):
        """
        输入：intentID
        输出：url
        """
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                payload = ''
                urlnodeid = f'https://apaas.feishu.cn/ai/api/v1/conversational_runtime/namespaces/{self.aily_app_id}/association/{intentID}/node/{nodeid}?intentID={intentID}'
                response = requests.request("GET", urlnodeid, headers=self.headers, data=payload)
                # 检查响应状态码
                response.raise_for_status()
                response = response.json()
                # 检查特定错误状态码
                if 'status_code' in response and response['status_code'] == "k_gw_ec_100033":
                    retries += 1
                    if retries < max_retries:
                        print(f"接口不存在，正在进行第 {retries} 次重试...")
                        continue
                    else:
                        print(f"接口不存在，已达到最大重试次数 {max_retries} 次")
                        return None
                return response
            except (requests.RequestException, json.JSONDecodeError) as e:
                retries += 1
                if retries < max_retries:
                    print(f"请求失败，原因: {e}，正在进行第 {retries} 次重试...")
                else:
                    print(f"请求失败，已达到最大重试次数 {max_retries} 次，原因: {e}")
        return None



    def get_intent_detail_llm(self, res_list):
        """
        提取关键词：
        槽位提取：'apply_day': "",'apply_num': "",'asset_name': "",'device_type': ""
        表头字段：
        '对话日志/intentID': 7485264011232886786,
        '用户输入/userInput': "我要申请一个鼠标",
        '数据是否有效/isdatavalid': "是",
        '语言/language': "zh",
        '是否 IT 问题/isITproblem': "是",
        '业务场景/businessscenario': "NULL",
        '分发技能/skill': "NULL",
        '型号关键字词/asset_name': "NULL", #显示器
        '型号类型/device_type': "NULL",    # 设备 配件 软件
        '匹配型号/AssetNamelist': "NULL",
        """
        ii0 = []
        ii = {
            '对话日志/intentID': "7485264011232886786",
            '用户输入/userInput': "我要申请一个鼠标",
            '数据是否有效/isdatavalid': "是",
            '语言/language': "zh",
            '是否 IT 问题/isITproblem': "是",
            '业务场景/businessscenario': "NULL",
            '分发技能/skill': "NULL",
            'llm关键词': "NULL"
        }
        try:
            # 检查 res_list 是否为空
            if not res_list:
                print("输入的 res_list 为空")
                return []
            for i in res_list:
                print("urlintentID_1:" + str(i))
                ii['分发技能/skill'] = i['分发技能/skill']
                ii['对话日志/intentID'] = i['对话日志/intentID']
                ii['用户输入/userInput'] = i['用户输入/userInput']
                intentID = str(ii['对话日志/intentID'])
                res_ = self.get_urlintentID(intentID)
                if res_ is None:
                    continue
                response = res_
                for j in response['data']['steps']:
                    if j['titleForMaker'] in ["槽位抽取", "LLM 2", "LLM"]:
                        nodeid = j['nodeID']
                        data_nodeid = self.get_urlnodeid(intentID, nodeid)
                        if data_nodeid is None or 'data' not in data_nodeid or 'step' not in data_nodeid['data'] or 'output' not in data_nodeid['data']['step'] or data_nodeid['data']['step']['output'] == "":
                            ii['llm关键词'] = "NULL"
                        else:
                            ii['llm关键词'] = json.loads(data_nodeid['data']['step']['output'])['response']
                ii0.append(copy.deepcopy(ii))
            return ii0
        except requests.RequestException as req_err:
            print(f"请求错误: {req_err}")
            return ii0
        except Exception as general_err:
            print(f"发生未知错误: {general_err}")
            return ii0

    def get_bestmatchitemforreturn(self, keyword):
        """
        mock数据，获取最佳匹配的sku/spu
        mock数据：公用配件列表、设备列表、软件列表
        todo：mock数据表格为飞书文档或者其他？
        """
        _urlGetBestMatchItemForReturn = "https://asset-mig-pre.bytedance.net/aily/api/itservice/ai/GetBestMatchItemForReturn"

        payload = json.dumps({
            "SearchKey": keyword,
            "AiUseType": 1,
            "ListReturnableAccessoryRequest": {
                "IsAll": True,
                "Page": {
                    "PageNum": 1,
                    "PageSize": 30
                },
                "OwnerUserID": "",
                "AccessoryApplyTypeList": []
            },
            "GetAssetListRequest": {
                "Status": 6,
                "Search": "",
                "IsAll": True,
                "SubStatusList": [
                    12,
                    18,
                    19
                ],
                "Page": {
                    "PageNum": 1,
                    "PageSize": 30
                },
                "OrganizationalUnitID": 1
            }
        })
        response = requests.request("GET", _urlGetBestMatchItemForReturn, headers=self.headers, data=payload)
        response = json.loads(response.text)

    def get_segsearchcandidates(self, res_list):
        # 获取分数值
        ### 读取设备&配件的信息并拼接到text里面
        ### 遍历res_list中的device_name
        ###判断是否在asset.json里面
        ###调用算法接口获取设备&配件的分数值
        pass


""""""
if __name__ == '__main__':
    clientin = {
        'cookie': 'X-Kunlun-SessionId=L%3A028d306c70a340a69fe9.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2YWwiOnsidGVuYW50X2lkIjozOTAsInVzZXJfaWQiOjE3MjIxNjYwNzMxOTk2NDUsInRlbmFudF9kb21haW5fbmFtZSI6ImFwYWFzIiwic2Vzc2lvbl92ZXJzaW9uIjoidjIwMjAtMDUtMTkiLCJ3c190b2tlbiI6Ilc6ZTU3MmJlYzNmOGIzNDE0ZDk0NDYiLCJsb2dpbl90b2tlbiI6IjE3MDE3ZmFlMWJlNjVlMzc2V1VhMzA0ZjY0N2MyZmFjY2QwZ256YmNmNGVjNzAzZDgwOWYxNHJPWTY0MzY1ZjEyNWI0YmZlZDhreUciLCJzb3VyY2VfY2hhbm5lbCI6ImZlaXNodSIsInRlbmFudF9rZXkiOiI3MzY1ODhjOTI2MGYxNzVkIiwiZXh0ZXJuYWxfZG9tYWluX25hbWUiOiJieXRlZGFuY2UiLCJvcmlnaW5hbF90ZW5hbnRfaWQiOjAsIm9yaWdpbmFsX3VzZXJfaWQiOjAsImlkcF9jaGFubmVsIjoiIn0sImV4cCI6MTc2Mzg4MzY0NX0.VWyqct9gPOSXiX_72IqCRAknHsJK1aaZLIZ4gICbH5U; gd_random=eyJwZXJjZW50IjowLjY4NTgwODU2NDE4ODc2MjcsIm1hdGNoIjpmYWxzZX0=.iBiK3be8U+wA12/YghnWQbmDRz/vrBS/OQJpAvYx4XY=; trust_browser_id=3686a9b0-ce48-4e07-a0ce-e6928dc2bd6a; X-Kunlun-LoginTag=feishu; passport_trace_id=7389204030662426627; passport_web_did=7424353640858812419; QXV0aHpDb250ZXh0=9bcf0657fb6e47d497625011ffcd73e7; lark_sso_session=XN0YXJ0-488md350-54b2-433e-9eeb-b7a5c700ea26-WVuZA; X-Larkgw-Web-DID=3439857258174095984; X-Larkgw-Use-Lark-Session-119=1; __tea__ug__uid=7441424216023565850; is_anonymous_session=; fid=24c45ffc-f3d7-44f2-87ed-421f54ee78fb; lang=zh; i18n_locale=zh; locale=zh-CN; _gcl_au=1.1.2073766041.1742190427; _uetvid=44545540063311f08ed91353a6123699; _ga_7PY069DX7K=GS1.1.1742549605.1.0.1742549605.60.0.0; s_v_web_id=verify_m8cn771e_wyNgDZJ9_u4vt_4Tcr_8GHG_aoFTRqp3UEgK; _csrf_token=8d1282b097e1c2e7aea50829b47ffb77a72db55f-1745993230; help_center_session=7b5fca25-c6c5-4106-9d93-8709981a6957; _uuid_hera_ab_path_1=7502360423243071516; Hm_lvt_a79616d9322d81f12a92402ac6ae32ea=1746779408; apaas_web_did=1832530807807051; _tea_utm_cache_1229=undefined; lgw_csrf_token=c540cf747b5b41c2f749a2e1c0bd0900c3eb71b2-1747901330; _ga=GA1.2.113646166.1700115833; _gid=GA1.2.1661485038.1748331634; landing_url=https://accounts.feishu.cn/accounts/page/login?app_id=107&no_trap=1&redirect_uri=https%3A%2F%2Fapaas.feishu.cn%2Fai%2F{self.appid}%2Fmanagement%2Fchat-log; session=XN0YXJ0-583sf83f-7ceb-44bc-8578-0692b8383b7c-WVuZA; session_list=XN0YXJ0-583sf83f-7ceb-44bc-8578-0692b8383b7c-WVuZA; _ga_VPYRHN104D=GS2.1.s1748331633$o2$g1$t1748331645$j48$l0$h0; kunlun-session-v2=L%3A028d306c70a340a69fe9.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2YWwiOnsidGVuYW50X2lkIjozOTAsInVzZXJfaWQiOjE3MjIxNjYwNzMxOTk2NDUsInRlbmFudF9kb21haW5fbmFtZSI6ImFwYWFzIiwic2Vzc2lvbl92ZXJzaW9uIjoidjIwMjAtMDUtMTkiLCJ3c190b2tlbiI6Ilc6ZTU3MmJlYzNmOGIzNDE0ZDk0NDYiLCJsb2dpbl90b2tlbiI6IjE3MDE3ZmFlMWJlNjVlMzc2V1VhMzA0ZjY0N2MyZmFjY2QwZ256YmNmNGVjNzAzZDgwOWYxNHJPWTY0MzY1ZjEyNWI0YmZlZDhreUciLCJzb3VyY2VfY2hhbm5lbCI6ImZlaXNodSIsInRlbmFudF9rZXkiOiI3MzY1ODhjOTI2MGYxNzVkIiwiZXh0ZXJuYWxfZG9tYWluX25hbWUiOiJieXRlZGFuY2UiLCJvcmlnaW5hbF90ZW5hbnRfaWQiOjAsIm9yaWdpbmFsX3VzZXJfaWQiOjAsImlkcF9jaGFubmVsIjoiIn0sImV4cCI6MTc2Mzg4MzY0NX0.VWyqct9gPOSXiX_72IqCRAknHsJK1aaZLIZ4gICbH5U; kunlun-session-token=e337d885c13162ff663d9a991e6eb54f7dd3e04e539c8b817a923e225a87d3aa; msToken=su30ijthwqpaGKP8qOkL3viO1aXYouV3yjJ_EXTKoIlvgSJva8VvCSVRhhd1kKUHF6qdrLnsH6MF28bg8N3V1WVMmSA1ccqF8tPmt6YL0jVYhI6SePZBvIS6MJE2xkWY7vSYBCMoNax8pj4oITBwrtP_rG6yt25SlSFDdzu9WwYL; passport_app_access_token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDg0MDA5NTYsInVuaXQiOiJldV9uYyIsInJhdyI6eyJtX2FjY2Vzc19pbmZvIjp7IjEwNyI6eyJpYXQiOjE3NDgzNTc3NTYsImFjY2VzcyI6dHJ1ZX19LCJzdW0iOiI3NmY5MmYyNDQ4MDczNjc1MTA3NmI5ZTgyYzYyZWJmN2M3NzE0ZWVlOTM3YTg1NDUzZjhmNzc4NjEzYzY2NTBjIn19.qCGZwBOJ0tpGfLjtnncUTmLEai6u4D5me5ga-N8Tter0Ey5L6do2FPxoOacqLj1Wj2hxyHSTfad60hSsMTkPaQ; sl_session=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDg0MDM1NTQsInVuaXQiOiJldV9uYyIsInJhdyI6eyJtZXRhIjoiQVdIazBuRzhRUUFDQUFBQUFBQUFBQUZuQ0pwTTZrU0FBMmNJbWt6cVJJQURaeklSUnZpQUFBRUNLZ0VBUVVGQlFVRkJRVUZCUVVKdlRsZDRPVTVvU2tGQlp6MDkiLCJzdW0iOiI3NmY5MmYyNDQ4MDczNjc1MTA3NmI5ZTgyYzYyZWJmN2M3NzE0ZWVlOTM3YTg1NDUzZjhmNzc4NjEzYzY2NTBjIiwibG9jIjoiemhfY24iLCJhcGMiOiJSZWxlYXNlIiwiaWF0IjoxNzQ4MzYwMzU0LCJzYWMiOnsiVXNlclN0YWZmU3RhdHVzIjoiMSIsIlVzZXJUeXBlIjoiNDIifSwibG9kIjpudWxsLCJjbmYiOnsiamt0IjoiRWtuRFMyTmdZVDR4Y2xZRDM4UU9KUHNkUFptLVluRHRaR3ZmX1hfSTJxTSJ9LCJucyI6ImxhcmsiLCJuc191aWQiOiI3MDUzOTk0MzAyMzAwNTUzMjE4IiwibnNfdGlkIjoiMSIsIm90IjozLCJjdCI6MTc0ODMzMTY0NSwicnQiOjE3NDgzMzE2NDV9fQ.BP9Q4Wxdq_TWB898FxFr4TlpqUN8-N1QC6fFWO57C8wiNeAcFNUfed8mGdd7kvBgbC5PjwnNJjoL0iXySUpuXQ; swp_csrf_token=dd289ebe-0ce4-42d2-aece-263b6abf2d45; t_beda37=e1445dd5c8a191cc38f34d9809eb3c5179904df5285bb079d87b96baad8ee3e5',
        "x-kunlun-token": "17017fae1be65e376WUa304f647c2faccd0gnzbcf4ec703d809f14rOY64365f125b4bfed8kyG"

    }
    startAt = 1748410380
    num = 1230
    res_list = webapiClient(clientin).get_intent_detail_list(1748410380,10)
    a = webapiClient(clientin).get_intent_detail_llm(res_list)




