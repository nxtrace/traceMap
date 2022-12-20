import folium

from __init__ import *
from geo import geoInterface

localQuery = True


def draw(locationsRawList: list, output_path: str, file_name: str) -> None:
    """
    绘制traceMap
    :param locationsRawList: list, 需要绘制轨迹的经纬度信息，格式为[[lat0, lon0, msg0], [lat1, lon1, msg1], ...] (纬度,经度,信息)
    :param output_path: str, 轨迹图保存路径
    :param file_name: str, 轨迹图保存文件名
    """
    locationsList = [[i[0], i[1]] for i in locationsRawList]
    msgList = [i[2] for i in locationsRawList]
    tiles = "https://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}"
    if locationsList:
        location_center_lat = (locationsList[0][0] + locationsList[-1][0]) / 2
        location_center_lng = (locationsList[0][1] + locationsList[-1][1]) / 2
        m = folium.Map([location_center_lat, location_center_lng], attr='default', zoom_start=4, tiles=tiles)  # 中心区域的确定

        folium.PolyLine(  # polyline方法为将坐标用实线形式连接起来
            locationsList,  # 将坐标点连接起来
            weight=4,  # 线的大小为4
            color='red',  # 线的颜色为红色
            opacity=0.8,  # 线的透明度
        ).add_to(m)  # 将这条线添加到刚才的区域m内
        # 起始点，结束点
        folium.Marker(locationsList[0], popup=f'<b>Starting Point, {msgList[0]}</b>',
                      icon=folium.Icon(color='green', prefix='fa', icon='info-sign')).add_to(m)
        folium.Marker(locationsList[-1], popup=f'<b>End Point, {msgList[-1]}</b>',
                      icon=folium.Icon(color='red', prefix='fa', icon='info-sign')).add_to(m)

        # 其他点
        for i in range(1, len(locationsList) - 1):
            if not (locationsList[i] == locationsList[0] or locationsList[i] == locationsList[-1]):
                folium.Marker(locationsList[i], popup=f'<b>{msgList[i]}</b>').add_to(m)
        m.save(os.path.join(output_path, file_name))  # 将结果以HTML形式保存到指定路径
    else:
        logging.info('locationsList is []')


def process(rawData: Union[dict, str], filename=str(int(datetime.datetime.now().timestamp())) + '.html') -> str:
    """
    处理原始数据，获取HTML文件路径
    :param filename: 导出的文件名，默认时间戳
    :param rawData: str or dict, 原始数据
    :return: str, HTML文件路径
    """
    urlPrefix = "http://api.leo.moe/tracemap/"
    coordinatesList = []
    for k in rawData['Hops']:
        for j in k:
            if j['Success']:
                if not 'lat' in j['Geo']:
                    return "不受支持的版本，请更新至 NextTrace，因时间精力等问题，我们已经暂时放弃对 Enhanced 版本的继续支持"
                if j['Geo']['lat'] == 0 and j['Geo']['lng'] == 0:
                    continue
                if j['Geo']['prov'] == "" and j['Geo']['country'] in ['中国', '美国', '俄罗斯']:
                    continue
                coordinatesList.append([j['Geo']['lat'], j['Geo']['lng'], j['Geo']['country'] + ' ' + j['Geo']['prov'] + ' ' + j['Geo']['city'] + ' ' + j['Geo']['owner']])
                break
    # print(coordinatesList)
    draw(coordinatesList, './html', filename)
    return urlPrefix + filename
