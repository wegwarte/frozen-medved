# pylint: disable=E1101

import subprocess
import json
from jsoncomment import JsonComment
from lib import Logger
import GeoIP
from Config import cnf

from lib.exeq import Task

class MasScan:
  def __init__(self, bin_path='/usr/bin/masscan', opts="-sS -Pn -n --wait 0 --max-rate 5000"):
    self.bin_path = bin_path
    self.opts_list = opts.split(' ')

  def scan(self, ip_list, port_list):
    port_list = ','.join([str(p) for p in port_list])
    ip_list = ','.join([str(ip) for ip in ip_list])
    process_list = [self.bin_path]
    process_list.extend(self.opts_list)
    process_list.extend(['-oJ', '-', '-p'])
    process_list.append(port_list)
    process_list.append(ip_list)

    proc = subprocess.run(process_list, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out = proc.stdout.decode('utf-8') if proc.stdout else '[]'
    parser = JsonComment(json)
    result = parser.loads(out)
    return result

class MasScanTask(Task):
  def __init__(self, id, root):
    super().__init__(id, root)

  def _run(self, items):
    result = []

    gi = GeoIP.open(cnf.get("geoip_dat", "/usr/share/GeoIP/GeoIPCity.dat"), GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)
    ip_list = [i['data']['ip'] for i in items]
    port_list = self.lcnf.get("ports")
    
    self._logger.debug("Starting scan, ip_list=%s, port_list=%s", ip_list, port_list)
    
    ms = MasScan()
    hosts = ms.scan(ip_list=ip_list, port_list=port_list)
    
    self._logger.debug(hosts)
    hosts = {h['ip']: h for h in hosts}
    for item in items:
      data = {}
      result = False
      if hosts.get(item['data']['ip']):
        data = {
          'ports': [p['port'] for p in hosts[item['data']['ip']]['ports']],
          'geo': {
            'country': None,
            'city': None
          }
        }
        result = True
        geodata = gi.record_by_name(item['data']['ip'])
        if geodata:
          if 'country_code3' in geodata and geodata['country_code3']:
            data['geo']['country'] = geodata['country_code3']
          if 'city' in geodata and geodata['city']:
            data['geo']['city'] = geodata['city']
      self._logger.debug(data)
      item['data'].update(data)
      item['steps'][self._id] = result
      if result:
        self._logger.debug("Found %s with open %s", item['data']['ip'], item['data']['ports'])
    return items
