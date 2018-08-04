#!/usr/bin/env bash

export CORE_IP=$(host ${CORE_IP} | head -n1 | grep -Po "(\d+\.?){4}")
export MONGO_IP=$(host ${MONGO_IP} | head -n1 | grep -Po "(\d+\.?){4}")
export SELENIUM_IP=$(host ${SELENIUM_IP} | head -n1 | grep -Po "(\d+\.?){4}")
export REDIS_IP=$(host ${REDIS_IP} | head -n1 | grep -Po "(\d+\.?){4}")

/tmp/confd -onetime -backend env

#sudo -u tor tor

#cd /mdvd && proxychains -q python3 medved.py
cd /mdvd && python3 medved.py
