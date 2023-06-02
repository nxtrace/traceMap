import uuid

import flask
from flask import request

from __init__ import *
from main import process


def html(filename):
    return flask.send_from_directory('html', filename)


def favicon():
    return flask.send_file('favicon.ico', mimetype='image/vnd.microsoft.icon')


def api():
    data = json.loads(request.data.decode("utf-8"))

    uName = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.get_data().decode()))
    json_str = json.dumps(data, ensure_ascii=False)
    data = json.loads(json_str)
    with open('log/' + uName + '.json', 'w', encoding='utf-8') as f:
        f.write(json_str)
        logging.info("Saved log to log/" + uName + ".json")
    try:
        filename = process(data, filename=uName + '.html')
        logging.info("Saved html to " + filename)
    except Exception as e:
        logging.error("uuid:", uName)
        logging.error(e)
        print(traceback.format_exc())
        return "", 500
    return filename, 200


class WebServer:
    def __init__(self):
        self.app = flask.Flask(__name__)
        if 'GUNICORN_CMD_ARGS' in os.environ:
            gunicorn_logger = logging.getLogger('gunicorn.error')
            self.app.logger.handlers = gunicorn_logger.handlers
            self.app.logger.setLevel(gunicorn_logger.level)
        else:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        self.app.config['JSON_AS_ASCII'] = False

        self.urlPrefix = "http://localhost:8888/html/"

        self.app.route('/api', methods=['post'])(api)
        self.app.route('/html/<filename>', methods=['get'])(html)
        self.app.route('/favicon.ico', methods=['get'])(favicon)

    def run(self, host="0.0.0.0", port=18888, debug=True):
        self.app.run(host=host, port=port, debug=debug)


server = WebServer()
APP = server.app
if __name__ == '__main__':
    server.run()
