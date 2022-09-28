import requests

from common.Basic_starify import header_starify, query_starify, body_starify
from caseStarify.tools import create_sign
from time import time
from urllib.parse import urlencode, urlunparse, unquote

from common.Config import config

headers = header_starify
query = query_starify
query['_timestamp'] = str(int(time()))
body = body_starify
sign = create_sign(query)
query['_sign'] = sign
url = config.starify_mobile_login_url + "?" + unquote(urlencode(query))
session = requests.session()
res = session.post(url, data=body, headers=headers, timeout=30)
print(res.json())
res.raise_for_status()