<div align="center">

<img src="https://github.com/OwO-Network/nexttrace-enhanced/raw/main/asset/logo.png" height="200px" alt="NextTrace Logo"/>

</div>

# traceMap

NextTrace Enhanced traceMap Plugin

同时支持本地查询和使用OSMAPI查询

## How To Use

+ 运行`traceMap`服务器

  默认端口为`18888`
  
  POST接口默认路径为`/api`,GET接口默认路径为`/html/<filename>`

  服务端会为每次 trace 同时生成同名 HTML 和 JSON。例如 `abc.html` 会生成 `abc.json`。
  JSON 可通过 `/json/<id>`、`/json/<id>.json`、`/html/<id>.json` 或 `/tracemap/<id>.json` 读取，
  其中 JSON 响应默认允许 `https://peer.as`、`https://www.peer.as`、`https://cn.peer.as` 跨域读取。
  本地开发 Origin 需要通过 `TRACEMAP_JSON_CORS_ORIGINS` 显式加入。

  可选环境变量：

  ```bash
  # 返回给 NextTrace 客户端的 URL 模板。可用占位符: {id}, {filename}, {json_filename}
  export TRACEMAP_RETURN_URL_TEMPLATE='https://peer.as/trace?nt={id}'

  # HTML 的公开地址前缀，写入 JSON 的 html_url 字段
  export TRACEMAP_HTML_URL_PREFIX='https://assets.nxtrace.org/tracemap/'

  # 允许读取 JSON 的 Origin，逗号分隔
  export TRACEMAP_JSON_CORS_ORIGINS='https://peer.as,https://www.peer.as,https://cn.peer.as'
  ```

  部署前请按实际路径修改 `traceMap.service` 中的 `User`、`WorkingDirectory` 和 venv 路径。

  ```bash
  mkdir -p /var/www
  cd /var/www
  git clone https://github.com/tsosunchia/traceMap.git
  cd traceMap
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  cp traceMap.service /etc/systemd/system/traceMap.service
  systemctl daemon-reload
  systemctl enable --now traceMap.service
  ```
  
+ 调试模式：调用`main.py`中的`process`函数即可。
    
  ```python3
  def process(rawData) -> str:
    """
    处理原始数据，获取HTML文件路径
    :param rawData: dict, 原始数据
    :return: str, HTML文件路径
    """
  ```
    
  默认使用本地查询，如果需要使用OSMAPI查询，请在`main.py`中设置`localQuery`为`False`。
