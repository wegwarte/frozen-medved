import json, yaml
import sys, os
import importlib

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Config import namedtupledict
from lib import Logger, Loader

logger = Logger('Linter')
logger.info('Reading config')

with open('data/config.yaml', 'r') as config:
  data = yaml.load(config)

cnf = json.loads(json.dumps(data), object_hook=lambda d: namedtupledict('X', d.keys())(*d.values()))

logger.info("Config: \n%s", json.dumps(data, indent=2))

logger.info('CORE')
services_check = ["datamgr", "listener", "executor"]
services = []
logger.info("Checking services: %s", ", ".join(services))
for s, sv in cnf.core:
  services.append(s)
print(services)
for s in services_check:
  if not s in services:
    logger.error("Service %s is not defined!", s)
  else:
    logger.info("Service %s is defined, continuing", s)
    for k, v in cnf.core[s]:
      if k == 'package':
        try:
          importlib.import_module(v)
        except Exception as e:
          logger.error("Unable to load package %s!\n%s", v, e)
        else:
          logger.info("Package %s was imported successfully", v)
      elif k == 'service':
        try:
          Loader(cnf.core[s]['package']).get(v)
        except Exception as e:
          logger.error("Unable to load package %s!\n%s", v, e)
        else:
          logger.info("Service %s was imported successfully", v)
