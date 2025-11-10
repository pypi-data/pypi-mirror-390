import json

from smartpush.base.request_base import CrowdRequestBase, RequestBase
from smartpush.base.url_enum import URL
from smartpush.export.basic.ExcelExportChecker import compare_lists, compare_dicts
from smartpush.export.basic.ReadExcel import read_excel_file_form_local_path


class Crowd(CrowdRequestBase):

    def callEditCrowdPackage(self, crowdName="", groupRules=None, groupRelation="$AND",
                             triggerStock=False):
        """
        更新群组条件id
        :param triggerStock:
        :param crowdName:
        :param groupRules:
        :param groupRelation:
        :return:
        """
        requestParam = {"id": self.crowd_id, "crowdName": crowdName, "groupRelation": groupRelation,
                        "groupRules": groupRules, "triggerStock": triggerStock}
        result = self.request(method=URL.editCrowdPackage.method, path=URL.editCrowdPackage.url, data=requestParam)
        return result['resultData']

    def callCrowdPersonListInPackage(self, page=1, pageSize=20, filter_type=None, operator='eq', filter_value=None):
        """
        获取群组联系人列表
        :param operator:操作符：eq/in/invalidPerson/subscribeStatusEnum/
        :param page:
        :param pageSize:
        :param filter_type: 过滤类型，email、sms、
        :param filter_value:具体值
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize}
        if filter_value is not None:
            requestParam["filter"] = {filter_type: {operator: filter_value}}
        result = self.request(method=URL.crowdPersonListInPackage.method, path=URL.crowdPersonListInPackage.url,
                              data=requestParam)
        resultData = result['resultData']
        return resultData

    def callCrowdPackageDetail(self, page=1, pageSize=20):
        """
        获取群组详情
        :param page:
        :param pageSize:
        :return:
        """
        requestParam = {"id": self.crowd_id, "page": page, "pageSize": pageSize, "filter": {}}
        # if filter_value is not None:
        #     requestParam["filter"] = {filter_type: {"in": filter_value}}
        result = self.request(method=URL.crowdPackageDetail.method, path=URL.crowdPackageDetail.url, data=requestParam)
        resultData = result['resultData']
        return resultData


class CrowdList(RequestBase):
    def callCrowdPackageList(self, page=1, pageSize=20):
        """
        获取群组联系人列表
        :param page:
        :param pageSize:
        :param filter_type:
        :param filter_value:
        :return:
        """
        requestParam = {"page": page, "pageSize": pageSize}
        result = self.request(method=URL.crowdPackageList.method, path=URL.crowdPackageList.url,
                              data=requestParam)
        resultData = result['resultData']
        return resultData


if __name__ == '__main__':
    host = "https://test.smartpushedm.com/bff/api-em-ec2"
    headers = {
        "cookie": "sl_lc_session_id=ARdVBTYWFkAHFAOZAAAAAAAAAL-KVkgKBEThtKK15gJ0Zs5FGBzwsoTN2dBPh0jqgjbD; osudb_lang=; a_lang=zh-hans-cn; osudb_uid=4600602538; osudb_oar=#01#SID0000137BGuxewUplqynPbKiaNcheknhOa/Gnew3PkzQg3g4wX8svtCKzKNYEqtDMqbcprxgo3dc1piMLUaV7AcPZ4EYmLp/EjQbAowjsUkUOm02fj3Fd8WW8B8vDA2T9PNFbVEKwTdvt4T5g550posh1y5a; osudb_appid=SMARTPUSH; osudb_subappid=1; ecom_http_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjA2NzA4MzUsImp0aSI6ImQyZTkxMzMyLTYwMTMtNGI3NC04NzAzLWQzZDAxMzkyNTdjNSIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0NjAwNjAyNTM4IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsInVzZXJSb2xlIjoib3duZXIiLCJwbGF0Zm9ybVR5cGUiOjcsInN1YlBsYXRmb3JtIjoxLCJwaG9uZSI6IiIsImxhbmd1YWdlIjoiemgtaGFucy1jbiIsImF1dGhUeXBlIjoiIiwiYXR0cmlidXRlcyI6eyJjb3VudHJ5Q29kZSI6IkNOIiwiY3VycmVuY3kiOiJVU0QiLCJjdXJyZW5jeVN5bWJvbCI6IlVTJCIsImRvbWFpbiI6Imx1LWx1LmVtYWlsIiwibGFuZ3VhZ2UiOiJ6aC1oYW50LXR3IiwibWVyY2hhbnRFbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsIm1lcmNoYW50TmFtZSI6Imx1bHUzODIt6K6i6ZiF5byP55S15ZWGIiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIn0sInN0b3JlSWQiOiIxNzQ1Mzc3NzA1OTM2IiwiaGFuZGxlIjoibHVsdTM4MiIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc1ODA3ODgzNTYwMiwic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.ZMtJ83tH8i-BArVnSvfS4rKCD49N8WLsnhxVJ11BddI; JSESSIONID=02CC44F5CD538B9151BF875A62716465",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjA2NzA4MzUsImp0aSI6ImQyZTkxMzMyLTYwMTMtNGI3NC04NzAzLWQzZDAxMzkyNTdjNSIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0NjAwNjAyNTM4IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsInVzZXJSb2xlIjoib3duZXIiLCJwbGF0Zm9ybVR5cGUiOjcsInN1YlBsYXRmb3JtIjoxLCJwaG9uZSI6IiIsImxhbmd1YWdlIjoiemgtaGFucy1jbiIsImF1dGhUeXBlIjoiIiwiYXR0cmlidXRlcyI6eyJjb3VudHJ5Q29kZSI6IkNOIiwiY3VycmVuY3kiOiJVU0QiLCJjdXJyZW5jeVN5bWJvbCI6IlVTJCIsImRvbWFpbiI6Imx1LWx1LmVtYWlsIiwibGFuZ3VhZ2UiOiJ6aC1oYW50LXR3IiwibWVyY2hhbnRFbWFpbCI6Imx1Lmx1QHNob3BsaW5lLmNvbSIsIm1lcmNoYW50TmFtZSI6Imx1bHUzODIt6K6i6ZiF5byP55S15ZWGIiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIn0sInN0b3JlSWQiOiIxNzQ1Mzc3NzA1OTM2IiwiaGFuZGxlIjoibHVsdTM4MiIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc1ODA3ODgzNTYwMiwic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.ZMtJ83tH8i-BArVnSvfS4rKCD49N8WLsnhxVJ11BddI"}

    crowd_id = "687a028fa34ae35465dc91a2"


    # def diff_person(_crowd_id, path):
        ## 这里是查询群组的人的差异
        # list_len = 0
        # flag = True
        # page = 1
        # crowd = Crowd(crowd_id=_crowd_id, host=host, headers=headers)
        # result_list = []
        #
        # while flag:
        #     result = crowd.callCrowdPersonListInPackage(pageSize=100, page=page)
        #     page += 1
        #     num = result['num']
        #     list_len += len(result['responseResult'])
        #     for data in result['responseResult']:
        #         result_list.append(data['id'])
        #     if list_len >= num:
        #         break
        # print(result_list)
        # print("es查询群组数量：", len(result_list))

    #     # 这里是解析本地文件，查看
    #     key = ["user_id"]
    #     data = read_excel_file_form_local_path(path, key)
    #     print(data)
    #     print(list(data.get(key)))
    #     compare_lists(list(data.get("crowd_id")))
    #
    #
    # def diff_crowd_num(sql_result_list):
    #     ## 比较哪些群组数量不一致
    #     _sql_result_list = {item["crowd_id"]: item["num"] for item in sql_result_list}
    #     crowd_list = CrowdList(host=host, headers=headers)
    #     cc = crowd_list.callCrowdPackageList(1, 100)
    #     crowd_dict = {i['id']: i['nums'] for i in cc['responseList']}
    #
    #     print("-----sql_result_list-----:\n", json.dumps(sql_result_list, ensure_ascii=False))
    #     print("****crowd_dict*****:\n", json.dumps(cc, ensure_ascii=False))
    #     print(f"人群列表数量:{len(crowd_dict)}，hive数量：{len(_sql_result_list)}")
    #     print(":::::差异:::::\n", json.dumps(compare_dicts(crowd_dict, _sql_result_list), ensure_ascii=False))
    #
    #
    # sql_result_list = [
    #             {
    #                 "crowd_id": "68778564f40cc91244b1e9fc",
    #                 "num": "1306"
    #             },
    #             {
    #                 "crowd_id": "68b54dbef66289676b17fb02",
    #                 "num": "5"
    #             },
    #             {
    #                 "crowd_id": "68942ae20241ad76344e3bab",
    #                 "num": "8"
    #             },
    #             {
    #                 "crowd_id": "6894453f0241ad76344e3bd3",
    #                 "num": "9"
    #             },
    #             {
    #                 "crowd_id": "68c838d568575727b9f017fb",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "689444a20241ad76344e3bd1",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68942bd458bb063f71fd58c9",
    #                 "num": "8"
    #             },
    #             {
    #                 "crowd_id": "68ba5c555259840710f2e44c",
    #                 "num": "5"
    #             },
    #             {
    #                 "crowd_id": "687b3670a34ae35465dc92ee",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "68942a780241ad76344e3baa",
    #                 "num": "1297"
    #             },
    #             {
    #                 "crowd_id": "689adf847430a236d5cb6f08",
    #                 "num": "23"
    #             },
    #             {
    #                 "crowd_id": "687e1753a5e5180731e21271",
    #                 "num": "20"
    #             },
    #             {
    #                 "crowd_id": "68998763498c5c49695a260b",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "68942b1b58bb063f71fd58c6",
    #                 "num": "35"
    #             },
    #             {
    #                 "crowd_id": "689444e958bb063f71fd58eb",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "6874b5338c6fe76c51447579",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "6879fc5aa34ae35465dc9199",
    #                 "num": "1280"
    #             },
    #             {
    #                 "crowd_id": "687dec0ba5e5180731e2113d",
    #                 "num": "21"
    #             },
    #             {
    #                 "crowd_id": "68a2c948f847681961408a55",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "687a028fa34ae35465dc91a2",
    #                 "num": "1290"
    #             },
    #             {
    #                 "crowd_id": "687debd0a5e5180731e2113c",
    #                 "num": "55"
    #             },
    #             {
    #                 "crowd_id": "687da2bda34ae35465dc9460",
    #                 "num": "1256"
    #             },
    #             {
    #                 "crowd_id": "687ef5febeaa88751e197aca",
    #                 "num": "48"
    #             },
    #             {
    #                 "crowd_id": "687a1913a34ae35465dc91fb",
    #                 "num": "21"
    #             },
    #             {
    #                 "crowd_id": "687afff5a34ae35465dc92d7",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "687e171ba5e5180731e2126f",
    #                 "num": "9"
    #             },
    #             {
    #                 "crowd_id": "689444b858bb063f71fd58e9",
    #                 "num": "39"
    #             },
    #             {
    #                 "crowd_id": "6894444e58bb063f71fd58e7",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "687a193aa34ae35465dc91fc",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "6894456558bb063f71fd58ee",
    #                 "num": "14"
    #             },
    #             {
    #                 "crowd_id": "689445030241ad76344e3bd2",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68942bb20241ad76344e3bac",
    #                 "num": "12"
    #             },
    #             {
    #                 "crowd_id": "689448b10241ad76344e3bdf",
    #                 "num": "39"
    #             },
    #             {
    #                 "crowd_id": "68942aa258bb063f71fd58c4",
    #                 "num": "6"
    #             },
    #             {
    #                 "crowd_id": "6894447b58bb063f71fd58e8",
    #                 "num": "1256"
    #             },
    #             {
    #                 "crowd_id": "6873eeddf1ac104346194bde",
    #                 "num": "8"
    #             },
    #             {
    #                 "crowd_id": "689d9df3cb5cfd0392532206",
    #                 "num": "24"
    #             },
    #             {
    #                 "crowd_id": "689443d70241ad76344e3bcb",
    #                 "num": "5"
    #             },
    #             {
    #                 "crowd_id": "687b0207a34ae35465dc92da",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "689a0f2fb96a557a6d78bf3c",
    #                 "num": "11"
    #             },
    #             {
    #                 "crowd_id": "6889f03c48f6a30bd07aa14e",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68c7ebc168575727b9f01445",
    #                 "num": "68"
    #             },
    #             {
    #                 "crowd_id": "687e16dfa5e5180731e2126e",
    #                 "num": "12"
    #             },
    #             {
    #                 "crowd_id": "68942b7158bb063f71fd58c7",
    #                 "num": "8"
    #             },
    #             {
    #                 "crowd_id": "687b0269a34ae35465dc92db",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68832876f0cc690fd7105324",
    #                 "num": "93"
    #             },
    #             {
    #                 "crowd_id": "687e1908a5e5180731e21272",
    #                 "num": "1314"
    #             },
    #             {
    #                 "crowd_id": "6879f8c6a34ae35465dc9185",
    #                 "num": "22"
    #             },
    #             {
    #                 "crowd_id": "687df922a5e5180731e211d0",
    #                 "num": "4"
    #             },
    #             {
    #                 "crowd_id": "689c4ba7c73a8e68c750ef9c",
    #                 "num": "8"
    #             },
    #             {
    #                 "crowd_id": "687b3c0ba34ae35465dc9303",
    #                 "num": "51"
    #             },
    #             {
    #                 "crowd_id": "689420620241ad76344e3b9e",
    #                 "num": "22"
    #             },
    #             {
    #                 "crowd_id": "687de8eaa5e5180731e21123",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68c78afb70b5fc0b7a37992c",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "689444cd58bb063f71fd58ea",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "6877c4aaf40cc91244b1ea05",
    #                 "num": "1289"
    #             },
    #             {
    #                 "crowd_id": "689c4cc2801953000707b9b9",
    #                 "num": "1315"
    #             },
    #             {
    #                 "crowd_id": "689443f758bb063f71fd58e5",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "68b68f041532400e8327b305",
    #                 "num": "12"
    #             },
    #             {
    #                 "crowd_id": "6880a6a146fc3040a4851cff",
    #                 "num": "105"
    #             },
    #             {
    #                 "crowd_id": "68c9027c68575727b9f01d1b",
    #                 "num": "9"
    #             },
    #             {
    #                 "crowd_id": "68ade82592874335048e92c4",
    #                 "num": "3"
    #             },
    #             {
    #                 "crowd_id": "68942abf58bb063f71fd58c5",
    #                 "num": "1267"
    #             },
    #             {
    #                 "crowd_id": "6894457c0241ad76344e3bd4",
    #                 "num": "4"
    #             },
    #             {
    #                 "crowd_id": "6894452e58bb063f71fd58ec",
    #                 "num": "9"
    #             },
    #             {
    #                 "crowd_id": "6894455258bb063f71fd58ed",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "68b543d5f66289676b17fa6c",
    #                 "num": "12"
    #             },
    #             {
    #                 "crowd_id": "689a2c95079db40c09aa710d",
    #                 "num": "1314"
    #             },
    #             {
    #                 "crowd_id": "689add237430a236d5cb6efc",
    #                 "num": "1306"
    #             },
    #             {
    #                 "crowd_id": "68c38fd2617bb73ea09f7da0",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "687b38dda34ae35465dc92ef",
    #                 "num": "9"
    #             },
    #             {
    #                 "crowd_id": "68942b9258bb063f71fd58c8",
    #                 "num": "5"
    #             },
    #             {
    #                 "crowd_id": "68a02fc81625ac62b727fae2",
    #                 "num": "24"
    #             },
    #             {
    #                 "crowd_id": "6879fc29a34ae35465dc9198",
    #                 "num": "25"
    #             },
    #             {
    #                 "crowd_id": "689a1e17b96a557a6d78bf4d",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "6894461e58bb063f71fd58ef",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "68ba5e0d5259840710f2e457",
    #                 "num": "1"
    #             },
    #             {
    #                 "crowd_id": "687a0dada34ae35465dc91be",
    #                 "num": "59"
    #             },
    #             {
    #                 "crowd_id": "689444620241ad76344e3bcf",
    #                 "num": "50"
    #             },
    #             {
    #                 "crowd_id": "687b649aa34ae35465dc934a",
    #                 "num": "14"
    #             },
    #             {
    #                 "crowd_id": "6894209858bb063f71fd58b1",
    #                 "num": "21"
    #             },
    #             {
    #                 "crowd_id": "687b632ca34ae35465dc933b",
    #                 "num": "57"
    #             },
    #             {
    #                 "crowd_id": "686dea326424e217d9c0c86a",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "687e05e8a5e5180731e2122b",
    #                 "num": "2"
    #             },
    #             {
    #                 "crowd_id": "689bf254801953000707b8fe",
    #                 "num": "1315"
    #             },
    #             {
    #                 "crowd_id": "689420c258bb063f71fd58b4",
    #                 "num": "13"
    #             },
    #             {
    #                 "crowd_id": "689c133a801953000707b996",
    #                 "num": "1306"
    #             },
    #             {
    #                 "crowd_id": "687dec77a5e5180731e21143",
    #                 "num": "10"
    #             },
    #             {
    #                 "crowd_id": "6881a1d97fe4b22a4d5feec6",
    #                 "num": "1"
    #             }
    #         ]
    # diff_crowd_num(sql_result_list)

    # diff_person(_crowd_id="687a028fa34ae35465dc91a2",
    #             path="/Users/lulu/Downloads/临时文件2_20250719155155.xls")
