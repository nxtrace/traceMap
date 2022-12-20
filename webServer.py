import uuid

import flask
from flask import request

from __init__ import *
from main import process

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
app = flask.Flask(__name__)

app.config['JSON_AS_ASCII'] = False



@app.route('/api', methods=['post'])
def api():
    data = request.get_json()
    uName = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.get_data().decode()))
    json.dump(obj=data,
              fp=open('log/' + uName + '.json', 'w'),
              ensure_ascii=False
              )
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
