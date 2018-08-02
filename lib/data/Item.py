class Item(object):
  """Base class for item"""
  def __init__(self, source):  
    self._item = {
      'source': source,
      'steps': {},
      'data': {}
    }

  def set(self, key, value):
    elem = self._item['data']
    upd = {}
    for x in key.split("."):
      elem = elem.get(x, {})
      upd[x] = {}
    upd[0] = value
    self._item['data'].update(upd)