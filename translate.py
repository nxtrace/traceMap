import re
from urllib import parse

import requests

import html

GOOGLE_TRANSLATE_URL = 'http://translate.google.cn/m?q=%s&tl=%s&sl=%s'


def translate(session: requests.session, text: str, to_language, text_language) -> str:
    """
    Google翻译
    exmaple:
        type -> "en" "zh-CN" "auto"
    """
    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
    response = session.get(url)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if len(result) == 0:
        return ""
    return html.unescape(result[0])


if __name__ == '__main__':
    s = requests.session()
    # print(translate("你吃饭了么?", "en", "zh-CN"))  # 汉语转英语
    # print(translate("你吃饭了么？", "ja", "zh-CN"))  # 汉语转日语
    print(translate(s, "中国，天津市", "en", "zh-CN"))
    print(translate(s, "中国，天津市", "en", "zh-CN"))
    print(translate(s, "China, Tianjin", "en", "auto"))
    print(translate(s, "香港", "en", "auto"))
    s.close()
