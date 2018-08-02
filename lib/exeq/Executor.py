from lib import Service, Loader, Loadable

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
  """rq (redis queue) executor"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    redis_conn = Redis(host=self.lcnf.get('redis').get('host'))
    jobs = []
    
    while self._running:
      sleep(self.lcnf.get('delay', 0.2))
      try:
        for pn, pipeline in self.cnf.get("pipelines").items():
          if pn not in self.cnf.get('core').get('pipelines'):
            continue
          source = Loader.by_id('storage', pipeline.get('source'))
          for step in pipeline['steps']:
            q = Queue(step.get('priority', 'normal'), connection=redis_conn)
            for job_id in jobs:
              job = q.fetch_job(job_id)
              if job:
                if job.result is not None:
                  self._logger.debug("%s|%s", job_id, job._status)
                  self._data.update(job.result)
                  job.cleanup()
                  jobs.remove(job_id)
            if len(jobs) + 1 > self.lcnf.get('qsize', 200):
              continue
            filter = {"steps.%s" % step['task']: {'$exists': False}}
            filter.update({key: value for key, value in step.get("if", {}).items()})
            count = step.get('parallel', 1)
            # get as much as possible from own pool
            items = self._data.get(block=False, count=count, filter=filter)
            # obtain everything else from source
            if len(items) < count:
              new_items = source.get(block=False, count=(count - len(items)), filter=filter)
              items.extend(new_items)
              source.remove(new_items)

            if items:
              self._data.update(items, {'$set': {'steps.%s' % step['task']: None}})
              job = q.enqueue("lib.exeq.Task.run", step['task'], items)
              self._logger.info("%s|%s|%s|%s", job.id, step.get('priority', 'normal'), step['task'], len(items))
              jobs.append(job.id)
      except Exception as e:
        self._logger.error("Error in executor main thread: %s", e)