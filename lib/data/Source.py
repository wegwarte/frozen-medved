import copy

from lib import Service

class Source(Service):
  """Base class for datasources"""
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
    self._logger.add_field('service', 'Source')
    self._logger.add_field('vname', self.__class__.__name__)

    self._item = {
      'source': self._id,
      'steps': {},
      'data': {}
    }

  def _create(self):
    return copy.deepcopy(self._item)

  def _prepare(self, item):
    pass
