# pylint: disable=E1101

import subprocess
import json
from jsoncomment import JsonComment
from lib import Logger
import GeoIP
from Config import cnf

logger = Logger("common")


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

def scan(items, taskid):
  gi = GeoIP.open(cnf.geoip_dat, GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)
  logger.debug("Starting scan")
  ms = MasScan()
  hosts = ms.scan(ip_list=[i['data']['ip'] for i in items], port_list=cnf.Tasks[taskid].ports)
  for h in hosts:
    for port in h['ports']:
      host = {
        'ip': h['ip'],
        'port': port['port'],
        'data': {
          'geo': {
            'country': None,
            'city': None
          }
        }
      }
    geodata = gi.record_by_name(host['ip'])
    if geodata:
      if 'country_code3' in geodata and geodata['country_code3']:
        host['data']['geo']['country'] = geodata['country_code3']
      if 'city' in geodata and geodata['city']:
        host['data']['geo']['city'] = geodata['city']
    logger.debug("Found %s:%s", host['ip'], host['port'])