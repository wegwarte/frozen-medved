from lib import Loader

class Filter:
  """Base class for filters..? ehm, it should be part of storage, i think"""
  def __init__(self):
    self._not_exist = []
    self._exist = []
    self._equal = {}
    self._not_equal = {}

  def generate(self):
    pass

def MongoFilter(filter):
  def generate(self):
    data = {}
    #for i in 


# dunno