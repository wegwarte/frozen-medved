from lib.data import Source
from lib import Loader

import copy

from time import sleep

import os
import netaddr
import itertools
import random
import socket
import struct

class IPSource(Source):
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
  
    self._item.update ({
      'source': self._id,
      'data': {
        'ip': None
      }
    })


class IPRange(IPSource):
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
    self._iprange = []
    self.load_ip_range()

  def load_ip_range(self):
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
          raise Exception("Error while adding range {}: {}".format(line, e))
    self._iprange = ip_range

  def __run(self):
    npos = 0
    apos = 0
    while self._running:
      try:
        for _ in itertools.repeat(None, self.lcnf.get('oneshot', 100)):
          if self.lcnf.get('ordered', True):
            # put currently selected element
            self._data.put(str(self._iprange[npos][apos]))
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
            self._data.put(str(random.choice(random.choice(self._iprange))))
        sleep(self.lcnf.get('delay', 0.5))
      except Exception as e:
        self._logger.warn(e)


class RandomIP(IPSource):
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
  
  def __run(self):
    while self._running:
      try:
        items = []
        for _ in itertools.repeat(None, self.lcnf.get("oneshot", 200)):
          item = copy.deepcopy(self._item)
          randomip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
          item['data']['ip'] = str(randomip)
          items.append(item)
        self._data.put(items)
        sleep(self.lcnf.get("delay", 0.2))
      except Exception as e:
        self._logger.warn(e)
