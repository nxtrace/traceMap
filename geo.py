import translate
from __init__ import *

iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))


def listToStr(rawList: list) -> str:
    """
    列表转字符串
    :param rawList: list, 列表
    :return: str, 字符串
    """
    resStr = ''
    for i in rawList:
        if type(i) is not str:
            i = str(i)
        if i:
            if resStr:
                resStr += ','
            resStr += i
    return resStr


def getRawData(rawData: dict, localQuery: bool) -> list:
    """
    获取原始数据
    :param localQuery: bool, 是否为本地查询
    :param rawData: dict, 原始数据
    :return: [['Country0','Prov0','extraMsg0'],['Country1','Prov1','extraMsg1'],...]
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
                    geoRawDataList.append([
                        time['Geo']['Country'],
                        time['Geo']['Prov'],
                        listToStr([
                            time['Geo']['City'],
                            time['Geo']['District'],
                            'IP:' + time['Address']['IP'],
                            ('asn:' + time['Geo']['Asnumber']) if time['Geo']['Asnumber'] else '',
                            'TTL:' + str(time['TTL']),
                            f"RTT:{time['RTT'] / 10e5:.1f}ms",
                            ('Owner:' + time['Geo']['Owner']) if time['Geo']['Owner'] else '',
                            ('ISP:' + time['Geo']['Isp']) if time['Geo']['Isp'] else '',
                        ])
                    ])
                break
    if localQuery:
        geoRawDataList = translate.dictTranslate(geoRawDataList)
    logging.debug('geoRawDataList: {}'.format(geoRawDataList))
    return geoRawDataList


def geocodingSingle(addrList: list, localQuery: bool):
    """
    单个地址转经纬度
    :param localQuery: bool, 是否为本地查询
    :param addrList: list, 地址信息，格式为[国家, 省份, 额外信息]
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
    extraMsg = addrList[2]
    if localQuery:
        from localQuery import search
    else:
        from externalQuery import search
    coordinateTuple = search(country, prov)
    if coordinateTuple and len(coordinateTuple) == 3:
        tmpMsg = coordinateTuple[2] + ',' + extraMsg
        logging.debug(f"coordinateTuple: {[coordinateTuple[0], coordinateTuple[1], tmpMsg]}")
        return [coordinateTuple[0], coordinateTuple[1], tmpMsg]
    else:
        if not ((country == 'China') and (prov == '')):
            logging.info('{}, {} not found'.format(country, prov))
        return None


def geoInterface(rawData: dict, localQuery: bool) -> list:
    """
    地址转经纬度接口
    :param localQuery: bool, 是否为本地查询
    :param rawData: dict, 原始数据
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    geoRawDataList = getRawData(rawData, localQuery)
    if localQuery:
        from localQuery import geocoding
    else:
        from externalQuery import geocoding
    coordinatesList = geocoding(geoRawDataList)
    if not coordinatesList:
        logging.warning('没有搜索到任何数据\nrawData:\n{}'.format(rawData))
    logging.debug('coordinatesList: {}'.format(coordinatesList))
    return coordinatesList
