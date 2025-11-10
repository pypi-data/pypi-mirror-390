# -*- coding: utf-8 -*-


import copy
import csv
import time

import requests
import json
from typing import List, Dict


def get_SegSearchCandidates(Query: str, Candidates: List[Dict]) -> str or None:
    """
    获取分段搜索候选结果。

    :param Query: 搜索查询字符串
    :param Candidates: 候选结果列表，每个元素是一个字典，包含 "Score", "Text", "Attrs" 等键
    :return: 按分数排序后的前 5 个候选结果的 JSON 字符串，如果请求失败则返回 None
    """
    api_url = "https://genie.bytedance.com/pre/entsol/genie/skills/it-service/common/SegSearchCandidates"
    payload = {
        "Query": Query,
        "TopN": 0,
        "Candidates": Candidates
    }

    headers = {
        'Authorization': 'Basic bWFzLTZrMGJxLWgwMmhxbDM4MjQtMzJrcXQ6YTljNDIwMWJlOTc4OTg4MDRhZmZiNTQyMzA2ZTMxMzU=',
        'Content-Type': 'application/json'
    }

    try:
        # 发起 POST 请求
        response = requests.post(api_url, headers=headers, json=payload)
        # 检查响应状态码
        response.raise_for_status()
        result = response.json()
        if result and 'Candidates' in result:
            top_5_scores = sorted(result['Candidates'], key=lambda x: x.get('Score', 0), reverse=True)[:5]
            return json.dumps(top_5_scores, ensure_ascii=False)
    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
    except (KeyError, ValueError) as e:
        print(f"处理响应数据时发生错误: {e}")

    return None


def get_query_vector(para, clientinfo):
    url = "https://open-itam-mig-pre.bytedance.net/v1/query_vector"
    payload = json.dumps(para)
    headers = {
        'Authorization': clientinfo.get(
            "authorization") or "Basic cm40cmFpdTRwenY1cGlsYTo2bWhvOXV3ZXFrOHZpbDllcXRxMHZ1YmVnc2xjeXBucg==",
        'x-use-ppe': '1',
        'x-tt-env': clientinfo.get("x_tt_env") or "ppe_openapi_vector_v2",
        'Content-Type': 'application/json'
    }
    time.sleep(2.1)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def get_by_AssetModelBizTypes(param, res):
    """
    根据AssetModelBizTypes对分数进行预处理
    """
    num = len(param.get("AssetModelFieldsWithOr"))
    res0 = res["body"]["Results"]
    for i in res0:
        i['Score'] = i['Score'] / num
    res["body"]["Results"] = res0
    return res


def software_asset_sku_structure(QueryValue):
    """
    { "asset_name": "figma", "version": null, "usage": "画画", "other_software": null, "link": "https://www.figma.com" }
    """
    AssetModelFieldsWithAnd = []
    if QueryValue.get('asset_name'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_neme", "FieldType": "knn", "QueryValue": QueryValue.get("asset_name")})
    if QueryValue.get('version'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_version", "FieldType": "knn", "QueryValue": QueryValue.get("version")})
    if QueryValue.get('usage'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_description", "FieldType": "knn", "QueryValue": QueryValue.get("usage")})

    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.6,
        "AssetModelFieldsWithAnd": AssetModelFieldsWithAnd,
        "AssetModelBizTypes": "software_asset_sku"
    }
    return parm


def asset_sku_structure(QueryValue):
    """
    //除4
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword_parts = [QueryValue.get(key, "") for key in ["asset_name", "brand", "model", "specification"] if
                     QueryValue.get(key)]
    keyword = ''.join(keyword_parts)
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_specification",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_model_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": ["asset_sku"]
    }
    return parm


def asset_spu_structure(QueryValue):
    """
    //
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": [
            "asset_spu"
        ]
    }
    return parm


