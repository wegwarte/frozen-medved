from time import sleep
from pymongo import MongoClient

from lib.data import Storage

class MongoStorage(Storage):
  """Mongo storage. Currently the only working correctly."""
  def __init__(self, id, root):
    super().__init__(id, root)
    self._client = MongoClient(self.lcnf.get("url", "127.0.0.1"))
    self._db = self._client.get_database(self.lcnf.get("db"))
    self._coll = self._db.get_collection(self.lcnf.get("coll"))
    self._logger.add_field("db", self.lcnf.get("db"), 7)
    self._logger.add_field("coll", self.lcnf.get("coll"), 7)
    self._logger.debug("Connecting")

  def count(self):
    return self._coll.count()

  def _get(self, block, filter):
    if filter is None:
      filter = {}

    item = self._coll.find_one(filter=filter)
    if block:
      while not item:
        item = self._coll.find_one(filter=filter)
        sleep(1)
    return item

  def _get_many(self, count, block, filter):
    if filter is None:
      filter = {}
    items = self._coll.find(filter=filter, limit=count)
    return items

  def _put(self, item, block):
    if block and self.size() is not 0:
      while self.count() + 1 > self.size():
        self._logger.debug('Collection full: %s of %s', self.count(), self.size())
        sleep(1)
    self._coll.insert_one(item)

  def _put_many(self, items, block):
    if block and self.size() is not 0:
      while self.count() + len(items) > self.size():
        self._logger.debug('Collection full: %s of %s', self.count(), self.size())
        sleep(1)
    self._coll.insert_many(items)

  def _find(self, filter=None):
    if filter is None:
      filter = {}
    return self._coll.find(filter)

  def _update(self, items, update):
    if update:
      filter = {'_id': {'$in': [item['_id'] for item in items]}}
      self._coll.update_many(filter, update, upsert=True)
    else:
      for item in items:
        self._coll.replace_one({'_id': item['_id']}, item, upsert=True)

  def _remove(self, items):
    self._coll.delete_many({'_id': {'$in': [item['_id'] for item in items]}})
