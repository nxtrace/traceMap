import json
import logging

import requests

logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')
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


def geocodingSingle(addrList: list, localQuery: bool):
    """
    单个地址转经纬度
    :param localQuery: bool, 是否使用本地数据
    :param addrList: list, 地址信息，格式为[国家, 省份]
    :return: list[lat:float, lng:str, msg:float], 经纬度
    """
    if len(addrList[0].encode()) == 2:
        if addrList[0] in iso3166MapDict:
            country = iso3166MapDict[addrList[0]]
        else:
            country = addrList[0]
    else:
        country = addrList[0]
    logging.debug('country: {}'.format(country))
    prov = addrList[1]
    logging.debug('prov: {}'.format(prov))
    if localQuery:
        from localQuery import search
    else:
        from externalQuery import search
    coordinateTuple = search(country, prov)
    if len(coordinateTuple)==3:
        logging.debug(f"coordinateTuple: {[coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]}")
        return [coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]
    else:
        if not ((country == 'China') and (prov == '')):
            logging.info('{}, {} not found'.format(country, prov))
        return None


def geoInterface(rawData: dict, localQuery: bool) -> list:
    """
    地址转经纬度接口
    :param localQuery: bool, 是否使用本地数据
    :param rawData: dict, 原始数据
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    geoRawDataList = getRawData(rawData)
    logging.debug('geoRawDataList: {}'.format(geoRawDataList))
    if localQuery:
        from localQuery import geocoding
    else:
        from externalQuery import geocoding
    coordinatesList = geocoding(geoRawDataList)
    if not coordinatesList:
        logging.warning('没有搜索到任何数据\nrawData:\n{}'.format(rawData))
    return coordinatesList