def accessory_sku_structure(QueryValue):
    """
    //除2
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": ["accessory_sku"]
    }
    return parm


def asset_sku_structure0(QueryValue):
    """
    //除4
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword_parts = [QueryValue.get(key, "") for key in ["asset_name", "brand", "model", "specification"] if
                     QueryValue.get(key)]
    keyword = ''.join(keyword_parts)
    keyword = QueryValue['asset_name']
    spuid = ["7188375763950259259", "7188376358115380256", "7188376497748560929", "7189141923718220857",
             "7189147675056704572", "7195007119644134460", "7195007119644150844", "7195086198350842891",
             "7195086198350859275", "7195090795660069921", "7195090795660086305", "7195090795660102689",
             "7195090795660119073", "7195090795660135457", "7195090795660151841", "7195090795660168225",
             "7195090795660184609", "7195090795660200993", "7195090795660217377", "7195090795660233761",
             "7195090795660250145", "7195090795660266529", "7195090795660282913", "7195090795660299297",
             "7195090795660315681", "7195090795660332065", "7195090795660348449", "7195090795660364833",
             "7195090795660381217", "7195090795660397601", "7195090795660413985", "7195090795660430369",
             "7195090795660446753", "7195090795660463137", "7195090795660479521", "7195090795660495905",
             "7195090795660512289", "7195090795660528673", "7195090795660545057", "7195090795660561441",
             "7195090795660577825", "7195090795660594209", "7195090795660610593", "7195090795660626977",
             "7195090795660643361", "7195090795660659745", "7195090795660676129", "7195090795660692513",
             "7195090795660708897", "7195090795660725281", "7195090795660741665", "7195090795660758049",
             "7195090795660774433", "7195090795660790817", "7195090795660807201", "7195090795660823585",
             "7195090795660839969", "7195090795660856353", "7195090795660872737", "7195090795660889121",
             "7195090795660905505", "7195090795660921889", "7195090795660938273", "7195090795660954657",
             "7195090795660971041", "7195090795660987425", "7195090795661003809", "7195090795661020193",
             "7195090795661036577", "7195090795661052961", "7195090795661069345", "7195090795661085729",
             "7195090795661102113", "7195090795661118497", "7195090795661134881", "7195090795661151265",
             "7195090795661167649", "7195090795661184033", "7195090795661200417", "7195090795661216801",
             "7195090795661233185", "7195090795661249569", "7195090795661265953", "7195090795661282337",
             "7195090795661298721", "7195090795661315105", "7195090795661331489", "7195090795661347873",
             "7195090795661364257", "7195090795661380641", "7195090795661397025", "7195090795661413409",
             "7195090795661429793", "7195090795661446177", "7195090795661462561", "7195090795661478945",
             "7195090795661495329", "7195090795661511713", "7195090795661528097", "7195090795661544481",
             "7195090795661560865", "7195090795661577249", "7195090795661593633", "7195090795661610017",
             "7195090795661626401", "7195090795661642785", "7195090795661659169", "7195090795661675553",
             "7195092625618111499", "7195092625618127883", "7195092625618144267", "7195092625618160651",
             "7195092625618177035", "7195092625618193419", "7195092625618209803", "7195092625618226187",
             "7195092625618242571", "7195092625618258955", "7195092625618275339", "7195092625618291723",
             "7195092625618308107", "7195092625618324491", "7195092625618340875", "7195092625618357259",
             "7195092625618373643", "7195092625618390027", "7195092625618406411", "7195092625618422795",
             "7195092625618439179", "7195092625618455563", "7195092625618471947", "7195092625618488331",
             "7195092625618504715", "7195092625618521099", "7195092625618537483", "7195092625618553867",
             "7195092625618570251", "7195092625618586635", "7195092625618603019", "7195092625618619403",
             "7195092625618635787", "7195092625618652171", "7195092625618668555", "7195092625618684939",
             "7195092625618701323", "7195092625618717707", "7195092625618734091", "7195092625618750475",
             "7195092625618766859", "7195092625618783243", "7195092625618799627", "7195092625618816011",
             "7195092625618832395", "7195092625618848779", "7195092625618865163", "7195092625618881547",
             "7195092625618897931", "7195092625618914315", "7195092625618930699", "7195092625618947083",
             "7195092625618963467", "7195092625618979851", "7195092625618996235", "7195092625619012619",
             "7195092625619029003", "7195092625619045387", "7195092625619061771", "7195092625619078155",
             "7195092625619094539", "7195092625619110923", "7195092625619127307", "7195092625619143691",
             "7195092625619160075", "7195092625619176459", "7195092625619192843", "7195092625619209227",
             "7195092625619225611", "7195092625619241995", "7195092625619258379", "7195092625619274763",
             "7195092625619291147", "7195092625619307531", "7195092625619323915", "7195092625619340299",
             "7195092625619356683", "7195092625619373067", "7195092625619389451", "7195092625619405835",
             "7195092625619422219", "7195092625619438603", "7195092625619454987", "7195092625619471371",
             "7195092625619487755", "7195092625619504139", "7195092625619520523", "7195092625619536907",
             "7195092625619553291", "7195092625619569675", "7195092625619586059", "7195092625619602443",
             "7195092625619618827", "7195092625619635211", "7195092625619651595", "7195092625619667979",
             "7195092625619684363", "7195092625619700747", "7195092625619717131", "7195092625619733515",
             "7195096094198467588", "7195096094198483972", "7195096094198500356", "7195096094198516740",
             "7195096094198533124", "7195096094198549508", "7195096094198565892", "7195096094198582276",
             "7195096094198598660", "7195096094198615044", "7195096094198631428", "7195096094198647812",
             "7195096094198664196", "7195096094198680580", "7195096094198696964", "7195096094198713348",
             "7195096094198729732", "7195096094198746116", "7195096094198762500", "7195096094198778884",
             "7195096094198795268", "7195096094198811652", "7195096094198828036", "7195096094198844420",
             "7195096094198860804", "7195096094198877188", "7195096094198893572", "7195096094198909956",
             "7195096094198926340", "7195096094198942724", "7195096094198959108", "7195096094198975492",
             "7195096094198991876", "7195096094199008260", "7195096094199024644", "7195096094199041028",
             "7195096094199057412", "7195096094199073796", "7195096094199090180", "7195096094199106564"]
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_specification",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_model_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "SPUIDs": spuid,
        "AssetModelBizTypes": ["asset_sku"]
    }
    return parm


