# pylint: disable=E1101
# ^
#  fags
#      v
import zmq
import threading

from Config import cnf
from lib.net import Message
from lib import Logger

"""This should be reworked to loadable format. Protos may be different, just like listeners"""


class Remote:
  """Used to run remote Actions.. meh"""
  def __init__(self, ip, port):
    self._send_lock = threading.Lock()
    self._ip = ip
    self._port = port
    self._url = "tcp://%s:%s" % (ip, port)
    self._logger = Logger("Remote %s" % self._url)
    self._z_ctx = None
    self._z_sck = None
  
  def connect(self):
    self._z_ctx = zmq.Context()
    self._z_sck = self._z_ctx.socket(zmq.REQ)

  def run(self, action, data=None):
    msg = Message()
    msg.set('action', action)
    msg.set('data', data)

    rep = self._send_msg(msg)

    if rep.get('status') == False:
      self._logger.info(rep.get('data'))
    
    return rep

  def _send_msg(self, msg):
    self._logger.debug(msg.data())
    self._send_lock.acquire()
    self._z_sck.connect(self._url)
    self._z_sck.send(msg.dump())
    reply = Message.load(self._z_sck.recv())
    self._send_lock.release()
    self._logger.debug(reply.data())
    return reply

