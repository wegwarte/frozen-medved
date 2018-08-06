from time import sleep
import telebot

from lib.data import Feed

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
          chat_id = chat.get('id')
          self._logger.debug(chat_id)
          filter = {"feed.%s" % self._id: {'$exists': False}}
          filter.update({key: value for key, value in chat.get("if", {}).items()})
          items = self._data.get(block=False, count=10, filter=filter)
          self._logger.debug(items)
          if items:
            self._data.update(items, {'$set': {'feed.%s' % self._id: True}})
            tbot = telebot.TeleBot(self.lcnf.get('token'), threaded=False)
            for i in items:
              self._logger.debug("@%s: %s", chat_id, i['data']['message'])
              tbot.send_message("@" + chat_id, i['data']['message'])
        sleep(delay)
      except Exception as err:
        self._logger.warn(err)
