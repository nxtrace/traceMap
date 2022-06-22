import json
import logging

import requests
import threadpool

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
session = requests.session()
cb = []


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


def search(country: str, prov: str):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :return: tuple(lat:str, lng:str, msg:str)
    """
    addr = prov + ',' + country
    logging.debug(f'addr:{addr}')
    if (country == 'China') or (country == '中国'):
        if prov == '':
            return None
        if prov == 'Taiwan':
            return "23.9739374", "120.9820179", "Taiwan Province,China"
    try:
        r = session.get(f'https://nominatim.openstreetmap.org/search/{addr}?limit=1&format=json')
        r = r.json()[0]
    except IndexError:
        logging.info('{} {} not found by osmApi'.format(country, prov))
        return None
    return r['lat'], r['lon'], addr


def geocodingSingle(addrList: list) -> list:
    """
    单个地址转经纬度
    :param addrList: list, 地址信息，格式为[国家, 省份]
    :return: list[lat:str, lng:str, msg:str], 经纬度
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
    coordinateTuple = search(country, prov)
    if coordinateTuple:
        logging.debug(f"coordinateTuple: {[coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]}")
        return [coordinateTuple[0], coordinateTuple[1], coordinateTuple[2]]
    else:
        if not ((country == 'China') and (prov == '')):
            logging.info('{}, {} not found'.format(country, prov))
        return []


def threadRun(geoRawData: list):
    """
    :param geoRawData: list, 地址集:['Country','Prov']
    """
    coordinateList = geocodingSingle(geoRawData)
    return coordinateList


def save_callback(request, result):
    """
    回调函数 输出结果: [lat:float, lng:float, msg:str] 插入到cb.append \n
    :param request: 可以访问request.requestID
    :param result: tasks执行完的结果
    """
    output = ""
    if result:
        output = [float(result[0]), float(result[1]), str(result[2])]
        cb.append((request.requestID, output))
    logging.debug(f"request.requestID, result = {request.requestID}, {output}")


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0','Prov0'],['Country1','Prov1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    coordinatesList = []
    pool = threadpool.ThreadPool(8)
    tasks = threadpool.makeRequests(threadRun, geoRawDataList, save_callback)
    [pool.putRequest(task) for task in tasks]
    pool.wait()
    cb.sort(key=lambda x: x[0])
    logging.debug(f"callbackResult = {cb}")
    for i in cb:
        try:
            if i[1][0]:
                coordinatesList.append(i[1])
        except (TypeError, IndexError):
            continue
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
