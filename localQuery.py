import json
import logging

import requests
from requests.adapters import HTTPAdapter

import geo
import translate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
spToEngDict = json.load(open('assets/assets.json', 'r', encoding='utf-8'))
iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
geoDict = json.load(open('assets/geocoding.json', 'r', encoding='utf-8'))
session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=2))
combineQuery = True


def toEnglish(text: str) -> str:
    """
    转换为英文
    :param text: str, 要转换的文本
    :return: str, 英文
    """
    if text in spToEngDict:
        return spToEngDict[text]
    else:
        return translate.translate(session, text, "en", "auto")


def search_cmp(country=None, prov=None):
    if prov in geoDict[country]:
        return geoDict[country][prov][0], geoDict[country][prov][1]
    else:
        tmp = None
        for j in geoDict[country]:
            tmp = geoDict[country][j][0], geoDict[country][j][1]
            if j in prov or prov in j:
                break
        return tmp


def search(countryRaw: str, provRaw: str):
    """
    根据国家和省份查询经纬度 by English
    :param countryRaw: str, 国家
    :param provRaw: str, 省份
    :return: tuple(lat:float, lng:float, msg:str)
    """
    country = toEnglish(countryRaw)
    prov = toEnglish(provRaw)
    tmp = None
    if country in geoDict:
        _ = search_cmp(country, prov)
        return _[0], _[1], provRaw + ',' + countryRaw
    else:
        for i in geoDict:
            if country in i or i in country:
                _ = search_cmp(i, prov)
                return _[0], _[1], provRaw + ',' + countryRaw
        if combineQuery:
            from externalQuery import search as search_external
            return search_external(countryRaw, provRaw)
        else:
            for i in geoDict:
                for j in geoDict[i]:
                    if j in prov or prov in j:
                        tmp = geoDict[i][j][0], geoDict[i][j][1], provRaw + ',' + countryRaw
                        return tmp
        logging.warning(f'{countryRaw},{provRaw} not found')
        return tmp


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0','Prov0'],['Country1','Prov1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    coordinatesList = []
    for i in geoRawDataList:
        coordinateList = geo.geocodingSingle(i, localQuery=True)
        if coordinateList and len(coordinateList):
            coordinatesList.append(coordinateList)
    return coordinatesList