def asset_spu_structure0(QueryValue):
    """
    //
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    spuid = ["7188375763950250000", "7188376358115380000", "7188376497748560000", "7189141923718220000",
             "7189147675056700000", "7195007119644130000", "7195007119644150000", "7195086198350840000",
             "7195086198350850000", "7195090795660060000", "7195090795660080000", "7195090795660100000",
             "7195090795660110000", "7195090795660130000", "7195090795660150000", "7195090795660160000",
             "7195090795660180000", "7195090795660200000", "7195090795660210000", "7195090795660230000",
             "7195090795660250000", "7195090795660260000", "7195090795660280000", "7195090795660290000",
             "7195090795660310000", "7195090795660330000", "7195090795660340000", "7195090795660360000",
             "7195090795660380000", "7195090795660390000", "7195090795660410000", "7195090795660430000",
             "7195090795660440000", "7195090795660460000", "7195090795660470000", "7195090795660490000",
             "7195090795660510000", "7195090795660520000", "7195090795660540000", "7195090795660560000",
             "7195090795660570000", "7195090795660590000", "7195090795660610000", "7195090795660620000",
             "7195090795660640000", "7195090795660650000", "7195090795660670000", "7195090795660690000",
             "7195090795660700000", "7195090795660720000", "7195090795660740000", "7195090795660750000",
             "7195090795660770000", "7195090795660790000", "7195090795660800000", "7195090795660820000",
             "7195090795660830000", "7195090795660850000", "7195090795660870000", "7195090795660880000",
             "7195090795660900000", "7195090795660920000", "7195090795660930000", "7195090795660950000",
             "7195090795660970000", "7195090795660980000", "7195090795661000000", "7195090795661020000",
             "7195090795661030000", "7195090795661050000", "7195090795661060000", "7195090795661080000",
             "7195090795661100000", "7195090795661110000", "7195090795661130000", "7195090795661150000",
             "7195090795661160000", "7195090795661180000", "7195090795661200000", "7195090795661210000",
             "7195090795661230000", "7195090795661240000", "7195090795661260000", "7195090795661280000",
             "7195090795661290000", "7195090795661310000", "7195090795661330000", "7195090795661340000",
             "7195090795661360000", "7195090795661380000", "7195090795661390000", "7195090795661410000",
             "7195090795661420000", "7195090795661440000", "7195090795661460000", "7195090795661470000",
             "7195090795661490000", "7195090795661510000", "7195090795661520000", "7195090795661540000",
             "7195090795661560000", "7195090795661570000", "7195090795661590000", "7195090795661610000",
             "7195090795661620000", "7195090795661640000", "7195090795661650000", "7195090795661670000",
             "7195092625618110000", "7195092625618120000", "7195092625618140000", "7195092625618160000",
             "7195092625618170000", "7195092625618190000", "7195092625618200000", "7195092625618220000",
             "7195092625618240000", "7195092625618250000", "7195092625618270000", "7195092625618290000",
             "7195092625618300000", "7195092625618320000", "7195092625618340000", "7195092625618350000",
             "7195092625618370000", "7195092625618390000", "7195092625618400000", "7195092625618420000",
             "7195092625618430000", "7195092625618450000", "7195092625618470000", "7195092625618480000",
             "7195092625618500000", "7195092625618520000", "7195092625618530000", "7195092625618550000",
             "7195092625618570000", "7195092625618580000", "7195092625618600000", "7195092625618610000",
             "7195092625618630000", "7195092625618650000", "7195092625618660000", "7195092625618680000",
             "7195092625618700000", "7195092625618710000", "7195092625618730000", "7195092625618750000",
             "7195092625618760000", "7195092625618780000", "7195092625618790000", "7195092625618810000",
             "7195092625618830000", "7195092625618840000", "7195092625618860000", "7195092625618880000",
             "7195092625618890000", "7195092625618910000", "7195092625618930000", "7195092625618940000",
             "7195092625618960000", "7195092625618970000", "7195092625618990000", "7195092625619010000",
             "7195092625619020000", "7195092625619040000", "7195092625619060000", "7195092625619070000",
             "7195092625619090000", "7195092625619110000", "7195092625619120000", "7195092625619140000",
             "7195092625619160000", "7195092625619170000", "7195092625619190000", "7195092625619200000",
             "7195092625619220000", "7195092625619240000", "7195092625619250000", "7195092625619270000",
             "7195092625619290000", "7195092625619300000", "7195092625619320000", "7195092625619340000",
             "7195092625619350000", "7195092625619370000", "7195092625619380000", "7195092625619400000",
             "7195092625619420000", "7195092625619430000", "7195092625619450000", "7195092625619470000",
             "7195092625619480000", "7195092625619500000", "7195092625619520000", "7195092625619530000",
             "7195092625619550000", "7195092625619560000", "7195092625619580000", "7195092625619600000",
             "7195092625619610000", "7195092625619630000", "7195092625619650000", "7195092625619660000",
             "7195092625619680000", "7195092625619700000", "7195092625619710000", "7195092625619730000",
             "7195096094198460000", "7195096094198480000", "7195096094198500000", "7195096094198510000",
             "7195096094198530000", "7195096094198540000", "7195096094198560000", "7195096094198580000",
             "7195096094198590000", "7195096094198610000", "7195096094198630000", "7195096094198640000",
             "7195096094198660000", "7195096094198680000", "7195096094198690000", "7195096094198710000",
             "7195096094198720000", "7195096094198740000", "7195096094198760000", "7195096094198770000",
             "7195096094198790000", "7195096094198810000", "7195096094198820000", "7195096094198840000",
             "7195096094198860000", "7195096094198870000", "7195096094198890000", "7195096094198900000",
             "7195096094198920000", "7195096094198940000", "7195096094198950000", "7195096094198970000",
             "7195096094198990000", "7195096094199000000", "7195096094199020000", "7195096094199040000",
             "7195096094199050000", "7195096094199070000", "7195096094199090000", "7195096094199100000"]

    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "SPUIDs": spuid,
        "AssetModelBizTypes": [
            "asset_spu"
        ]
    }
    return parm


def accessory_sku_structure0(QueryValue):
    """
    //除2
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    aid = ["7255990503152471077", "7256617984164285452", "7256686318809091129", "7256686749950004281",
           "7256687225969986618", "7256690778088442899", "7262681101586811916", "7263392934995921977",
           "7268230229804747813", "7268232128557550653", "7268234687477910586", "7268241171808357415",
           "7268255937588087864", "7268270717870197771", "7269732837775182887", "7269763472186002495",
           "7270845670796332092", "7272702161690856502", "7272752025073929228", "7273438590867098636",
           "7273440306249845814", "7280477482813344825", "7280479475325815868", "7280483298299366456",
           "7280498894235667511", "7280764067903065124", "7290837439865310264", "7290842766874889276",
           "7291270703461551115", "7291277340449049663", "7291277661333244982", "7291354258590501900",
           "7291354258590649356", "7291358098207444009", "7296056359766166567", "7296382679158967332",
           "7296382761811069988", "7296382987112680467", "7296388329770503222", "7296388836878879782",
           "7296390800186264587", "7296391160079567911", "7299038962449910823", "7299051655970245695",
           "7299061913801985035", "7299080091194625065", "7304504856743185462", "7304574626516126730",
           "7304864148406897701", "7305960363957799948", "7316741301058866239", "7316852547615149110",
           "7340991996498660389", "7340992199092259890", "7379095110077697087", "7399862706805558281",
           "7399862706805574665", "7399862706805591049", "7399862706805607433", "7399862706805623817",
           "7399862706805640201", "7399862706805656585", "7399862706805672969", "7399862706805689353",
           "7399862706805705737", "7399862706805722121", "7399862706805738505", "7399862706805754889",
           "7399862706806000649", "7399862706806017033", "7399862706806033417", "7399862706806049801",
           "7399906761391852556", "7399906761392245772", "7399906761392262156", "7399906761392278540",
           "7399906761392294924", "7399906761392311308", "7399906761392327692", "7399906761392344076",
           "7399906761392360460", "7399906890068904979", "7399906890069429267", "7399906890069445651",
           "7399906890069462035", "7399906890069478419", "7399906890069494803", "7399906890069511187",
           "7399952345222433843", "7399952345222450227", "7399952345222515763", "7399952345222663219",
           "7399952345222679603", "7399952345222695987", "7399952345222712371", "7399952345222728755",
           "7399952345222745139", "7399952345222761523", "7399952345222777907", "7399952345222794291",
           "7399952345222810675", "7399952345222827059", "7399952345222843443", "7399952345222859827",
           "7400306254902873115", "7401103218090822683", "7401103559464389641", "7401158275641658404",
           "7401170324039224356", "7401176177328753705", "7401191208268139561", "7401193223491685388",
           "7402187910122474505", "7402561710756334603", "7402563646222437395", "7402564170141666367",
           "7402564170141682751", "7402564472043113483", "7402565735024102463", "7402565735024200767",
           "7408913120209751090", "7425532006169906227", "7425532006170266675", "7425536204962565130",
           "7425537037367479322", "7425537037367495706", "7425537037367594010", "7425537518110805042",
           "7425537637102652425", "7425538636952685594", "7425538636953013274", "7425540136253770789",
           "7425543080369507355", "7425545975999089701", "7425552650253470770", "7427045751215541298"]
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "SPUIDs": aid,
        "AssetModelBizTypes": ["accessory_sku"]
    }
    return parm


