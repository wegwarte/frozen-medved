#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

from Config import cnf
from lib import Logger, Loader

class Core:
  def __init__(self):
    self.cnf = cnf.Core
    self.logger = Logger("Core")
    self.logger.debug("Loading services")

    self._services = []
    for service in self.cnf.services:
      service = Loader.by_id('services', service)
      self._services.append(service)

  def start(self):
    self.logger.info("Starting")
    for service in self._services:
      service.start()
    self.logger.info("Started")

  def stop(self):
    self.logger.info("Stopping Core")
    for service in self._services:
      service.stop()
    self.logger.info("Stopped")

if __name__ == '__main__':
  core = Core()
  core.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    core.stop()
