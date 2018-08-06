from lib import Service

class Feed(Service):
  """Base class for datafeeds"""
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
    self._logger.add_field('service', 'Feed')
    self._logger.add_field('vname', self.__class__.__name__)
