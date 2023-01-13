from __init__ import *

spToEngDict = json.load(open('assets/assets.json', 'r', encoding='utf-8'))
GOOGLE_TRANSLATE_URL = 'https://translate.google.com/m?q=%s&tl=%s&sl=%s'
session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=2))


def translate(text: str, to_language, text_language) -> str:
    """
    Google翻译
    exmaple:
        type -> "en" "zh-CN" "auto"
    """
    if text in spToEngDict:
        return spToEngDict[text]
    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
    response = session.get(url, timeout=3)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if len(result) == 0:
        return ""
    return html.unescape(result[0])


def singleTranslate(text: str) -> str:
    return translate(text, "en", "auto")


def dictTranslate(geoDataList: list) -> list:
    dataListCnt = len(geoDataList)
    forTranslateQueue = []
    for i in range(dataListCnt):
        forTranslateQueue.append(geoDataList[i][0])
        forTranslateQueue.append(geoDataList[i][1])
    pool = ThreadPool(4)
    sum_result = pool.map(singleTranslate, forTranslateQueue)
    pool.close()
    pool.join()
    logging.info(f"translate_sum_result:{sum_result}")
    for i in range(dataListCnt):
        geoDataList[i][0] = sum_result[i * 2]
        geoDataList[i][1] = sum_result[i * 2 + 1]
    return geoDataList


if __name__ == '__main__':
    # print(translate("你吃饭了么?", "en", "zh-CN"))  # 汉语转英语
    # print(translate("你吃饭了么？", "ja", "zh-CN"))  # 汉语转日语
    print(translate("中国，天津市", "en", "zh-CN"))
    print(translate("中国，天津市", "en", "zh-CN"))
    print(translate("China, Tianjin", "en", "auto"))
    print(translate("香港", "en", "auto"))