def equipmentrequest_structure(QueryValue, asset_type):
    """
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """

    if "asset_sku" in asset_type:
        return asset_sku_structure(QueryValue)
    if "asset_spu" in asset_type:
        return asset_spu_structure(QueryValue)
    if "accessory_sku" in asset_type:
        return accessory_sku_structure(QueryValue)


def equipmentreturn_structure0(QueryValue, asset_type):
    """
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """

    if "asset_sku" in asset_type:
        return asset_sku_structure0(QueryValue)
    if "asset_spu" in asset_type:
        return asset_spu_structure0(QueryValue)
    if "accessory_sku" in asset_type:
        return accessory_sku_structure0(QueryValue)


def equipmentrequest_structure0(QueryValue):
    """
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """

    if QueryValue.get("device_type") and QueryValue.get("device_type") == "asset":
        if QueryValue.get("brand") or QueryValue.get("model") or QueryValue.get("specification"):
            return asset_sku_structure(QueryValue)  # sku
        else:
            return asset_spu_structure(QueryValue)
    else:
        return accessory_sku_structure(QueryValue)


def equipmentreturn_structure(QueryValue):
    """
    设备退还时的请求参数
    """
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [
                    QueryValue.get("asset_name")
                ]
            }
        ],
        "AssetModelBizTypes": [
            "accessory_sku"
        ]
    }
    return parm


def GetBestMatchItemonline(SearchKey, HardwareMatchType, clientinfo):
    url = "https://it.bytedance.com/itam-byte/api/itservice/common/GetBestMatchItem"
    payload = json.dumps({
            "SearchKey": SearchKey,
            "TopN": 10,
            "AiUseType": 5,
            "QueryAssetModelScopeRequestV2": {
                "HardwareMatchType": HardwareMatchType,
                "TemplateType": "6883418246797986828",
                "ApplyRegionID": "7145432241957506086",
                "Page": {
                    "PageNum": 1,
                    "PageSize": 10
                }
            },
            "psm": "athena"
        })
    time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwOTI3NjksImp0aSI6ImR1M3o1UEh3ZDNla2tLUlUiLCJpYXQiOjE3NDk3OTY3NjksImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.GGUPJ3FzxW131PovtM_BUANXWUPIJTfG6zbNlb80ZIiPviQ3U0t4hxVMty9Dj4PYfiLfLMQ1r3E9xsIWfvQDL-CGC7EsnqBDT6Vc4_ZGvW_mx-z3YVzs7TJ8cKE0YZUI8gB-ZsAgztMJF5Jlja0zqdWNi7sdc-YnYISzrxv6aiY',
        'cookie': clientinfo.get(
            'cookie') or 'MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTAzMzYyMzMsImlhdCI6MTc0OTczMTQzMywiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.dMO0OWpMvIXmHGHfgxU3FRvwLOqNWAW_kiWDiHWt9wMxQd5qsi9PILBXCEYP4NVq5CaNbU_XO488CJz0vxxNh50hLdk5Jgf7n1lm-FaTJ-AtD7tqBlUl94ZB38GiAb2m7U4xC-7iHWVH2Mp-M92Z7_jgB0xJcEiDmOhlLqBviatlLGcoeAIjhpK01MA04T6Efb5M_OgeJbbqOZgl-jSdIvY6SD5my9kSzg1KE3E1caquPzYMDtgjIy9L8rkqYz0A77DXac6l0tv6daHshoPvgtc4urTV9QdT6XAYyPO_yf8ISXz03opaKkmHtZ5slIFSqgTPbLJ9Y_dmaZuX9D_NRg; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; _tea_utm_cache_1229=undefined; amuserid=7036392@bytedance.people',
        'Content-Type': 'application/json',
    }
    if clientinfo.get('x_tt_env'):
        headers['x-tt-env'] = clientinfo.get('x_tt_env')
        headers['x-use-ppe'] = '1'

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def GetBestMatchItemonline_(SearchKey, HardwareMatchType, clientinfo):
    url = "https://it.bytedance.com/itam-byte/api/itservice/common/GetBestMatchItem"
    payload = json.dumps({
        "SearchKey": SearchKey,
        "TopN": 10,
        "AiUseType": 7,
        "QueryAssetModelScopeRequestV2": {
            "HardwareMatchType": HardwareMatchType,
            "TemplateType": "6883418246797954060",
            "ApplyRegionID": "7145432241957506086",
            "Page": {
                "PageNum": 1,
                "PageSize": 10
            }
        },
        "psm": "athena"
    })
    time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwOTI3NjksImp0aSI6ImR1M3o1UEh3ZDNla2tLUlUiLCJpYXQiOjE3NDk3OTY3NjksImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.GGUPJ3FzxW131PovtM_BUANXWUPIJTfG6zbNlb80ZIiPviQ3U0t4hxVMty9Dj4PYfiLfLMQ1r3E9xsIWfvQDL-CGC7EsnqBDT6Vc4_ZGvW_mx-z3YVzs7TJ8cKE0YZUI8gB-ZsAgztMJF5Jlja0zqdWNi7sdc-YnYISzrxv6aiY',
        'cookie': clientinfo.get(
            'cookie') or 'MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTAzMzYyMzMsImlhdCI6MTc0OTczMTQzMywiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.dMO0OWpMvIXmHGHfgxU3FRvwLOqNWAW_kiWDiHWt9wMxQd5qsi9PILBXCEYP4NVq5CaNbU_XO488CJz0vxxNh50hLdk5Jgf7n1lm-FaTJ-AtD7tqBlUl94ZB38GiAb2m7U4xC-7iHWVH2Mp-M92Z7_jgB0xJcEiDmOhlLqBviatlLGcoeAIjhpK01MA04T6Efb5M_OgeJbbqOZgl-jSdIvY6SD5my9kSzg1KE3E1caquPzYMDtgjIy9L8rkqYz0A77DXac6l0tv6daHshoPvgtc4urTV9QdT6XAYyPO_yf8ISXz03opaKkmHtZ5slIFSqgTPbLJ9Y_dmaZuX9D_NRg; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; _tea_utm_cache_1229=undefined; amuserid=7036392@bytedance.people',
        'Content-Type': 'application/json'
    }
    if clientinfo.get('x_tt_env'):
        headers['x-tt-env'] = clientinfo.get('x_tt_env')
        headers['x-use-ppe'] = '1'


    response = requests.request("POST", url, headers=headers, data=payload)
    response0 = json.loads(response.text)
    response1 = json.loads(response.text)
    if HardwareMatchType == 2:
        if response0['data'].get('AiBorrowAndUseResponseList'):
            for i in response0['data']['AiBorrowAndUseResponseList']:
                if str(i['OutOfStock']) == 'True':
                    response1['data']['AiBorrowAndUseResponseList'].remove(i)
                else:
                    pass
            return response1
    return json.loads(response.text)

