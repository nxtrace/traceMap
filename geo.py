import json
import logging
import time

import requests

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
session = requests.session()


def getRawData(rawData: dict) -> list:
    """
    获取原始数据
    :param rawData: dict, 原始数据
    :return: [['Country0']['Prov0'],['Country1']['Prov1'],...]
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


def search(country: str, prov: str):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :return: tuple(lat:float, lng:float)
    """
    # tmp = None
    # for index, row in df.iterrows():
    #     if (str(row['Country']) in country) or (country in str(row['Country'])):
    #         tmp = row['lat'], row['lng']
    #         if prov == '' and (country == 'China' or country == 'CN'):
    #             return None
    #         if (str(row['Province']) in prov) or (prov in str(row['Province'])):
    #             return row['lat'], row['lng']
    # for index, row in df.iterrows():
    #     if (str(row['Province']) in prov) or (prov in str(row['Province'])):
    #         return row['lat'], row['lng']
    # logging.info('{} {} not match,return {}'.format(country, prov, tmp))
    # return tmp
    addr = prov + ',' + country
    try:
        r = session.get(f'https://nominatim.openstreetmap.org/search/{addr}?limit=1&format=json')
        r = r.json()[0]
    except IndexError:
        logging.info('{} {} not found by osmApi'.format(country, prov))
        return None
    return r['lat'], r['lon']


def geocodingSingle(addrList: list) -> list:
    """
    单个地址转经纬度
    :param addrList: list, 地址信息，格式为[国家, 省份]
    :return: list[lat:float, lng:float], 经纬度
    """
    if len(addrList[0]) == 2:
        if addrList[0] in iso3166MapDict:
            country = iso3166MapDict[addrList[0]]
        else:
            country = addrList[0]
    else:
        country = addrList[0]
    logging.debug('country: {}'.format(country))
    prov = addrList[1]
    logging.debug('prov: {}'.format(prov))
    coordinateTuple = search(country, prov)
    if coordinateTuple:
        return [coordinateTuple[0], coordinateTuple[1]]
    else:
        if not ((country == 'China') and (prov == '')):
            logging.info('{}, {} not found'.format(country, prov))
        return []


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0']['Prov0'],['Country1']['Prov1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float],[lat1:float, lng1:float],...]
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
    :return: list, 经纬度:[[lat0:float, lng0:float],[lat1:float, lng1:float],...]
    """
    session = requests.session()
    geoRawDataList = getRawData(rawData)
    logging.debug('geoRawDataList: {}'.format(geoRawDataList))
    coordinatesList = geocoding(geoRawDataList)
    if not coordinatesList:
        logging.warning('没有搜索到任何数据\nrawData:\n{}'.format(rawData))
    return coordinatesList


if __name__ == '__main__':
    t0 = time.time()
    res0 = geoInterface(json.load(open("tmp.json")))
    t1 = time.time()
    print(f"costTime:{t1 - t0}")
    print(res0)
