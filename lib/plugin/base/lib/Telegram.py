from lib.data import Feed, Filter
from lib.plugin import Manager

import telebot
from time import sleep


class TelegramFeed(Feed):
  """Send data to Telegram chat"""
  # it doesn't work, though
  def __init__(self, id, root):
    super().__init__(self.__run, id, root)

  def __run(self):
    delay = self.lcnf.get("delay", 2)
    while self._running:
      try:
        for chat in self.lcnf.get("chats"):
          chat_id = chat['id']
          sleep(delay)
          continue
          # plugins -> pipelines
          # it is in progress
          #TODO
          msg = Manager.get_plugin(plugin).Plugin.TelegramMessage(host)
          msg.run()
          if msg.data['txt']:
            tbot = telebot.TeleBot(self.lcnf.get('token'), threaded=False)
            if msg.data['img']:
              self._logger.debug("Send IP with img %s:%s to %s" % (host['ip'], host['port'], chat_id))
              tbot.send_photo("@" + chat_id, msg.data['img'], caption=msg.data['txt'])
            else:
              self._logger.debug("Send IP %s:%s to %s" % (host['ip'], host['port'], chat_id))
              tbot.send_message("@" + chat_id, msg.data['txt'])
          else:
            self._logger.error('Empty text!')
        sleep(delay)
      except Exception as e:
        self._logger.warn(e)
