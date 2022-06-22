import json
import logging

import pandas as pd
import requests
from requests.adapters import HTTPAdapter

import geo
import translate

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
spToEngDict = json.load(open('assets/assets.json', 'r', encoding='utf-8'))
iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=2))


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


def search(country: str, prov: str, geocodingCsvPath: str = 'assets/geocoding2.csv'):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :param geocodingCsvPath: str, 经纬度文件路径
    :return: tuple(lat:float, lng:float, msg:str)
    """
    country = toEnglish(country)
    prov = toEnglish(prov)
    df = pd.read_csv(geocodingCsvPath, delimiter=",")
    tmp = None
    for index, row in df.iterrows():
        if (str(row['Country']) in country) or (country in str(row['Country'])):
            tmp = row['lat'], row['lng'], prov + ',' + country
            if prov == '' and (country == 'China' or country == 'CN'):
                return None
            if (str(row['Province']) in prov) or (prov in str(row['Province'])):
                return row['lat'], row['lng'], prov + ',' + country
    for index, row in df.iterrows():
        if (str(row['Province']) in prov) or (prov in str(row['Province'])):
            return row['lat'], row['lng'], prov + ',' + country
    logging.info('{} {} not match,return {}'.format(country, prov, tmp))
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
        if len(coordinateList):
            coordinatesList.append(coordinateList)
    return coordinatesList
