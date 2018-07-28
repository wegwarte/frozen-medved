# medved
alpha beta whatever 
partly works

## roadmap
refactor README and lib/plugin/plugins/*
cleanup *

probably Listener shoul be part of Core in order to supervise everything

tasks don't store results currently. need to implement some validation of performed tasks (at least in Executor thread before spreading new tasks)
http://python-rq.org/docs/results/

## configuration

`data/config.yaml`
```
# lists top-level services (like listeners, executors, data-manager) and pipelines enabled
core:
  services: # should point to correct service
  - data_manager
  - rq_executor
  pipelines:
  - ftp

# describes top-level services and their configurations
services:
  data_manager:
    # REQUIRED package name, just like path to file with dots
    package: lib.data.Manager
    # REQUIRED class inherited from Service (lib.Service)
    service: DataManager
    # REQUIRED used to select one of storages
    data:
      id: pool
    # there can be more service-specific configuration fields
    # for now they can be found in code :)
    sources:
    - random_ip
    feeds: 
    - test_telegram
  rq_executor:
    package: lib.exeq.Executor
    service: RQExecutor
    data:
      id: pool
    redis:
      host: "127.0.0.1"

# describes datasources for data_manager
sources:
  random_ip:
    package: lib.plugin.base.lib.IP
    service: RandomIP
    data:
      id: random_ip

# describes datafeeds for data_manager
feeds:
  test_telegram: # doesn't work yet, eh
    package: lib.plugin.base.lib.Telegram
    service: TelegramFeed
    data:
      id: pool
    token: 
    chats: 
      - id: good_evening
        pipelines: [ftp, gopher]
        filter:
          clause: any-of
          equal: 
          - ftp_list_files_status: success
          - gopher_collect_status: success

# describes various storages, e.g. data pool for pipelines or queues for datasources 
storage:
  pool:
    # REQUIRED
    package: lib.plugin.base.lib.Mongo
    service: MongoStorage
    size: 40960
    # service-specific
    db: "medved"
    coll: 'pool'
  random_ip:
    package: lib.plugin.base.lib.Mongo
    service: MongoStorage
    size: 500
    db: "medved"
    coll: 'randomipsource'

# describes available pipelines
pipelines:
  ftp:
    # list of steps with dependencies
    steps: 
    # will pass 10 items to lib.plugin.iscan.tasks.common.scan
    - name: scan
      package: lib.plugin.iscan.tasks.common
      service: scan
      multiple: 10 # default: False
      requires: []
    # will pass 1 item marked with ftp_scan to lib.plugin.iscan.tasks.ftp.connect
    - name: connect
      package: lib.plugin.iscan.tasks.ftp
      service: connect
      requires:
      - ftp_scan
    - name: list_files
      package: lib.plugin.iscan.tasks.ftp
      service: list_files
      requires:
      - ftp_connect

# various configurations for tasks
tasks:
  ftp_scan:
    ports:
    - 21
  ftp_connect:
    logins: data/ftp/logins.txt
    passwords: data/ftp/passwords.txt
    bruteforce: true
    timeout: 15
  ftp_list_files:

logging: 
  Storage: INFO 
```
probably it can be launched with docker, however I didn't test it yet

run `make base && docker-compose up --build --scale worker=5`

or simply `python medved.py`

you'll need working redis and mongodb for default configuration

## top-level services

### lib.data.Manager.DataManager
Orchestrates datasources and datafeeds - starts and stops them, also checks pool size. If it is too low - takes data from DS.
### lib.exeq.Executor.RQExecutor
Should run pipelines described in configuration. Works via [RedisQueue](http://python-rq.org/), so needs some Redis up and running
Basically takes data from pool and submits it to workers.
RQ workers should be launched separately (`rqworker worker` from code root)
