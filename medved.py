#!/usr/bin/python3

import time

from Config import cnf
from lib import Logger, Loader

class Core:
  """Core class, contains core services (like listeners, executors, datapool)"""
  def __init__(self):
    self.cnf = cnf.get("core")
    self.logger = Logger("Core")
    self.logger.debug("Loading services")

    self._services = []

    for service_name in self.cnf.get("services"):
      service = Loader.by_id('services', service_name)
      self._services.append(service)

  def start(self):
    """Starts all loaded services"""
    self.logger.info("Starting")
    for service in self._services:
      service.start()
    self.logger.info("Started")

  def stop(self):
    """Stops all loaded services"""
    self.logger.info("Stopping Core")
    for service in self._services:
      service.stop()
    self.logger.info("Stopped")

if __name__ == '__main__':
  CORE = Core()
  CORE.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    CORE.stop()
