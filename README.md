# Ansible API
基于Flask、Celery开发的Ansible api (ansible==1.6.6)
---

## Based on
* flask
* celery
* redis

## Debug
1. run develop server: 
```
python manage.py runserver
``` 
2. run celery worker: 
```
# ansible use root (Not recommanded)
export C_FORCE_ROOT=True
#
export PYTHONOPTIMIZE=1
celery -A celery_worker.celery worker --loglevel=debug
```

## API Usage：

* POST /ad_hoc
  - param : < json >  
```
{ 
    "module": "shell",
    "args": "hostname -s",
    "host": "all",
    "resource": {
        "hosts": {
            "testdb": {
                "ip": "xxx.xxx.xxx.x",
                "port": "22",
                "username": "root",
                "password": "yyyyyyyyy",
            }
        }
    },
    "sign": "5135ec5c6526d01b5a57ea221390d9dc",
}
```
   - return: < json >
```
{
    "task_id": "suijizifuchuan",
    "task_url": "/taskstats/ad_hoc/suijizifuchuan"
}
```
* POST /playbook
  - param: < json >
```
{
    "playbook": "test.yml", 
    "sign" : "9c25246e3bf6af494ebfcf304c23e2b1"
}
```
  - return: < json >
```
{
    "task_id": "suijizifuchuan",
    "task_url": "/taskstats/playbook/suijizifuchuan"
}
```
* GET /taskstats/< task_type >/< task_id >
  - return: < json >
```
{
    "state": "task_state",
    "status": "task_info",
}
```

## Deploy
* supervisord 启动配置： supervisord.conf
* uwsgi 配置： uwsgi.yml

`supervisord -c supervisord.conf`