from time import sleep

import itertools
import random
import socket
import struct
import netaddr

import GeoIP

from lib.data import Source

class IPSource(Source):
  """Base source for IPs, appends data.ip and data.geo"""
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
    self._item.update({
      'data': {
        'ip': None,
        'geo': {
          'country': None,
          'city': None
        }
      }
    })
    self.geo_ip = GeoIP.open(self.lcnf.get("geoip_dat", "/usr/share/GeoIP/GeoIPCity.dat"),
                             GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)

  def _geoip(self, item):
    geodata = self.geo_ip.record_by_name(item['data']['ip'])
    if geodata:
      if 'country_code3' in geodata and geodata['country_code3']:
        item['data']['geo']['country'] = geodata['country_code3']
      if 'city' in geodata and geodata['city']:
        item['data']['geo']['city'] = geodata['city']

  def _prepare(self, item):
    self._geoip(item)

class IPRange(IPSource):
  """Provides IPs from ranges specified in file"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
    self._iprange = []
    self.load_ip_range()

  def load_ip_range(self):
    """Loads IP ranges from specified path"""
    ip_range = []
    with open(self.lcnf.get('path'), "r") as text:
      for line in text:
        try:
          diap = line.split('-')
          if len(diap) == 2:
            ip_range.append(netaddr.IPRange(diap[0], diap[1]))
          else:
            ip_range.append(netaddr.IPNetwork(diap[0]))
        except Exception as e:
          raise Exception("Error while adding range %s: %s" % (line, e))
    self._iprange = ip_range

  def __run(self):
    npos = 0 # network cursor
    apos = 0 # address cursor
    while self._running:
      try:
        for _ in itertools.repeat(None, self.lcnf.get('oneshot', 200)):
          item = self._create()
          if self.lcnf.get('ordered', True):
            # put currently selected element
            item['data']['ip'] = str(self._iprange[npos][apos])
            # rotate next element through networks and addresses
            if apos + 1 < self._iprange[npos].size:
              apos += 1
            else:
              apos = 0
              if npos + 1 < len(self._iprange):
                npos += 1
              else:
                if self.lcnf.get('repeat', True):
                  npos = 0
                else:
                  self.stop()
          else:
            item['data']['ip'] = str(random.choice(random.choice(self._iprange)))
          self._prepare(item)
          self._data.put(item)
        sleep(self.lcnf.get('delay', 0.5))
      except Exception as err:
        self._logger.warn(err)


class RandomIP(IPSource):
  """Generates completely pseudorandom IPs"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    while self._running:
      try:
        items = []
        for _ in itertools.repeat(None, self.lcnf.get("oneshot", 200)):
          item = self._create()
          randomip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
          item['data']['ip'] = str(randomip)
          self._prepare(item)
          items.append(item)
        self._data.put(items)
        sleep(self.lcnf.get("delay", 0.2))
      except Exception as err:
        self._logger.warn(err)
