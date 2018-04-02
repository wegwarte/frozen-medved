#!/bin/bash -x

export CORE_IP=$(host ${CORE_IP} | head -n1 | grep -Po "(\d+\.?){4}")

source /mdvd/docker/env

/tmp/confd -onetime -backend env

cat /etc/proxychains.conf
cat /mdvd/config.json | python -m json.tool