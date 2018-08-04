# pylint: disable=E1101

import ftplib
import netaddr

from lib import Logger
from Config import cnf

from lib.exeq import Task

class FTPConnectTask(Task):
  def __init__(self, id, root):
    super().__init__(id, root)

  def _process(self, item):
    data = {}
    result = False

    self.ftp = ftplib.FTP(host=item['data']['ip'], timeout=self.lcnf.get('timeout', 30))
    try:
      self._logger.debug('Trying anonymous login')
      self.ftp.login()
    except ftplib.error_perm:
      pass
    else:
      self._logger.debug('Succeeded with anonymous')
      data['username'] = 'anonymous'
      data['password'] = ''
      result = True

      self._logger.debug(data)
      item['data'].update(data)
      item['steps'][self._id] = result
      return

    if self.lcnf.get('bruteforce', False):
      usernames = []
      passwords = []

      with open(self.lcnf.get('logins'), 'r') as lfh:
        for username in lfh:
          usernames.append(username.rstrip())
      with open(self.lcnf.get('passwords'), 'r') as pfh:
        for password in pfh:
          passwords.append(password.rstrip())
      for username in usernames:
        for password in passwords:
          try:
            self.ftp.voidcmd('NOOP')
          except IOError:
            self.ftp = ftplib.FTP(host=item['data']['ip'], timeout=self.lcnf.get('timeout', 30))
          self._logger.debug('Trying %s' % (username + ':' + password))
          try:
            self.ftp.login(username, password)
          except ftplib.error_perm:
            continue
          except:
            raise
          else:
            self._logger.debug('Succeeded with %s' %(username + ':' + password))
            data['username'] = username
            data['password'] = password
            result = True


            self._logger.debug(data)
            item['data'].update(data)
            item['steps'][self._id] = result
            return
    self._logger.debug(data)
    item['data'].update(data)
    item['steps'][self._id] = result

  def _run(self, items):
    for item in items:
      self._process(item)
    return items

class FTPListFilesTask(Task):
  def __init__(self, id, root):
    super().__init__(id, root)

  def _process(self, item):
    item['steps'][self._id] = False
    self.ftp = ftplib.FTP(host=item['data']['ip'], 
                          user=item['data']['username'],
                          passwd=item['data']['password'])
    filelist = self.ftp.nlst()
    try:
      self.ftp.quit()
    except:
      # that's weird, but we don't care
      pass

    try:
      if len(filelist) == 0 or filelist[0] == "total 0":
        item['data']['filter'] = "Empty server"
    except IndexError:
      pass

    item['data']['files'] = []
    for fileName in filelist:
      item['data']['files'].append(fileName)
      item['steps'][self._id] = True

  def _filter(self, item):
    item['data']['filter'] = False
    if len(item['data']['files']) == 0:
      item['data']['filter'] = "Empty"
    elif len(item['data']['files']) < 6:
      match = 0
      for f in 'incoming', '..', '.ftpquota', '.', 'pub':
        if f in item['data']['files']:
          match += 1
        if match == len(item['data']['files']):
          item['data']['filter'] = "EmptyWithSystemDirs"
    if item['data']['filter'] == False:
      item['steps'][self._id] = True

  def _run(self, items):
    for item in items:
      self._process(item)
      if self.lcnf.get('filter', False):
        self._filter(item)
    return items
