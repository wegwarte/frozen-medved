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
    redis_conn = Redis(host=self.lcnf.get('redis').get('host'))
    
    jobs = []
    while self._running:
      sleep(self.lcnf.get('delay', 0.07))
      try:
        for job in [j for j in jobs if j.result is not None]:
          self._logger.debug('Publishing finished job result')
          self._data.put(job.result)
          job.cleanup()
          jobs.remove(job)
        for pn, pipeline in self.cnf.get("pipelines").items():
          self._logger.debug("pipeline: %s", pn)
          source = Loader.by_id('storage', pipeline.get('source'))
          for step in pipeline['steps']:
            self._logger.debug("task name: %s", step['task'])
            q = Queue(step.get('priority', 'normal'), connection=redis_conn)
            if q.count + 1 > self.lcnf.get('qsize', 100):
              continue
            filter = {"steps.%s" % step['task']: {'$exists': False}}
            filter.update({key: value for key, value in step.get("if", {}).items()})
            count = step.get('multiple') if step.get('multiple', False) else 1
            # get as much as possible from own pool
            items = self._data.get(block=False, count=count, filter=filter)
            # obtain everything else from source
            if len(items) < count:
              items.extend(source.get(block=False, count=(count - len(items)), filter=filter))
            if items:
              for i in items:
                i['steps'][step['task']] = None
              self._logger.debug("enqueueing task '%s' (count: %s)", step['task'], len(items))
              job = q.enqueue("lib.exeq.Task.run", step['task'], items)
              jobs.append(job)
      except Exception as e:
        self._logger.error("Error in executor main thread: %s", e)