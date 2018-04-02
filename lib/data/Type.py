from lib import Loadable, Logger

# dunno

class Type(Loadable):
  def __init__(self):
    self.data = {}
  
class Host(Type):
  def __init__(self):
    self.data = {
      'ip': ''
    }
