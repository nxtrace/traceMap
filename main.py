# -- coding: utf-8 --

from __init__ import *

localQuery = True


def draw(locationsRawList: list, output_path: str, file_name: str) -> None:
    """
    绘制traceMap
    :param locationsRawList: list, 需要绘制轨迹的经纬度信息，格式为[[lat0, lon0, msg0], [lat1, lon1, msg1], ...] (纬度,经度,城市名,信息)
    :param output_path: str, 轨迹图保存路径
    :param file_name: str, 轨迹图保存文件名
    """
    # 计算中心
    content = []
    location_center_lat = (locationsRawList[0][0] + locationsRawList[-1][0]) / 2
    if abs(locationsRawList[0][1] - locationsRawList[-1][1]) > 180:
        location_center_lng = (locationsRawList[0][1] + locationsRawList[-1][1] + 360) / 2
    else:
        location_center_lng = (locationsRawList[0][1] + locationsRawList[-1][1]) / 2
    content += 'map.centerAndZoom(new BMapGL.Point({}, {}), 4)\n'.format(location_center_lng, location_center_lat)

    isIPv4 = (IPy.IP(locationsRawList[0][5]).version() == 4)
    if isIPv4:
        locationsRawList[0][5] = str(IPy.IP(locationsRawList[0][5]).make_net('24'))
        locationsRawList[-1][5] = str(IPy.IP(locationsRawList[-1][5]).make_net('24'))
    else:
        locationsRawList[0][5] = str(IPy.IP(locationsRawList[0][5]).make_net('48'))
        locationsRawList[-1][5] = str(IPy.IP(locationsRawList[-1][5]).make_net('48'))

    tableDataList = [[i[7], i[5], i[7], i[4], i[2]] for i in locationsRawList]
    textList = []

    for k, i in enumerate(locationsRawList):
        lat = i[0]
        lng = i[1]
        text = i[5] + ' ' \
               + (('AS' + i[4]) if i[4] != '' else '') + ' ' \
               + 'TTL:' + i[7] + ' ' \
               + i[3] + ' ' \
               + 'RTT:' + i[8] + 'ms'  # + i[6]
        if k == len(locationsRawList) - 1:
            textList.append(text)
            text = '<br>'.join(textList)
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            content += 'AddPathPoint(path, {}, {})\n'.format(lat, lng)
            content += 'AddPoint(map, "{}", "{}", {}, {})\n'.format(i[2], text, lat, lng)
            textList = []
            break
        if lat == locationsRawList[k + 1][0] and lng == locationsRawList[k + 1][1]:
            textList.append(text)
            continue
        else:
            textList.append(text)
            text = '<br>'.join(textList)
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            content += 'AddPathPoint(path, {}, {})\n'.format(lat, lng)
            content += 'AddPoint(map, "{}", "{}", {}, {})\n'.format(i[2], text, lat, lng)
            textList = []

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()
        new_content = (template.replace("%_REPLACE_CONTENT0_%", ''.join(content))).replace(
            "%_REPLACE_CONTENT1_%",json.dumps(tableDataList,ensure_ascii=False)
        )
        with open(os.path.join(output_path, file_name), 'w', encoding='utf-8') as fp:
            fp.write(new_content)


def process(rawData: dict, filename=str(int(datetime.datetime.now().timestamp())) + '.html') -> str:
    """
    处理原始数据，获取HTML文件路径
    :param filename: 导出的文件名，默认时间戳
    :param rawData: dict, 原始数据
    :return: str, HTML文件路径
    """
    # print(rawData)
    urlPrefix = "https://api.leo.moe/tracemap/"
    coordinatesList = []
    for k in rawData['Hops']:
        for j in k:
            if j['Success']:
                if 'lat' not in j['Geo']:
                    return "不受支持的版本，请更新至最新版本NextTrace。"
                if j['Geo']['lat'] == 0 and j['Geo']['lng'] == 0:
                    continue
                if j['Geo']['prov'] == "" and j['Geo']['country'] in ['中国', '美国', '俄罗斯']:
                    continue
                tmpCity = ''
                if j['Geo']['country'] != '':
                    tmpCity = j['Geo']['country']
                if j['Geo']['prov'] != '':
                    tmpCity = j['Geo']['prov']
                if j['Geo']['city'] != '':
                    tmpCity = j['Geo']['city']
                coordinatesList.append(
                    [
                        j['Geo']['lat'], j['Geo']['lng'],
                        tmpCity,
                        j['Geo']['owner'],
                        j['Geo']['asnumber'] if 'asnumber' in j['Geo'] else '',
                        j['Address']['IP'] if 'IP' in j['Address'] else '',
                        j['whois'] if 'whois' in j else '',
                        f'{j["TTL"]}' if 'TTL' in j else '',
                        f'{(j["RTT"] / 1_000_000):.2f}' if 'RTT' in j else ''  # unit: ms
                    ]
                )
                break
    draw(coordinatesList, './html', filename)
    return urlPrefix + filename


if __name__ == '__main__':
    json.load(open('test/test.json', 'r'))
    print(process(json.load(open('test/test.json', 'r')), filename='demo1.html'))
