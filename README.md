<div align="center">

<img src="https://github.com/OwO-Network/nexttrace-enhanced/raw/main/asset/logo.png" height="200px" alt="NextTrace Logo"/>

</div>

# traceMap

NextTrace Enhanced traceMap Plugin

同时支持本地查询和使用OSMAPI查询

## How To Use

调用`main.py`中的`process`函数即可。

```python3
def process(rawData) -> str:
    """
    处理原始数据，获取HTML文件路径
    :param rawData: dict, 原始数据
    :return: str, HTML文件路径
    """
```

默认使用本地查询，如果需要使用OSMAPI查询，请在`main.py`中设置`localQuery`为`False`。
