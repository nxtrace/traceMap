import geo
from __init__ import *

iso3166MapDict = json.load(open('assets/iso3166-1.json', 'r', encoding='utf-8'))
session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=2))


def search(country: str, prov: str):
    """
    根据国家和省份查询经纬度 by English
    :param country: str, 国家
    :param prov: str, 省份
    :return: tuple(lat:float, lng:float, msg:str)
    """
    addr = country + ',' + prov
    logging.debug(f'addr:{addr}')
    if (country == 'China') or (country == '中国'):
        if prov == '':
            return None
        if prov == 'Taiwan':
            return 23.9739374, 120.9820179, "China, Taiwan Province"
    try:
        r = session.get(f'https://nominatim.openstreetmap.org/search/{addr}?limit=1&format=json', timeout=3)
        r = r.json()[0]
    except IndexError:
        logging.info('{} {} not found by osmApi'.format(country, prov))
        return None
    return float(r['lat']), float(r['lon']), addr


def geocoding(geoRawDataList: list) -> list:
    """
    多个地址转经纬度
    :param geoRawDataList: list, 地址集:[['Country0','Prov0','extraMsg0'],['Country1','Prov1','extraMsg1'],...]
    :return: list, 经纬度:[[lat0:float, lng0:float, msg0:str],[lat1:float, lng1:float, msg1:str],...]
    """
    coordinatesList = []
    pool = ThreadPool(4)
    sum_result = pool.map(geocodingSingle, geoRawDataList)
    pool.close()
    pool.join()
    logging.info(f"geocoding_osm_sum_result:{sum_result}")
    for i in sum_result:
        if i and len(i) == 3:
            coordinatesList.append([i[0], i[1], i[2]])
    return coordinatesList


def geocodingSingle(geoRawDataList: list):
    return geo.geocodingSingle(geoRawDataList, localQuery=False)
