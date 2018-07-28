from lib import Service, Loader, Loadable

from lib.tasks.worker import worker

from time import sleep

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
        redis_conn = Redis(host=self.lcnf.get('redis').get('host'))
        q = Queue('worker', connection=redis_conn)
        if q.count + 1 > self.lcnf.get('size', 100):
          sleep(self.lcnf.get('delay', 2))
          continue
        for pn, pipeline in self.cnf.get("pipelines").items():
          self._logger.debug("pipeline: %s", pn)
          for step in pipeline['steps']:
            self._logger.debug("step: %s", step['name'])
            filter = {
              "not_exist": [
                pn + '_' + step['name']
              ],
              "exist": [
                [tag for tag in step.get("requires")]
              ]
            }
            items = []
            multiple = step.get('multiple', False)
            if multiple != False:
              items = self._data.get(block=False, count=multiple, filter=filter)
            else:
              items = self._data.get(block=False, filter=filter)
            if items:
              self._logger.debug("enqueueing %s.%s with %s", step['package'], step['service'], items)
              q.enqueue("%s.%s" % (step['package'], step['service']), items)
      except Exception as e:
        self._logger.error(e)
