# medved
alpha beta whatever 
partly works


## configuration

`data/config.yaml`
```
---
dsl_version: 1

core:
  services:
  - random_ip
  - rq_executor
  - tg_feed
  pipelines:
  - ftp
  - gopher

services:
  random_ip:
    package: lib.plugin.base.lib.IP
    service: RandomIP
    storage: ip_source
  rq_executor:
    package: lib.exec.Executor
    service: RQExecutor
    storage: pool
    redis:
      host: "127.0.0.1"
  tg_feed:
    package: lib.plugin.base.lib.Telegram
    service: TelegramFeed
    storage: pool
    token: "mocken"
    chats:
    - id: aiWeipeighah7vufoHa0ieToipooYe
      if:
        steps.ftp_apply_tpl: true
        data.filter: false
    - id: ohl7AeGah5uo8cho4nae9Eemaeyae3
      if:
        steps.gopher_apply_tpl: true
        data.filter: false

storage:
  pool:
    package: lib.plugin.base.lib.Mongo
    service: MongoStorage
    size: 0
    db: "medved"
    coll: 'pool'
  ip_source:
    package: lib.plugin.base.lib.Mongo
    service: MongoStorage
    size: 800
    db: "medved"
    coll: 'ip_source'


pipelines:
  ftp:
    source: ip_source
    steps:
    - task: ftp_scan
      priority: low
      parallel: 100
    - task: ftp_connect
      priority: normal
      if:
        steps.ftp_scan: true
    - task: ftp_list_files
      priority: high
      if:
        steps.ftp_connect: true
    - task: ftp_apply_tpl
      priority: high
      if:
        steps.ftp_list_files: true
  gopher:
    source: ip_source
    steps:
    - task: gopher_scan
      priority: normal
      parallel: 100
    - task: gopher_find
      priority: high
      if:
        steps.gopher_scan: true
    - task: gopher_apply_tpl
      priority: high
      if:
        steps.gopher_find: true
    
  http:
    source: ip_source
    steps:
    - task: http_scan
      priority: low
      parallel: 25

tasks:
  gopher_scan:
    package: lib.plugin.iscan.tasks.common
    service: MasScanTask
    ports:
    - 70
  gopher_find:
    package: lib.plugin.iscan.tasks.gopher
    service: GopherFindTask
  gopher_apply_tpl:
    package: lib.plugin.base.tasks.text
    service: Jinja2TemplateTask
    path: lib/plugin/iscan/templates/gopher.tpl

  ftp_scan:
    package: lib.plugin.iscan.tasks.common
    service: MasScanTask
    ports:
    - 21
  ftp_connect: 
    package: lib.plugin.iscan.tasks.ftp
    service: FTPConnectTask
    logins: data/ftp/logins.txt
    passwords: data/ftp/passwords.txt
    bruteforce: true
    timeout: 15
  ftp_list_files:
    package: lib.plugin.iscan.tasks.ftp
    service: FTPListFilesTask
    filter: true
  ftp_apply_tpl:
    package: lib.plugin.base.tasks.text
    service: Jinja2TemplateTask
    path: lib/plugin/iscan/templates/ftp.tpl

logging: 
  Storage: DEBUG
  Loader: DEBUG
```
probably it can be launched with docker, however I didn't test it yet

run `make base && docker-compose up --build --scale worker=5`

or simply `python medved.py`

you'll need working redis and mongodb for default configuration

## top-level services

### sources ###
### feeds ###

### lib.exec.Executor.RQExecutor
Should run pipelines described in configuration. Works via [RedisQueue](http://python-rq.org/), so needs some Redis up and running
Basically takes data from pool and submits it to workers.
RQ workers should be launched separately (`rqworker worker` from code root)
