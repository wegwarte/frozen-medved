import logging

from Config import cnf as config

import importlib
import sys, os

class Logger(logging.Logger):
  """Logger. standard logging logger with some shitcode on the top"""
  def __init__(self, name):
    self._lf_start = '[%(asctime)s][%(levelname)-7s][%(name)-10s]'
    self._lf_end   = ' %(message)s'
    self._lf_extra = {}
    super().__init__(name, level=self.get_level(name))
    self._update()

  def get_level(self, name):
    return logging.getLevelName(config.get("logging").get(name, "DEBUG"))

  def add_field(self, name, default, size=3):
    if not name in self._lf_extra:
      self._lf_extra[name] = {
        'default': default,
        'size': size
      }
      self._update()

  def error(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.ERROR):
      kwargs['extra'] = {}
      for f, fv in self._lf_extra.items():
        kwargs['extra'][f] = fv['default']
      self._log(logging.ERROR, msg, args, **dict(kwargs))

  def warn(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.WARN):
      kwargs['extra'] = {}
      for f, fv in self._lf_extra.items():
        kwargs['extra'][f] = fv['default']
      self._log(logging.WARN, msg, args, **dict(kwargs))

  def info(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.INFO):
      kwargs['extra'] = {}
      for f, fv in self._lf_extra.items():
        kwargs['extra'][f] = fv['default']
      self._log(logging.INFO, msg, args, **dict(kwargs))

  def debug(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.DEBUG):
      kwargs['extra'] = {}
      for f, fv in self._lf_extra.items():
        kwargs['extra'][f] = fv['default']
      self._log(logging.DEBUG, msg, args, **dict(kwargs))

  def del_field(self, name):
    if name in self._lf_extra.keys():
      del self._lf_extra[name]
      self._update()

  def _update(self):
    self.handlers = []

    fields = "".join(['[%(' + name + ')-' + str(f['size']) + 's]' for name, f in self._lf_extra.items()])
    lf = logging.Formatter(self._lf_start + fields + self._lf_end)

    ch = logging.StreamHandler()
    ch.setLevel(self.level)
    ch.setFormatter(lf)

    self.addHandler(ch)


class Loadable:
  """parent for loadable from configuration"""
  def __init__(self, id, root=config):
    self.cnf = config
    self.lcnf = root[id]
    self._id = id


class Loader:
  """Loads classes by configuration"""
  def __init__(self, path):
    self._path = path
    self._name = path.split('.')[-1]
    # TODO remove # self._dir = ".".join(path.split('.')[:-1]) 
    self._logger = Logger('Loader')
    self._logger.add_field('path', self._path)

  def get(self, name):
    sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
    self._logger.debug('load %s', name)
    result = importlib.import_module(self._path)
    return getattr(result, name)
  
  @classmethod
  def by_id(cls, section, id):
    l = cls(config[section][id].get('package'))
    return l.get(config[section][id].get('service'))(id=id, root=config[section])
