import datetime
import json
import logging
import os
import re
import random
import IPy
import traceback
import uuid
from multiprocessing.dummy import Pool as ThreadPool
from typing import Union
from urllib import parse
from packaging import version

import requests
from requests.adapters import HTTPAdapter

import html

accept_version = "1.2.7"
latest_version = "1.4.2"

if __name__ == '__main__':
    _ = str(json) + str(logging) + str(ThreadPool()) + str(datetime) + str(os) + str(html) + str(re) + str(Union) + \
        str(parse) + str(requests) + str(HTTPAdapter) + str(random) + str(IPy) + str(traceback) + str(uuid) + str(version)
