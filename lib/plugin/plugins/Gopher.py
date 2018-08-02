import netaddr

from Config import cnf
from lib.plugin.plugins import BasePlugin


class Plugin(BasePlugin):
  class TelegramMessage(BasePlugin.TelegramMessage):
    def _init(self):
      self._name = "Gopher"

    def _generate(self):

  class Pipeline(BasePlugin.Pipeline):
    def _init(self):
      self._name = "Gopher"

    def run(self):
      try:
        self._find()
        self._push()
      except Exception as e:
        self._logger.debug("Error occured: %s (%s)", e, self._host['ip'])
      else:
        self._logger.info("Succeeded for %s" % self._host['ip'])
