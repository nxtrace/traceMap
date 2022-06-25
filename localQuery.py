import geo
from __init__ import *
from externalQuery import search as search_external

iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
geoDict = json.load(open('assets/geocoding.json', 'r', encoding='utf-8'))
combineQuery = True
spCountryList = ["Russia", "Canada", "China", "United States of America", "Brazil", "Australia", "India", "Argentina",
                 "Japan", "Vietnam", "Kazakhstan"]


def search_cmp(country=None, prov=None):
    if country in spCountryList and prov == "":
        return
    # DEBUG
    # _ = search_external(country, prov)
    # print(f"OSM: country:{country} prov:{prov} res:{_}")
    if prov in geoDict[country]:
        logging.debug(f"{prov} in geoDict[{country}]")
        res = (geoDict[country][prov][0], geoDict[country][prov][1]), True
    elif prov.split(' ')[0] in geoDict[country]:
        logging.debug(f"(prov.split(' ')[0] = {prov.split(' ')[0]}) in geoDict[{country}]")
        res = (geoDict[country][prov.split(' ')[0]][0], geoDict[country][prov.split(' ')[0]][1]), True
    else:
        isFind = False
        tmp = None
        for j in geoDict[country]:
            tmp = (geoDict[country][j][0], geoDict[country][j][1])
            if j in prov or prov in j:
                logging.debug(f"{prov} in geoDict[{country}][{j}] tmp:{tmp}")
                isFind = True
                break
        logging.debug(f"{prov} NOT FIND in geoDict[{country}] tmp:{tmp}") if isFind else None
        res = tmp, isFind
    logging.debug(f"country:{country} prov:{prov} res:{res}")
    if res[1]:
        return res[0]
    elif country in spCountryList:
        return search_external(country, prov)
    else:
        return res[0]


def search(country: str, prov: str):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :return: tuple(lat:float, lng:float, msg:str)
    """
    addr = country + ',' + prov
    logging.debug(f"addr:{addr}")
    tmp = None
    if country in geoDict:
        _ = search_cmp(country, prov)
        if _:
            return _[0], _[1], addr
        else:
            return
    else:
        for i in geoDict:
            if country in i or i in country:
                _ = search_cmp(i, prov)
                if _:
                    return _[0], _[1], addr
                else:
                    return
        if combineQuery:
            return search_external(country, prov)
        else:
            for i in geoDict:
                for j in geoDict[i]:
                    if j in prov or prov in j:
                        tmp = geoDict[i][j][0], geoDict[i][j][1], addr
                        return tmp
        logging.warning(f'{addr} not found')
        return tmp


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0','Prov0','extraMsg0'],['Country1','Prov1','extraMsg1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    coordinatesList = []
    for i in geoRawDataList:
        coordinateList = geo.geocodingSingle(i, localQuery=True)
        if coordinateList and len(coordinateList):
            coordinatesList.append(coordinateList)
    return coordinatesList