def GetBestMatchItemonline_software(SearchKey, Description, clientinfo):
    url = "https://it.bytedance.com/itam-byte/api/itservice/common/GetBestMatchItem"
    payload = json.dumps({
        "SearchKey":"","TopN":5,"AiUseType":100,
        "SoftwareApplyRequest":{"Size":3,
                                "Name":SearchKey,
                                "Description":""},
        "psm":"athena"})
    time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwOTI3NjksImp0aSI6ImR1M3o1UEh3ZDNla2tLUlUiLCJpYXQiOjE3NDk3OTY3NjksImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.GGUPJ3FzxW131PovtM_BUANXWUPIJTfG6zbNlb80ZIiPviQ3U0t4hxVMty9Dj4PYfiLfLMQ1r3E9xsIWfvQDL-CGC7EsnqBDT6Vc4_ZGvW_mx-z3YVzs7TJ8cKE0YZUI8gB-ZsAgztMJF5Jlja0zqdWNi7sdc-YnYISzrxv6aiY',
        'cookie': clientinfo.get(
            'cookie') or 'MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTAzMzYyMzMsImlhdCI6MTc0OTczMTQzMywiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.dMO0OWpMvIXmHGHfgxU3FRvwLOqNWAW_kiWDiHWt9wMxQd5qsi9PILBXCEYP4NVq5CaNbU_XO488CJz0vxxNh50hLdk5Jgf7n1lm-FaTJ-AtD7tqBlUl94ZB38GiAb2m7U4xC-7iHWVH2Mp-M92Z7_jgB0xJcEiDmOhlLqBviatlLGcoeAIjhpK01MA04T6Efb5M_OgeJbbqOZgl-jSdIvY6SD5my9kSzg1KE3E1caquPzYMDtgjIy9L8rkqYz0A77DXac6l0tv6daHshoPvgtc4urTV9QdT6XAYyPO_yf8ISXz03opaKkmHtZ5slIFSqgTPbLJ9Y_dmaZuX9D_NRg; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; _tea_utm_cache_1229=undefined; amuserid=7036392@bytedance.people',
        'Content-Type': 'application/json',

    }
    if clientinfo.get('x_tt_env'):
        headers['x-tt-env'] = clientinfo.get('x_tt_env')
        headers['x-use-ppe'] = '1'
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)

