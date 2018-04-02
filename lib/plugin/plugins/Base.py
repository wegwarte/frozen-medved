from lib.util import get_logger
from Config import cnf
from Storage import DB


class Plugin:
  class TelegramMessage:
    def __init__(self, host, name='Base'):
      self._host = host
      self._name = name
      self._init()
      self._logger = get_logger("%s Message" % self._name, cnf.stalker[self._name].loglevel)
      self.data = {
        'txt': 'Not implemented',
        'img': None
      }

    def _init(self):
      pass

    def run(self):
      try:
        self._generate()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s:%s)", e, self._host['ip'], self._host['port'])

    def _generate(self):
      pass
  
  
  class Pipeline:
    class PipelineError(Exception):
      pass
    
    def __init__(self, host, name='Base'):
      self._logger = get_logger("%s Pipeline" % name, cnf.stalker[name].loglevel)
      self._host = host
      self._name = name
      self._init()
      self._logger.debug("Starting for %s:%s", self._host['ip'], self._host['port'])
      self.run()

    def _init(self):
      pass

    def run(self):
      try:
        self._find()
        self._push()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s:%s)", e, self._host['ip'], self._host['port'])

    def _find(self):
      pass

    def _push(self):
      DB.collection('qu_%s_feed' % self._name).insert_one(self._host)
