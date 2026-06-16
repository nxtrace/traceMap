# -- coding: utf-8 --

from __init__ import *
import html
localQuery = True


DEFAULT_HTML_URL_PREFIX = "https://assets.nxtrace.org/tracemap/"
TRACE_JSON_SCHEMA = "peeras.trace.v1"


def _trace_id_from_filename(file_name: str) -> str:
    return os.path.splitext(os.path.basename(file_name))[0]


def _json_filename_for(file_name: str) -> str:
    return _trace_id_from_filename(file_name) + '.json'


def _html_url_for(file_name: str) -> str:
    url_prefix = os.environ.get("TRACEMAP_HTML_URL_PREFIX") or DEFAULT_HTML_URL_PREFIX
    if not url_prefix.endswith("/"):
        url_prefix += "/"
    return url_prefix + file_name


def _return_url_for(file_name: str) -> str:
    trace_id = _trace_id_from_filename(file_name)
    template = os.environ.get("TRACEMAP_RETURN_URL_TEMPLATE")
    if not template:
        return _html_url_for(file_name)
    try:
        return template.format(id=trace_id, filename=file_name, json_filename=_json_filename_for(file_name))
    except (KeyError, ValueError, IndexError) as exc:
        logging.warning("Invalid TRACEMAP_RETURN_URL_TEMPLATE=%r: %s", template, exc)
        return _html_url_for(file_name)


def _asn_to_number(asn: str):
    if not asn:
        return None
    text = str(asn).strip()
    if text.upper().startswith('AS'):
        text = text[2:]
    try:
        return int(text)
    except ValueError:
        return None


def _build_trace_json(locationsRawList: list, tableDataList: list, file_name: str) -> dict:
    trace_id = _trace_id_from_filename(file_name)
    hops = []
    for item in locationsRawList:
        ttl = int(item[7]) if str(item[7]).isdigit() else None
        hop = {
            "idx": ttl,
            "ip": item[5] or None,
            "rdns": item[9] or "",
            "asn": _asn_to_number(item[4]),
            "name": item[3] or "",
            "cc": "",
            "city": item[2] or "",
            "lat": item[0],
            "lon": item[1],
            "rtt": float(item[8]) if item[8] != "" else None,
            "loss": 0,
            "isTarget": False,
        }
        hops.append(hop)

    if hops:
        hops[-1]["isTarget"] = True
        first = hops[0]
        last = hops[-1]
    else:
        first = {"lat": 0, "lon": 0, "city": ""}
        last = {"ip": None, "lat": 0, "lon": 0, "city": ""}

    return {
        "schema": TRACE_JSON_SCHEMA,
        "id": trace_id,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "html_url": _html_url_for(file_name),
        "target": {
            "label": last.get("ip") or "",
            "ip": last.get("ip") or "",
            "lat": last.get("lat"),
            "lon": last.get("lon"),
            "cc": "",
            "city": last.get("city") or "",
            "loc": last.get("city") or "",
        },
        "probes": [
            {
                "id": "ntrace-" + trace_id,
                "city": first.get("city") or "NextTrace",
                "cc": "",
                "country": "",
                "network": "NextTrace",
                "asn": 0,
                "lat": first.get("lat"),
                "lon": first.get("lon"),
                "status": "done",
                "hops": hops,
            }
        ],
        "path": [{"lat": item[0], "lon": item[1]} for item in locationsRawList],
        "table": tableDataList,
    }


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

    def safe_make_net(ip_value: str, mask: str) -> str:
        """Return CIDR string when possible; otherwise preserve original value."""
        if not ip_value:
            return ip_value
        if '/' in ip_value:
            return ip_value
        try:
            return str(IPy.IP(ip_value).make_net(mask))
        except ValueError:
            return ip_value

    isIPv4 = (IPy.IP(locationsRawList[0][5]).version() == 4)
    if isIPv4:
        locationsRawList[0][5] = safe_make_net(locationsRawList[0][5], '24')
        locationsRawList[-1][5] = safe_make_net(locationsRawList[-1][5], '24')
    else:
        locationsRawList[0][5] = safe_make_net(locationsRawList[0][5], '48')
        locationsRawList[-1][5] = safe_make_net(locationsRawList[-1][5], '48')

    tableDataList = [[i[7], i[5], i[9], i[8], i[4], i[2]] for i in locationsRawList]
    traceJson = _build_trace_json(locationsRawList, tableDataList, file_name)
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
            textList.append(html.escape(text))
            text = '<br>'.join(textList)
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            content += 'AddPathPoint(path, {}, {})\n'.format(lat, lng)
            content += 'AddPoint(map, "{}", "{}", {}, {})\n'.format(i[2], text, lat, lng)
            textList = []
            break
        if lat == locationsRawList[k + 1][0] and lng == locationsRawList[k + 1][1]:
            textList.append(html.escape(text))
            continue
        else:
            textList.append(html.escape(text))
            text = '<br>'.join(textList)
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            content += 'AddPathPoint(path, {}, {})\n'.format(lat, lng)
            content += 'AddPoint(map, "{}", "{}", {}, {})\n'.format(i[2], text, lat, lng)
            textList = []

    with open('template/template.html', 'r', encoding='utf-8') as f:
        template = f.read()
        new_content = (template.replace("%_REPLACE_CONTENT0_%", ''.join(content))).replace(
            "%_REPLACE_CONTENT1_%", json.dumps(tableDataList, ensure_ascii=False)
        )
        with open(os.path.join(output_path, file_name), 'w', encoding='utf-8') as fp:
            fp.write(new_content)
    with open(os.path.join(output_path, _json_filename_for(file_name)), 'w', encoding='utf-8') as fp:
        json.dump(traceJson, fp, ensure_ascii=False)


