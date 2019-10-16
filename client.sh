#!/usr/bin/env bash

ps -ef | grep manage.py | grep -v grep | awk '{print$2}' | xargs kill -9

sleep 1

cd /data/app/fxh/python_project

python3 manage.py runserver 0.0.0.0:9999 &