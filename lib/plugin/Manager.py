import importlib

class Manager:
  def __init__(self):
    pass
  
  @staticmethod
  def get_plugin(name):
    return importlib.import_module("lib.plugin.plugins." + name)