def GetBestMatchItemoff0(SearchKey, HardwareMatchType, clientinfo):
    url = "https://it-pre.bytedance.net/itam-byte/api/itservice/common/GetBestMatchItem"

    if HardwareMatchType==1:
       pr = {"SearchKey":SearchKey,"TopN":10,"AiUseType":7,
          "QueryAssetModelScopeRequestV2":
              {"HardwareMatchType":HardwareMatchType,
               "TemplateType":"6848436666751798285",
               "ApplyRegionID":"7468013511194643493",
               "Page":{"PageNum":1,"PageSize":10}},"psm":"athena"}
    if HardwareMatchType==2:
        pr = {"SearchKey":SearchKey,"TopN":10,"AiUseType":7,
              "QueryAssetModelScopeRequestV2":
                  {"HardwareMatchType":HardwareMatchType,
                   "TemplateType":"7534557229471796234",
                   "ApplyRegionID":"7509062433064029194","Page":{"PageNum":1,"PageSize":10}},"psm":"athena"}



    payload = json.dumps(pr)
    # time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTk0MTc3ODEsImp0aSI6IkVXSUNmT0k5WVBCZVdKSTkiLCJpYXQiOjE3NTgxMjE3ODEsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.MmENqyPY7k4KMz9ufbxzpIZXOnLaoYAAyv3J2T0OMz6tcd1IyEhYJd1cFjzqLw26NnWe4bfglki7zmIVQduftIJc8QaRcXDjDszCfG4DfH2O7zQTi7cwptt_o-CxI6E6osRhYmJ7dwaSWw1hBRlnBNJMbyzUlHRspJz-hox_oGA',
        'cookie': clientinfo.get(
            'cookie') or '_ga=GA1.1.1854125625.1750232273; _ga_FVWC4GKEYS=GS2.1.s1750301537$o2$g1$t1750301683$j60$l0$h0; X-Risk-Browser-Id=8f55035c3e943940f7e4eea73ae96e203e00887d4e38ec8b0f918e6477c34ef8; people-lang=zh; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; email=liujunmei@bytedance.com; user_token=JTdCJTIybmFtZSUyMiUzQSUyMiVFNSU4OCU5OCVFNCVCRiU4QSVFNiVBMiU4NSUyMiUyQyUyMmZ1bGxfbmFtZSUyMiUzQSUyMiVFNSU4OCU5OCVFNCVCRiU4QSVFNiVBMiU4NSUyMDM4MzAzMTklMjIlMkMlMjJlbWFpbCUyMiUzQSUyMmxpdWp1bm1laSU0MGJ5dGVkYW5jZS5jb20lMjIlMkMlMjJwaWN0dXJlJTIyJTNBJTIyaHR0cHMlM0ElMkYlMkZzMS1pbWZpbGUuZmVpc2h1Y2RuLmNvbSUyRnN0YXRpYy1yZXNvdXJjZSUyRnYxJTJGdjNfMDBrOF81ZDBhNDk4MS0zMDJkLTQwMTEtOGJmMy0yNDYzZDhkY2IxMWd+JTNGaW1hZ2Vfc2l6ZSUzRDI0MHgyNDAlMjZjdXRfdHlwZSUzRCUyNnF1YWxpdHklM0QlMjZmb3JtYXQlM0RwbmclMjZzdGlja2VyX2Zvcm1hdCUzRC53ZWJwJTIyJTJDJTIyZW1wbG95ZWVfaWQlMjIlM0ElMjIzODMwMzE5JTIyJTJDJTIyZW1wbG95ZWVfbnVtYmVyJTIyJTNBJTIyMzgzMDMxOSUyMiUyQyUyMnRlbmFudF9hbGlhcyUyMiUzQSUyMmJ5dGVkYW5jZSUyMiUyQyUyMnVzZXJfaWQlMjIlM0ElMjJkZWdubjk2MWtma2treW9waDd5cyUyMiU3RA==; amuserid=3830319@bytedance.people; titan_passport_id=cn/bytedance/89511df1-02a0-412c-907d-fd5079b66ebe; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1229=undefined; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTg4MTU4NzQsImlhdCI6MTc1ODIxMTA3NCwiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.IkLCCJrY4uuskameDvQpPgArxbEpS7P202Q46tGJkqNm5JrV73SvAeRtU9jNtbBRruTwQnlyuZYpIcGy2CJq1UiBLLb34jGhnoqw6-v6C2s3sKu5OYuHNcPYHvYTbUi7aqVxYeJWA7ag0Wx0rmdjb250oZkmurQKbdVFq8mihfHUumm55LskBcsA2ai5WHX4fNPzJ63GNJt0CvWnAOIPT7cvY8qZWZhbqqyfVL6gdkPAxiCR6mLmjkg0Jrrl84jbPM3LQxaySGZ91vU5WuRpnpn_ITBXDtvySTEN63lFj0IkaiNxgjQQXonPEnndgoDI3Q1N-Jif-MFlucgy8a04MA',
        'Content-Type': 'application/json',
        'x-use-ppe': '1',
        'x-tt-env': 'ppe_itam_feat_vector_opt_nym'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)

def GetBestMatchItemoff(SearchKey, HardwareMatchType, clientinfo):
    url = "https://it-pre.bytedance.net/itam-byte/api/itservice/common/GetBestMatchItem"

    if HardwareMatchType==1:
       pr = {"SearchKey":SearchKey,"TopN":10,"AiUseType":5,
          "QueryAssetModelScopeRequestV2":
              {"HardwareMatchType":HardwareMatchType,
               "TemplateType":"6848436753938779140",
               "ApplyRegionID":"7468013511194643493",
               "Page":{"PageNum":1,"PageSize":10}},"psm":"athena"}
    if HardwareMatchType==2:
        pr = {"SearchKey":SearchKey,"TopN":10,"AiUseType":5,
              "QueryAssetModelScopeRequestV2":
                  {"HardwareMatchType":HardwareMatchType,
                   "TemplateType":"6848436753938779140",
                   "ApplyRegionID":"7509062433064029194","Page":{"PageNum":1,"PageSize":10}},"psm":"athena"}



    payload = json.dumps(pr)
    # time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTk0MTc3ODEsImp0aSI6IkVXSUNmT0k5WVBCZVdKSTkiLCJpYXQiOjE3NTgxMjE3ODEsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.MmENqyPY7k4KMz9ufbxzpIZXOnLaoYAAyv3J2T0OMz6tcd1IyEhYJd1cFjzqLw26NnWe4bfglki7zmIVQduftIJc8QaRcXDjDszCfG4DfH2O7zQTi7cwptt_o-CxI6E6osRhYmJ7dwaSWw1hBRlnBNJMbyzUlHRspJz-hox_oGA',
        'cookie': clientinfo.get(
            'cookie') or '_ga=GA1.1.1854125625.1750232273; _ga_FVWC4GKEYS=GS2.1.s1750301537$o2$g1$t1750301683$j60$l0$h0; X-Risk-Browser-Id=8f55035c3e943940f7e4eea73ae96e203e00887d4e38ec8b0f918e6477c34ef8; people-lang=zh; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; email=liujunmei@bytedance.com; user_token=JTdCJTIybmFtZSUyMiUzQSUyMiVFNSU4OCU5OCVFNCVCRiU4QSVFNiVBMiU4NSUyMiUyQyUyMmZ1bGxfbmFtZSUyMiUzQSUyMiVFNSU4OCU5OCVFNCVCRiU4QSVFNiVBMiU4NSUyMDM4MzAzMTklMjIlMkMlMjJlbWFpbCUyMiUzQSUyMmxpdWp1bm1laSU0MGJ5dGVkYW5jZS5jb20lMjIlMkMlMjJwaWN0dXJlJTIyJTNBJTIyaHR0cHMlM0ElMkYlMkZzMS1pbWZpbGUuZmVpc2h1Y2RuLmNvbSUyRnN0YXRpYy1yZXNvdXJjZSUyRnYxJTJGdjNfMDBrOF81ZDBhNDk4MS0zMDJkLTQwMTEtOGJmMy0yNDYzZDhkY2IxMWd+JTNGaW1hZ2Vfc2l6ZSUzRDI0MHgyNDAlMjZjdXRfdHlwZSUzRCUyNnF1YWxpdHklM0QlMjZmb3JtYXQlM0RwbmclMjZzdGlja2VyX2Zvcm1hdCUzRC53ZWJwJTIyJTJDJTIyZW1wbG95ZWVfaWQlMjIlM0ElMjIzODMwMzE5JTIyJTJDJTIyZW1wbG95ZWVfbnVtYmVyJTIyJTNBJTIyMzgzMDMxOSUyMiUyQyUyMnRlbmFudF9hbGlhcyUyMiUzQSUyMmJ5dGVkYW5jZSUyMiUyQyUyMnVzZXJfaWQlMjIlM0ElMjJkZWdubjk2MWtma2treW9waDd5cyUyMiU3RA==; amuserid=3830319@bytedance.people; titan_passport_id=cn/bytedance/89511df1-02a0-412c-907d-fd5079b66ebe; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1229=undefined; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTg4MTU4NzQsImlhdCI6MTc1ODIxMTA3NCwiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.IkLCCJrY4uuskameDvQpPgArxbEpS7P202Q46tGJkqNm5JrV73SvAeRtU9jNtbBRruTwQnlyuZYpIcGy2CJq1UiBLLb34jGhnoqw6-v6C2s3sKu5OYuHNcPYHvYTbUi7aqVxYeJWA7ag0Wx0rmdjb250oZkmurQKbdVFq8mihfHUumm55LskBcsA2ai5WHX4fNPzJ63GNJt0CvWnAOIPT7cvY8qZWZhbqqyfVL6gdkPAxiCR6mLmjkg0Jrrl84jbPM3LQxaySGZ91vU5WuRpnpn_ITBXDtvySTEN63lFj0IkaiNxgjQQXonPEnndgoDI3Q1N-Jif-MFlucgy8a04MA',
        'Content-Type': 'application/json',
        'x-use-ppe': '1',
        'x-tt-env': 'ppe_itam_feat_vector_opt_nym'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)
