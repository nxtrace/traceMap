import json
import logging

import pandas as pd
import requests

from translate import translate

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
spToEngDict = json.load(open('assets/assets.json', 'r', encoding='utf-8'))
iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
session = requests.session()


def getRawData(rawData: dict) -> list:
    """
    获取原始数据
    :param rawData: dict, 原始数据
    :return: [['Country0','Prov0'],['Country1','Prov1'],...]
    """
    logging.debug('rawData: {}'.format(rawData))
    hopsList = rawData['Hops']
    logging.debug('hopsList: {}'.format(hopsList))
    geoRawDataList = []
    for hop in hopsList:
        for time in hop:
            try:
                if time['Geo']['Country'] == 'LAN Address':
                    break
            except TypeError:
                break
            if time['Success']:
                if time['Geo']['Country']:
                    geoRawDataList.append([time['Geo']['Country'], time['Geo']['Prov']])
                break
    return geoRawDataList


def search(country: str, prov: str, geocodingCsvPath: str):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :param geocodingCsvPath: str, 经纬度文件路径
    :return: tuple(lat:float, lng:float, msg:str)
    """
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


# TODO 改为多线程
def toEnglish(text: str) -> str:
    """
    转换为英文
    :param text: str, 要转换的文本
    :return: str, 英文
    """
    if text in spToEngDict:
        return spToEngDict[text]
    else:
        return translate(session, text, "en", "auto")


def geocodingSingle(addrList: list) -> list:
    """
    单个地址转经纬度
    :param addrList: list, 地址信息，格式为[国家, 省份]
    :return: list[lat:float, lng:float], 经纬度
    """
    if len(addrList[0].encode()) == 2:
        if addrList[0] in iso3166MapDict:
            country = iso3166MapDict[addrList[0]]
        else:
            country = toEnglish(addrList[0])
    else:
        country = toEnglish(addrList[0])
    logging.debug('country: {}'.format(country))
    prov = toEnglish(addrList[1])
    logging.debug('prov: {}'.format(prov))
    coordinateTuple = search(country, prov, 'assets/geocoding2.csv')
    if coordinateTuple:
        logging.debug(f"coordinateTuple: {[coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]}")
        return [coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]
    else:
        if not ((country == 'China') and (prov == '')):
            logging.info('{}, {} not found'.format(country, prov))
        return []


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0']['Prov0'],['Country1']['Prov1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    coordinatesList = []
    for i in geoRawDataList:
        coordinateList = geocodingSingle(i)
        if len(coordinateList):
            coordinatesList.append(coordinateList)
    return coordinatesList


def geoInterface(rawData: dict) -> list:
    """
    地址转经纬度接口
    :param rawData: dict, 原始数据
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    geoRawDataList = getRawData(rawData)
    logging.debug('geoRawDataList: {}'.format(geoRawDataList))
    coordinatesList = geocoding(geoRawDataList)
    if not coordinatesList:
        logging.warning('没有搜索到任何数据\nrawData:\n{}'.format(rawData))
    return coordinatesList
