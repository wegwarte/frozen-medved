from lib.exec import Task

from io import BytesIO
import json
import time

import bs4
import requests
import urllib3
from PIL import Image
from bson.binary import Binary

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
import zlib
import netaddr


class HTTPFindTask(Task):
  def __init__(self, id, root):
    super().__init__(id, root)

  def _process(self, item):
      urllib3.disable_warnings()
      response = requests.get(url='http://%s:%s/' % (self._host['ip'], self._host['port']),
                              timeout=cnf.stalker.HTTP.timeout,
                              verify=False)

      if response.status_code in [400, 401, 403, 500]:
        raise self.PipelineError("Bad response")

      self._host['data']['response'] = {}
      self._host['data']['response']['code'] = response.status_code
      self._host['data']['response']['text'] = response.text
      self._host['data']['response']['content'] = response.content
      self._host['data']['response']['encoding'] = response.encoding
      self._host['data']['response']['headers'] = response.headers

      encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
      soup = bs4.BeautifulSoup(response.content, "html.parser", from_encoding=encoding)
      if soup.original_encoding != 'utf-8':
        meta = soup.select_one('meta[charset], meta[http-equiv="Content-Type"]')
        if meta:
          if 'charset' in meta.attrs:
            meta['charset'] = 'utf-8'
          else:
            meta['content'] = 'text/html; charset=utf-8'
        self._host['data']['response']['text'] = soup.prettify()  # encodes to UTF-8 by default

      title = soup.select_one('title')
      if title:
        if title.string:
          title = title.string
        else:
          title = ""
      else:
        title = ""

      self._host['data']['title'] = title