def GetBestMatchItemonline_old(SearchKey, HardwareMatchType, clientinfo):
    url = "https://it.bytedance.com/itam-byte/api/itservice/common/GetBestMatchItem"
    payload = json.dumps({
        "SearchKey": SearchKey,
        "TopN": 1000,
        "AiUseType": 3,
        "QueryAssetModelScopeRequest":
            {"FlowTemplateIDs":
                 ["6883468409742298119", "7514160571177913371", "6885245774565739523", "6883468929408437256",
                  "6883715234721188867", "6883457792222579716"],
             "SearchName": "",
             "ApplyRegionID": "7145432241957506086",
             "Page": {"PageNum": 1, "PageSize": 1000}, "Request": {}}, "psm": "athena"}
    )
    time.sleep(5)
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwOTI3NjksImp0aSI6ImR1M3o1UEh3ZDNla2tLUlUiLCJpYXQiOjE3NDk3OTY3NjksImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.GGUPJ3FzxW131PovtM_BUANXWUPIJTfG6zbNlb80ZIiPviQ3U0t4hxVMty9Dj4PYfiLfLMQ1r3E9xsIWfvQDL-CGC7EsnqBDT6Vc4_ZGvW_mx-z3YVzs7TJ8cKE0YZUI8gB-ZsAgztMJF5Jlja0zqdWNi7sdc-YnYISzrxv6aiY',
        'cookie': clientinfo.get(
            'cookie') or 'MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; bd_sso_3b6da9=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTAzMzYyMzMsImlhdCI6MTc0OTczMTQzMywiaXNzIjoic3NvLmJ5dGVkYW5jZS5jb20iLCJzdWIiOiJkZWdubjk2MWtma2treW9waDd5cyIsInRlbmFudF9pZCI6ImhncTN0Y2NwM2kxc2pqbjU4emlrIn0.dMO0OWpMvIXmHGHfgxU3FRvwLOqNWAW_kiWDiHWt9wMxQd5qsi9PILBXCEYP4NVq5CaNbU_XO488CJz0vxxNh50hLdk5Jgf7n1lm-FaTJ-AtD7tqBlUl94ZB38GiAb2m7U4xC-7iHWVH2Mp-M92Z7_jgB0xJcEiDmOhlLqBviatlLGcoeAIjhpK01MA04T6Efb5M_OgeJbbqOZgl-jSdIvY6SD5my9kSzg1KE3E1caquPzYMDtgjIy9L8rkqYz0A77DXac6l0tv6daHshoPvgtc4urTV9QdT6XAYyPO_yf8ISXz03opaKkmHtZ5slIFSqgTPbLJ9Y_dmaZuX9D_NRg; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; _tea_utm_cache_1508={%22utm_source%22:%22startup%22%2C%22utm_medium%22:%22chrome%22}; _tea_utm_cache_1229=undefined; amuserid=7036392@bytedance.people',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)


def GetBestMatchItemandres(keyword0, HardwareMatchType, clientinfo):
    list = {"Score": 0, "Name": "name"
            }
    lista, listc = [], []
    for i in keyword0:
        res0 = GetBestMatchItemonline(i, HardwareMatchType, clientinfo)['data']
        print(1)
        time.sleep(5)
        listb = {}
        if res0.get('AiBorrowAndUseResponseList'):
            res = res0['AiBorrowAndUseResponseList']
            for j in res:
                listb = {}
                lista = []
                list["Score"] = j['Score']
                list["Name"] = j['AccessoryModelScope']['AccessoryModelInfo']['Name']['ValueZh']
                lista.append(copy.deepcopy(list))
            listb = {"key": i, "res": lista}
        listc.append(copy.deepcopy(listb))
    return listc


