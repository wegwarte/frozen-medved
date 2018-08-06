"""
Basic tasks for Gopher services
"""

import socket

from lib.exec import Task

class GopherFindTask(Task): # pylint: disable=too-few-public-methods
  """Tries to connect Gopher service"""
  @staticmethod
  def _recv(sck):
    total_data = []
    while True:
      data = sck.recv(2048)
      if not data:
        break
      total_data.append(data.decode('utf-8'))
    return ''.join(total_data)

  def _process(self, item):
    sock = socket.socket()
    sock.settimeout(self.lcnf.get('timeout', 20))
    sock.connect((item['data']['ip'], int(70)))
    sock.sendall(b'\n\n')

    response = self._recv(sock)
    sock.close()

    self._logger.debug("Parsing result")
    item['data']['files'] = []
    item['data']['filter'] = False
    for s in [s for s in response.split("\r\n") if s]:
      node = {}
      fields = s.split("\t")
      self._logger.debug(fields)
      node['type'] = fields[0][0]
      if len(fields) == 4:
        node['name'] = fields[0][1:]
        node['path'] = fields[1]
        node['serv'] = f"{fields[2]}:{fields[3]}"
        item['data']['files'].append(node)

    if not item['data']['files']:
      raise Exception("Empty server (not Gopher?)")
    item['steps'][self._id] = True
