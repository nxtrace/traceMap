import datetime
import json
import logging

import flask
from flask import request

from main import process

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
app = flask.Flask(__name__)

app.config['JSON_AS_ASCII'] = False

urlPrefix = "http://localhost:8888/html/"


@app.route('/api', methods=['post'])
def api():
    data = request.get_json()
    json.dump(obj=data, fp=open('log/' + str(int(datetime.datetime.now().timestamp())) + '.json', 'w'))
    try:
        filename = process(data)
    except:
        return "", 500
    return request.host_url + 'html/' + filename, 200


@app.route('/html/<filename>', methods=['get'])
def html(filename):
    return flask.send_from_directory('html', filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=False)