def process(rawData: dict, filename=str(int(datetime.datetime.now().timestamp())) + '.html') -> str:
    """
    处理原始数据，获取HTML文件路径
    :param filename: 导出的文件名，默认时间戳
    :param rawData: dict, 原始数据
    :return: str, HTML文件路径
    """
    # print(rawData)
    coordinatesList = []
    for hop_group in rawData.get('Hops', []):
        if not hop_group:
            continue
        for j in hop_group:
            if not j or not isinstance(j, dict):
                continue
            if j.get('Success'):
                geo = j.get('Geo') or {}
                if 'lat' not in geo:
                    return "不受支持的版本，请更新至最新版本NextTrace。"
                if geo.get('lat') == 0 and geo.get('lng') == 0:
                    continue
                if geo.get('prov') == "" and geo.get('country') in ['中国', '美国', '俄罗斯']:
                    continue
                tmpCity = ''
                if geo.get('country'):
                    tmpCity = geo['country']
                if geo.get('prov'):
                    tmpCity = geo['prov']
                if geo.get('city'):
                    tmpCity = geo['city']
                address = j.get('Address') or {}
                coordinatesList.append(
                    [
                        geo.get('lat'),
                        geo.get('lng'),
                        tmpCity,
                        geo.get('owner', ''),
                        geo['asnumber'] if 'asnumber' in geo else '',
                        address['IP'] if 'IP' in address else '',
                        j['whois'] if 'whois' in j else '',
                        f'{j["TTL"]}' if 'TTL' in j else '',
                        f'{(j["RTT"] / 1_000_000):.2f}' if 'RTT' in j else '',  # unit: ms
                        j['Hostname'] if 'Hostname' in j else ''
                    ]
                )
                break
    if (len(coordinatesList) == 0):
        return "没有需要绘制的数据。"
    draw(coordinatesList, './html', filename)
    return _return_url_for(filename)


if __name__ == '__main__':
    json.load(open('test/test.json', 'r'))
    print(process(json.load(open('test/test.json', 'r')), filename='demo1.html'))
