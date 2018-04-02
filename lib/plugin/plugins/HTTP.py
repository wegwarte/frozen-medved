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

from Config import cnf
from lib.plugin.plugins import BasePlugin


class Plugin(BasePlugin):
  class TelegramMessage(BasePlugin.TelegramMessage):
    def _init(self):
      self._name = "HTTP"

    def _generate(self):
      self.data['txt'] = "#code%s" % self._host['data']['response']['code']
      server = self._host['data']['response']['headers'].get('Server', None)
      if server:
        self.data['txt'] += " Server: #%s\n" % server

      else:
        self.data['txt'] += "\n"

      if self._host['data']['title']:
        self.data['txt'] += "Title: %s\n" % self._host['data']['title']

      self.data['txt'] += "Geo: %s/%s\n" % (self._host['data']['geo']['country'], self._host['data']['geo']['city'])
      self.data['txt'] += "http://%s:%s/\n" % (self._host['ip'], self._host['port'])
      self.data['txt'] += "#http_" + str(int(netaddr.IPAddress(self._host['ip'])))

      if self._host["data"]["screenshot"]:
        self.data['img'] = BytesIO(zlib.decompress(self._host["data"]["screenshot"]))

  class Pipeline(BasePlugin.Pipeline):
    def _init(self):
      self._name = "HTTP"
    
    def run(self):
      try:
        self._find()
        self._filter()
        self._capture_screenshot()
        self._push()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s:%s)", e, self._host['ip'], self._host['port'])
      else:
        self._logger.info("Succeeded for %s:%s", self._host['ip'], self._host['port'])

    def _find(self):
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

    def _filter(self):
      self._host['data']['filter'] = False
      response = self._host['data']['response']

      with open(cnf.stalker.HTTP.filters, encoding='utf-8') as ffh:
        filters = json.load(ffh)

      for fid, filter in filters.items():
        title_filter = filter["content"]["title"] if "title" in filter["content"] else []
        body_filter = filter["content"]["body"] if "body" in filter["content"] else []
        server_filter = filter["content"]["server"] if "server" in filter["content"] else ""

        match = 0
        for keyword in title_filter:
          if keyword in self._host['data']['title']:
            match += 1
        if match == len(title_filter):
          match = 0
          for keyword in body_filter:
            if keyword in response['text']:
              match += 1
          if match == len(body_filter):
            match = True
            if server_filter:
              if self._host['data']['server'] == server_filter:
                match = True
              else:
                match = False
          else:
            match = False
        else:
          match = False

        if match:
          self._host['data']['filter'] = fid

    def _capture_screenshot(self):
      # сраный selenium, как же я его ненавижу
      # боль 
      #   страдания 
      #       ноль документации

      img_byte_arr = BytesIO()

      url = 'http://%s:%s/' % (self._host["ip"], self._host["port"])
      self._host["data"]["screenshot"] = None

      self._logger.debug("Obtaining driver")
      
      driver = None
      img = None
      try:
        caps = dict(DesiredCapabilities.CHROME)

        caps['args'] = ["--proxy-server", "socks5://%s:9050" % cnf.stalker.proxy]

        driver = webdriver.Remote(command_executor = "http://%s:4444/wd/hub" % cnf.stalker.HTTP.screenshots.selenium,
                                  desired_capabilities=caps)

        driver.set_window_size(cnf.stalker.HTTP.screenshots.width, cnf.stalker.HTTP.screenshots.height)
        driver.set_page_load_timeout(cnf.stalker.HTTP.screenshots.load_timeout)
        driver.set_script_timeout(cnf.stalker.HTTP.screenshots.script_timeout)

        self._logger.debug("Loading %s:%s", self._host['ip'], self._host['port'])

        driver.get(url)
        time.sleep(cnf.stalker.HTTP.screenshots.pause)
        driver.execute_script("window.scrollTo(0, 0);")
        img = driver.get_screenshot_as_png()
      except Exception as e:
        raise e
      finally:
        if driver:
          driver.quit()
      
      self._logger.debug("Finished for %s:%s", self._host['ip'], self._host['port'])

      with Image.open(BytesIO(img)) as img:
        img = img.crop((0, 0, cnf.stalker.HTTP.screenshots.width, cnf.stalker.HTTP.screenshots.height))
        extrema = img.convert("L").getextrema()
        if not extrema == (0, 0):
          img.save(img_byte_arr, format='PNG')

          self._host["data"]["screenshot"] = Binary(zlib.compress(img_byte_arr.getvalue()))
          img_byte_arr.close()
          self._logger.debug("Saved screen of %s:%s (e: %s)" % (self._host["ip"], self._host["port"], extrema))
        else:
          self._logger.debug("Not saving screen of %s:%s, as it is empty", self._host["ip"], self._host["port"])
