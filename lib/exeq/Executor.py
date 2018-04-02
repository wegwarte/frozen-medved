from lib import Service, Loader, Loadable

from lib.tasks.worker import worker

from rq import Queue
from redis import Redis


class Executor(Service):
  """Base class for executors"""
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
    self._logger.add_field('service', 'Executor')
    self._logger.add_field('vname', self.__class__.__name__)


class RQExecutor(Executor):
  """rq (redis queue) executor - lightweight; workers placed on different nodes"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    while self._running:
      try:
        #TODO
        for pn, pipeline in self.cnf.pipelines:
          self._logger.debug("pipeline: %s", pn)
          for step in pipeline.steps:
            self._logger.debug("step: %s", step.name)
            redis_conn = Redis(host=self.lcnf.redis.host)
            q = Queue('worker', connection=redis_conn)
            filter = {
              "not_exist": [
                pn + '_' + step.name
              ] 
            }
            items = []
            if step.multiple != False:
              items = self._data.get(count=step.multiple, filter=filter)
            else:
              items = self._data.get(filter=filter)
            for i in items:
              q.enqueue(Loader(step.package).get(step.service), i)
      except Exception as e:
        self._logger.error(e)
