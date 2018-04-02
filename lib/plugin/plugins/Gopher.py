import socket
import netaddr

from Config import cnf
from lib.plugin.plugins import BasePlugin


class Plugin(BasePlugin):
  class TelegramMessage(BasePlugin.TelegramMessage):
    def _init(self):
      self._name = "Gopher"

    def _generate(self):
      self.data['txt'] = "gopher://%s/\n" % self._host['ip']
      self.data['txt'] += "Dirs:\n"
      for dir in [f for f in self._host['data']['files'] if f['type'] == '1']:
        self.data['txt'] += " + %s\n" % dir['path']
      self.data['txt'] += "Other nodes:\n"
      for file in [f for f in self._host['data']['files'] if f['type'] != '1' and f['type'] != 'i']:
        self.data['txt'] += " + %s\n    %s\n" % (file['path'], file['name'])
      self.data['txt'] += "Geo: %s/%s\n" % (self._host['data']['geo']['country'], self._host['data']['geo']['city'])
      self.data['txt'] += "#gopher_" + str(int(netaddr.IPAddress(self._host['ip'])))

  class Pipeline(BasePlugin.Pipeline):
    def _init(self):
      self._name = "Gopher"

    def run(self):
      try:
        self._find()
        self._push()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s)", e, self._host['ip'])
      else:
        self._logger.info("Succeeded for %s" % self._host['ip'])

    def _recv(self, sck):
      total_data = []
      while True:
        data = sck.recv(2048)
        if not data:
          break
        total_data.append(data.decode('utf-8'))
      return ''.join(total_data)

    def _find(self):
      sock = socket.socket()
      sock.settimeout(cnf.stalker.Gopher.timeout)
      sock.connect((self._host['ip'], int(self._host['port'])))
      sock.sendall(b'\n\n')

      response = self._recv(sock)
      sock.close()

      self._logger.debug("Parsing result")
      self._host['data']['files'] = []
      self._host['data']['filter'] = False
      for s in [s for s in response.split("\r\n") if s]:
        node = {}
        fields = s.split("\t")
        self._logger.debug(fields)
        node['type'] = fields[0][0]
        if len(fields) == 4:
          node['name'] = fields[0][1:]
          node['path'] = fields[1]
          node['serv'] = f"{fields[2]}:{fields[3]}"
          self._host['data']['files'].append(node)

      if not self._host['data']['files']:
        raise self.PipelineError("Empty server (not Gopher?)")
