from pymongo import MongoClient
from time import sleep
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
    # TODO cleanup dat BS
    if filter is None:
      filter = {}
    ne_tags = {}
    e_tags = {}
    if filter.get('not_exist'):
      tags = []
      for ne in filter.get('not_exist'):
        tags.append(ne)
      ne_tags = {'tags': {'$not': {'$all': tags}}}
      del filter['not_exist']
    if filter.get('exist'):
      tags = []
      for e in filter.get('exist'):
        tags.append(e)
      e_tags = {'tags': {'$all': tags}}
      del filter['exist']
    filter = {'$and': [ne_tags, e_tags]}
    item = self._coll.find_one_and_delete(filter=filter)
    if block:
      while not item:
        item = self._coll.find_one_and_delete(filter=filter)
        sleep(1)
    
    return item
  
  def _put(self, item, block):
    if block:
      while self.count() + 1 > self.size():
        self._logger.debug('Collection full: %s of %s', self.count(), self.size())
        sleep(1)
    self._coll.insert_one(item)
  
  def _put_many(self, items, block):
    if block:
      while self.count() + len(items) > self.size():
        self._logger.debug('Collection full: %s of %s', self.count(), self.size())
        sleep(1)
    self._coll.insert_many(items)

  def _find(self, filter=None):
    if filter is None:
      filter = {}
    return self._coll.find(filter)
