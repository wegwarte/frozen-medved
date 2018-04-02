class Action:
  """Base class for remote actions"""
  #this part should be removed, I think
  #dunno
  def __init__(self, datapool):
    self._datapool = datapool
    self.result = None
  
  def run(self, data):
    pass

class data_get(Action):  
  def run(self, data):
    return self._datapool.get(data["plugin"], data["count"])

class data_put(Action):
  def run(self, data):
    self._datapool.put(data['plugin'], data['items'])

class ActionManager:
  @staticmethod
  def get(name: str):
    return globals()[name.replace('.', '_')]