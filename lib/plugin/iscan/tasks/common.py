# pylint: disable=E1101

import subprocess
import json
from jsoncomment import JsonComment

from lib.exec import Task

class MasScanTask(Task):
  """Provides data.ports for each of items scanned with masscan"""
  def scan(self, ip_list, port_list, bin_path, opts="-sS -Pn -n --wait 0 --max-rate 5000"):
    """Executes masscan on given IPs/ports"""
    bin_path = bin_path
    opts_list = opts.split(' ')
    port_list = ','.join([str(p) for p in port_list])
    ip_list = ','.join([str(ip) for ip in ip_list])
    process_list = [bin_path]
    process_list.extend(opts_list)
    process_list.extend(['-oJ', '-', '-p'])
    process_list.append(port_list)
    process_list.append(ip_list)

    proc = subprocess.run(process_list, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    out = proc.stdout.decode('utf-8') if proc.stdout else '[]'
    parser = JsonComment(json)
    result = parser.loads(out)
    return result

  def _run(self, items):
    ip_list = [i['data']['ip'] for i in items]
    port_list = self.lcnf.get("ports")

    self._logger.debug("Starting scan, port_list=%s", port_list)

    hosts = self.scan(ip_list=ip_list,
                      port_list=port_list,
                      bin_path=self.lcnf.get('bin_path', "/usr/bin/masscan"))

    self._logger.debug(hosts)
    hosts = {h['ip']: h for h in hosts}
    for item in items:
      if hosts.get(item['data']['ip']):
        ports = [p['port'] for p in hosts[item['data']['ip']]['ports']]
        if 'ports' in item['data']:
          item['data']['ports'].extend(ports)
        else:
          item['data']['ports'] = ports
        item['steps'][self._id] = True
        self._logger.debug("Found %s with open ports %s", item['data']['ip'], ports)
      else:
        item['steps'][self._id] = False
    return items
