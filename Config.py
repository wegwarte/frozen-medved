#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import yaml
import logging
from collections import namedtuple


def namedtupledict(*a, **kw):
    nt = namedtuple(*a, **kw)

    def getitem(self, key):
        try:
            if type(key) == str:
                return getattr(self, key)
            return tuple.__getitem__(self, key)
        except Exception:
            raise Exception("Could not get %s" % key)

    def ntiter(self):
        for name in self._fields:
            yield name, getattr(self, name)

    nt.__iter__ = ntiter
    nt.__getitem__ = getitem

    return nt

cnf = {}
# dafuq
with open('data/config.yaml') as config_file:
  cnf = json.loads(json.dumps(yaml.load(config_file)), object_hook=lambda d: namedtupledict('X', d.keys())(*d.values()))