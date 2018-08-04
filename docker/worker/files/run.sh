#!/usr/bin/env bash

export CORE_IP=$(host ${CORE_IP} | head -n1 | grep -Po "(\d+\.?){4}")

/tmp/confd -onetime -backend env

cd /mdvd && rq worker high normal low -u "redis://${REDIS_IP}:6379/"
