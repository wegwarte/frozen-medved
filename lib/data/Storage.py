import inspect

from lib import Loadable, Logger

class Storage(Loadable):
  """Base class for storages"""
  def __init__(self, id, root):
    super().__init__(id, root)

    self._size = self.lcnf.get("size", 0)
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
    """Returns items, removing them from storage"""
    self._logger.debug("get|%s|%s|%s",
                       count, block, inspect.stack()[1][0].f_locals["self"].__class__.__name__)
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
    """Puts provided items"""
    self._logger.debug("put|%s|%s|%s",
                       len(items), block, inspect.stack()[1][0].f_locals["self"].__class__.__name__)
    if items:
      items = [i for i in items if i is not None]
      if len(items) == 1:
        self._put(items[0], block)
      elif len(items) > 1:
        self._put_many(items, block)

  def _find(self, filter):
    pass

  def find(self, filter):
    """Returns items without removing them from storage"""
    return self._find(filter)

  def _update(self, items, update):
    pass

  def update(self, items, update=None):
    """Updates provided items"""
    self._logger.debug("update|%s|%s",
                       len(items), inspect.stack()[1][0].f_locals["self"].__class__.__name__)
    if items:
      items = [i for i in items if i is not None]
      self._update(items, update)

  def _remove(self, items):
    pass

  def remove(self, items):
    """Removes provided items"""
    self._remove(items)
