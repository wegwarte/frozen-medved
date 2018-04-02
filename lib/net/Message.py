import pickle

class Message:
    """Message. Just a pickled dict."""
    def __init__(self, data=None):
        if data is None:
            data = {}
        self._data = data

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key, None)

    def data(self):
        return self._data

    def dump(self):
        return pickle.dumps(self)

    @classmethod
    def load(cls, pickled_data):
        try:
            obj = pickle.loads(pickled_data)
            return cls(obj.data())
        except EOFError:
            return cls({})