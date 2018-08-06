"""
Provides garbage collector
"""

from time import sleep

from lib import Service

class GarbageCollector(Service):
  """Simple GarbageCollector, removes items by filter periodically"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
    self._logger.add_field('service', 'GC')
    self._logger.add_field('vname', self.__class__.__name__)

  def __run(self):
    while self._running:
      filter = {key: value for key, value in self.lcnf.get("if", {}).items()}
      if filter:
        items = self._data.find(filter=filter)
        self._logger.info("Removing %s items", items.count())
        self._data.remove(items)
      else:
        self._logger.error("Filter is empty!")
      sleep(self.lcnf.get('delay', 600))
