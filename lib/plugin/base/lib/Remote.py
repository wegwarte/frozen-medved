from lib.data import Feed, Source
from lib.net import Remote
from time import sleep

class RemoteFeed(Feed):
  """Puts processed data to remote medved"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    while self._running:
      try:
        remote = Remote(self.lcnf.get('ip'), self.lcnf.get('port'))
        remote.connect()
        items = self.get(5)
        if items:
          self._logger.info("Sending %s items" % len(items))
          remote.run('data.put', {'items': items})

        sleep(self.lcnf.get('delay', 10))
      except Exception as e:
        self._logger.warn(e)

class RemoteSource(Source):
  """Takes data from remote medved"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    remote = Remote(self.lcnf.get('ip'), self.lcnf.get('port'))
    remote.connect()
    while self._running:
      self._logger.debug("Requesting from %s", self.lcnf.get('ip'))
      rep = remote.run('data.get', {'count': self.lcnf.get('oneshot', 100)})
      if rep.get('status'):
        targets = rep.get("data")
      else:
        targets = []
      self._logger.debug("Got %s items", len(targets))      
      for t in targets:
        self._data.put(t)
      sleep(self.lcnf.get('delay', 10))