from queue import LifoQueue, Empty, Full

from lib import Loadable, Logger

class Storage(Loadable):
  """Base class for storages"""
  def __init__(self, id, root):
    super().__init__(id, root)

    self._size = self.lcnf.get("size")
    self._logger = Logger("Storage")
    self._logger.add_field('vname', self.__class__.__name__)
  
  def size(self):
    return self._size
  
  def count(self):
    return 0

  def _get(self, block, filter):
    pass
  
  def _get_many(self, count, block, filter):
    items = []
    for _ in range(count):
      items.append(self._get(block, filter))
    return items

  def get(self, count=1, block=True, filter=None):
    self._logger.debug("get %s, %s", count, block)
    items = []
    if count == 1:
      items.append(self._get(block, filter))
    elif count > 1:
      items = self._get_many(count, block, filter)
    return [i for i in items if i is not None]

  def _put(self, item, block):
    pass

  def _put_many(self, items, block):
    for i in items:
      if i is not None:
        self._put(i, block)

  def put(self, items, block=True):
    if items:
      items = [i for i in items if i is not None]
      self._logger.debug("put %s, %s", len(items), block)
      if len(items) == 1:
        self._put(items[0], block)
      elif len(items) > 1:
        self._put_many(items, block)

  def _find(self):
    pass

  def find(self):
    self._logger.debug("find")
    return self._find()


class LiFoStorage(Storage):
  def __init__(self, id, root):
    super().__init__(id, root)
    self._data = LifoQueue()

  def count(self):
    return self._data.qsize()
  
  def _get(self, block=False, filter=None):
    try:
      return self._data.get(block=block)
    except Empty:
      pass
  
  def _put(self, item, block=True):
    try:
      self._data.put(item, block=block)
    except Full:
      pass


