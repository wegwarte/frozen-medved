# pylint: disable=E1101
# ^
#  fags
#      v
import zmq
from lib import Service
from lib.net import ActionManager, Message


class Listener(Service):
  """Base class for listeners"""
  def __init__(self, thread, id, root):
    super().__init__(thread, id, root)
    self._logger.add_field('service', 'Listener')
    self._logger.add_field('vname', self.__class__.__name__)

class ZMQListener(Listener):
  """ZMQ (Zero MQ) listener - uses my own shitty legacy proto"""
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)
  
  def _pre_start(self):
    self._running = True
    self._z_ctx = zmq.Context()
    self._z_sck = self._z_ctx.socket(zmq.REP)
    self._z_sck.bind("tcp://%s:%s" % (self.lcnf.get('listen', '127.0.0.1'), self.lcnf.get('port', 12321)))

  def _post_stop(self):
    self._z_ctx.destroy()

  def __run(self):
    while self._running:
      try:
        reply = Message()
        msg = None
        try:
          msg = Message.load(self._z_sck.recv())
          if msg:
            self._logger.info("Requested %s", msg.get('action'))
            action = ActionManager.get(msg.get('action'))(self._datapool)
            reply.set('data', action.run(msg.get('data')))
            reply.set('status', True)
        except Exception as e:
          self._logger.warn("Action %s failed", msg.get('action'))
          self._logger.debug(e)
          reply.set('data', e)
          reply.set('status', False)
        self._z_sck.send(reply.dump())
      except Exception as e:
        self._logger.error(e)
