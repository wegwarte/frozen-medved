#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml

class Config(object):
  def __init__(self):
    with open('data/config.yaml') as config_file:
      self.config = yaml.load(config_file)

  def get(self, key, defval=None):
    return self.config.get(key, defval)


cnf = Config()