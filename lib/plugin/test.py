from threading import Thread
from time import sleep

class A: # NOOP
  def __init__(self, thread = None):
    if thread:
      self.__thread = Thread(target=thread)
    self._running = False
    self._init()
  
  def _init(self):
    pass
  
  def start(self):
    self._running = True
    self.__thread.daemon = True
    self.__thread.start()
  
  def stop(self):
    self._running = False
    self.__thread.join()
  
  def __run(self):
    while(self._running):
      print('NOOP')
      sleep(1)

class B(A): # NOOP
  def __init__(self):
    super().__init__(self.__run)

  def __run(self):
    while(self._running):
      print('OP')
      sleep(1)

class C(A): # NOOP
  def __run(self):
    while(self._running):
      print('OP')
      sleep(1)

  def _init(self):
    self.__thread = Thread(target=self.__run)

