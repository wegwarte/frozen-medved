"""
Provides Service class
"""


from time import sleep
from threading import Thread
from lib import Logger, Loader, Loadable
from Config import cnf

class Service(Loadable):
  """Base class for loadale service"""
  # service consists of running thread and storage attached
  def __init__(self, thread, id, root=cnf):
    super().__init__(id, root)

    self._data = Loader.by_id('storage', self.lcnf.get("storage"))

    self._stop_timeout = 10
    self._running = False
    self._thread_to_run = thread
    self._run_thread = None
    self._logger = Logger('Service')

    self._init()

  def _init(self):
    pass

  def start(self):
    """Executes pre_start, starts thread and executes post_start"""
    self._logger.debug('pre_start')
    self._pre_start()

    self._logger.debug('start')
    self._running = True
    self._run_thread = Thread(target=self._thread_to_run)
    self._run_thread.daemon = True
    self._run_thread.start()

    self._logger.debug('post_start')
    self._post_start()

    self._logger.info('start finished')

  def stop(self):
    """Executes pre_stop, stops thread and executes post_stop"""
    self._logger.debug('pre_stop')
    self._pre_stop()

    self._logger.debug('stop')
    self._running = False
    self._run_thread.join(timeout=self._stop_timeout)

    self._logger.debug('post_stop')
    self._post_stop()

    self._logger.info('stop finished')

  def __run(self):
    while self._running:
      self._logger.debug('NOOP')
      sleep(1)

  def _pre_stop(self):
    pass

  def _post_stop(self):
    pass

  def _pre_start(self):
    pass

  def _post_start(self):
    pass
