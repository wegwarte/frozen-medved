#!/usr/bin/python3
# -*- coding: utf-8 -*-

import yaml

cnf = {}
with open('data/config.yaml') as config_file:
  cnf = yaml.load(config_file)