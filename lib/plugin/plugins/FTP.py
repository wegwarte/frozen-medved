import ftplib
import netaddr

from Config import cnf


class Plugin():
  class TelegramMessage():
    def _init(self):
      self._name = "FTP"
    
    def _generate(self):
      self.data['txt'] = "ftp://%s:%s@%s/\n" % \
                        (self._host['data']['username'], self._host['data']['password'], self._host['ip'])
      for filename in self._host['data']['files']:
        self.data['txt'] += " + %s\n" % filename
      self.data['txt'] += "Geo: %s/%s\n" % (self._host['data']['geo']['country'], self._host['data']['geo']['city'])
      self.data['txt'] += "#ftp_" + str(int(netaddr.IPAddress(self._host['ip'])))
