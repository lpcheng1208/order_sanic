#!/bin/sh
echo "kill_server"
ps aux | grep 'app_server' | grep -v grep | awk '{print $2}'| xargs kill -9

echo "start_server"
nohup honcho -e envs/dev.env run python app_server.py -p 8686 >/dev/null &