def test_hardware_match(keyword0, HardwareMatchType, clientinfo):
    url = "https://open-itam-mig-pre.bytedance.net/v1/test_hardware_match"
    payload = json.dumps({
        "hardware_type": HardwareMatchType,
        "search_key": keyword0
    })
    headers = {
        'Authorization': clientinfo.get(
            'authorization') or 'Basic cm40cmFpdTRwenY1cGlsYTo2bWhvOXV3ZXFrOHZpbDllcXRxMHZ1YmVnc2xjeXBucg==',
        'x-use-ppe': '1',
        'x-tt-env': 'ppe_es_test_match',
        'Content-Type': 'application/json'
    }
    time.sleep(3)

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

    return json.loads(response.text)


def searchListAssetModelScope(key, HardwareMatchType, clientinfo):
    if HardwareMatchType == 1:
        url = f"https://it.bytedance.com/itam-byte/api/itservice/searchListAssetModelScope?FlowTemplateIDs=6883468409742298119,7514160571177913371,6885245774565739523,6883468929408437256,6883715234721188867,6883457792222579716&SearchName={key}&pageNum=1&pageSize=30&applyRegionID=7145432241957506086&AccessoryApplyType=1"
    else:
        url = f"https://it.bytedance.com/itam-byte/api/itservice/searchListAssetModelScope?FlowTemplateIDs=6883468409742298119,7514160571177913371,6885245774565739523,6883468929408437256,6883715234721188867,6883457792222579716&SearchName={key}&pageNum=1&pageSize=30&applyRegionID=7145432241957506086&AccessoryApplyType=1"

    payload = {}
    headers = {
        'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwMDU1MjQsImp0aSI6IktJVVI5ZkdoZ2Q1cyt4NWIiLCJpYXQiOjE3NDk3MDk1MjQsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.wtuTgUI6posLTQ-WJU539NuIYbMCgYqBrCOvdigR09h8zl_VO7tUJ4GSmfjDH8jZjtGSF-nEoDLPbX2z4BZkwtvoh--oa8KP-IIOOk2KQS2lVHz1mE7HWaEdCpml1_DS0PJB42F3B-L0EjRqQki_g3Jjn1kZjMgwFqpFW-TwcpY',
        'cookie': '_tea_utm_cache_1229=undefined; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; amuserid=3830319@bytedance.people; msToken=TYcrN_92buBPnrV9MSb8i_0Uvz5lFxoWtnz8PA8MhLaAtrddfSUuR69V8vEJvRwEMDOyOAFL-PY87wN-oA4tKDroSbEvsjPNFn202nmCEcO9rKH9KINPWA=='
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return json.loads(response.text)


def SoftwareApplyGetBestMatchItem(key, clientinfo):
    url = "https://it.bytedance.com/itam-byte/api/itservice/common/GetBestMatchItem"
    payload = json.dumps({
        "SearchKey": "",
        "TopN": 5,
        "AiUseType": 100,
        "SoftwareApplyRequest": {
            "Size": 3,
            "Name": key,
            "Description": ""
        },
        "psm": "athena"
    })
    headers = {
        'authorization': clientinfo.get(
            'authorization') or 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InYyIiwidHlwIjoiSldUIn0.eyJleHAiOjE3NTEwMDU1MjQsImp0aSI6IktJVVI5ZkdoZ2Q1cyt4NWIiLCJpYXQiOjE3NDk3MDk1MjQsImlzcyI6InRhbm5hIiwic3ViIjoiMzgzMDMxOUBieXRlZGFuY2UucGVvcGxlIiwidGVuYW50X2lkIjoiYnl0ZWRhbmNlLnBlb3BsZSIsInRlbmFudF9uYW1lIjoiIiwicHJvamVjdF9rZXkiOiJjcm1TZmdIVmU1dXhIMHJyIiwidW5pdCI6ImV1X25jIiwiYXV0aF9ieSI6Mn0.wtuTgUI6posLTQ-WJU539NuIYbMCgYqBrCOvdigR09h8zl_VO7tUJ4GSmfjDH8jZjtGSF-nEoDLPbX2z4BZkwtvoh--oa8KP-IIOOk2KQS2lVHz1mE7HWaEdCpml1_DS0PJB42F3B-L0EjRqQki_g3Jjn1kZjMgwFqpFW-TwcpY',
        'cookie': clientinfo.get(
            'cookie') or '_tea_utm_cache_1229=undefined; MONITOR_WEB_ID=ce5a3279-6ed5-4ede-9b00-29aa7c1a1311; amuserid=3830319@bytedance.people; msToken=TYcrN_92buBPnrV9MSb8i_0Uvz5lFxoWtnz8PA8MhLaAtrddfSUuR69V8vEJvRwEMDOyOAFL-PY87wN-oA4tKDroSbEvsjPNFn202nmCEcO9rKH9KINPWA==',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    time.sleep(5)

    return json.loads(response.text)


if __name__ == '__main__':
    info = {
        'input': {'用户输入/userInput': 'Autodesk 3Ds MAX'},
        'output': {'用户输入/output': 'Autodesk 3Ds MAX'},
        'rt': True,
        'label': []

    }
    info_list = []
    a = 0
    # 读取文件it_assistant/data/software_spu.csv
    with open('data/software_spu.csv', 'r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['name_zh'] != "--":
                a = a + 1

                row_ = row['name_zh'].lower()
                row_ = row_.replace(' ', '')
                info['input'] = {'用户输入/userInput': row['name_zh']}
                info['output'] = {'用户输入/output': row_}
                res = json.loads(get_query_vector(0.6, [row_], 4, "vec_name"))
                for i in res['body']['Results']:
                    info['label'].append({'socre': i['Score'], 'label': i['Item']['name_zh']})
                print(a)
            info_list.append(copy.deepcopy(info))
            # 将info_list写入本地文件
        # 异常报错或退出时将info_list写入本地文件

    with open('test_data/software_spu_res_xiaoxie.csv', 'w', encoding='utf-8') as file:
        json.dump(info_list, file, ensure_ascii=False)
