"""
Basic tasks for FTP services
"""

import ftplib

from lib.exec import Task

class FTPConnectTask(Task): # pylint: disable=too-few-public-methods
  """Tries to connect FTP service with various credentials"""
  def _process(self, item):
    ftp = ftplib.FTP(host=item['data']['ip'], timeout=self.lcnf.get('timeout', 30))
    try:
      self._logger.debug('Trying anonymous login')
      ftp.login()
    except ftplib.error_perm as err:
      self._logger.debug('Failed (%s)', err)
    else:
      self._logger.info('Succeeded with anonymous')
      item['data']['username'] = 'anonymous'
      item['data']['password'] = ''
      return True

    if self.lcnf.get('bruteforce', False):
      self._logger.debug('Bruteforce enabled, loading usernames and passwords')
      usernames = [line.rstrip() for line in open(self.lcnf.get('usernames'), 'r')]
      passwords = [line.rstrip() for line in open(self.lcnf.get('passwords'), 'r')]

      for username in usernames:
        for password in passwords:
          self._logger.debug('Checking %s', username + ':' + password)
          try:
            self._logger.debug('Sending NOOP')
            ftp.voidcmd('NOOP')
          except IOError as err:
            self._logger.debug('IOError occured (%s), attempting to open new connection', err)
            ftp = ftplib.FTP(host=item['data']['ip'], timeout=self.lcnf.get('timeout', 30))
          try:
            self._logger.debug('Trying to log in')
            ftp.login(username, password)
          except ftplib.error_perm as err:
            self._logger.debug('Failed (%s)', err)
            continue
          else:
            self._logger.info('Succeeded with %s', username + ':' + password)
            item['data']['username'] = username
            item['data']['password'] = password
            return True
    self._logger.info('Could not connect')
    return False

class FTPListFilesTask(Task): # pylint: disable=too-few-public-methods
  """Executes NLST to list files on FTP"""
  def _process(self, item):
    ftp = ftplib.FTP(host=item['data']['ip'], 
                     user=item['data']['username'],
                     passwd=item['data']['password'])
    filelist = ftp.nlst()
    try:
      ftp.quit()
    except ftplib.Error:
      pass

    item['data']['files'] = []
    for filename in filelist:
      item['data']['files'].append(filename)
    return True

class FTPFilterFilesTask(Task): # pylint: disable=too-few-public-methods
  """Sets data.filter if FTP contains only junk"""
  def _process(self, item):
    junk_list = ['incoming', '..', '.ftpquota', '.', 'pub']
    files = item['data']['files']

    item['data']['filter'] = False

    try:
      if not files or files[0] == "total 0":
        item['data']['filter'] = "Empty"
    except IndexError:
      pass

    if 0 < len(files) <= len(junk_list): # pylint: disable=C1801
      match_count = 0
      for filename in junk_list:
        if filename in files:
          match_count += 1
        if match_count == len(files):
          item['data']['filter'] = "EmptyWithBloatDirs"

    return True
