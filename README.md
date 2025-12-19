<div align="center">

<img src="https://github.com/OwO-Network/nexttrace-enhanced/raw/main/asset/logo.png" height="200px" alt="NextTrace Logo"/>

</div>

# traceMap

NextTrace Enhanced traceMap Plugin

同时支持本地查询和使用OSMAPI查询

## How To Use

+ 运行`traceMap`服务器

  默认端口为`8888`
  
  POST接口默认路径为`/api`,GET接口默认路径为`/html/<filename>`

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
