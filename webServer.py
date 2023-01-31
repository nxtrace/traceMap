import uuid

import flask
from flask import request

from __init__ import *
from main import process

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
app = flask.Flask(__name__)

app.config['JSON_AS_ASCII'] = False

urlPrefix = "http://localhost:8888/html/"


@app.route('/api', methods=['post'])
def api():
    data = json.loads(request.data.decode("utf-8"))

    uName = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.get_data().decode()))
    json_str = json.dumps(data, ensure_ascii=False)
    data = json.loads(json_str)
    with open('log/' + uName + '.json', 'w', encoding='utf-8') as f:
        f.write(json_str)
    try:
        filename = process(data, filename=uName + '.html')
    except:
        return "", 500
    return filename, 200


@app.route('/html/<filename>', methods=['get'])
def html(filename):
    return flask.send_from_directory('html', filename)


@app.route('/favicon.ico', methods=['get'])
def favicon():
    return flask.send_file('favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=18888, debug=False)