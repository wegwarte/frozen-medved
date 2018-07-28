from lib.data import Source, Feed
from time import sleep
from lib import Service, Loader

class DataManager(Service):
  """Actually, we may load feeds, sources and datapools right in core. Not sure that datamanager is required just to pull sources"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
    self._logger.add_field('service', 'DataManager')

    self.sources = {}
    for s in self.lcnf.get("sources"):
      self.attach_source(s)
    self.feeds = {}
    for f in self.lcnf.get("feeds"):
      self.attach_feed(f)

  def _pre_start(self):
    self._logger.debug('starting sources')
    for _,s  in self.sources.items():
      s.start()
    self._logger.debug('starting feeds')
    for _,f in self.feeds.items():
      f.start()

  def _pre_stop(self):
    self._logger.debug('stopping sources')
    for _,s in self.sources.items():
      s.stop()
    self._logger.debug('stopping feeds')
    for _,f in self.feeds.items():
      f.stop()
  
  def attach_source(self, id):
    ds = Loader.by_id('sources', id)
    self.sources[id] = ds

  def attach_feed(self, id):
    df = Loader.by_id('feeds', id)
    self.feeds[id] = df
  
  def get_source(self, name) -> Source:
    return self.sources.get(name)
  
  def get_feed(self, name) -> Feed:
    return self.feeds.get(name)

  def __run(self):
    oneshot = self.lcnf.get("oneshot", 500)
    while self._running:
      if self._data.count() < oneshot:
        while self._running and (self._data.count() + oneshot < self._data.size()):
          self._logger.debug("fill %s OF %s", self._data.count(), self._data.size())
          for _,source in self.sources.items():
            items = source.next(count=oneshot)
            if items:
              self._data.put(items)
          sleep(1)
      else:
        self._logger.debug('Pool size is ok: %s', self._data.count())
      sleep(1)
