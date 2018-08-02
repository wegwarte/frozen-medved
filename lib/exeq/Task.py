from lib import Loadable, Logger, Loader

from Config import cnf

class Task(Loadable):
  def __init__(self, id, root):
    super().__init__(id, root)
    self._logger = Logger(self.__class__.__name__)
  
  def run(self, items):
    result = []
    try:
      result = self._run(items)
    except Exception as e:
      self._logger.debug("Error occured while executing: %s", e)
    return result

  def _run(self, items):
    return items

def run(task_name, items):
  result = Loader.by_id('tasks', task_name).run(items)
  return result