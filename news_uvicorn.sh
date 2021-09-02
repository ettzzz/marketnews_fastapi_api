
#！/bin/bash

pid_file="pids.uvicorn"

kill_now(){
    # ps aux|grep fastapi|awk '{print $2}'|xargs kill -9
    cat $pid_file|xargs sudo kill -9
}

start_new(){
    # uvicorn main:app --host 127.0.0.1 --port 7705 >> ./uvicorn.log 2>&1 &
    uvicorn main:app --host 127.0.0.1 --port 7705 >> ./uvicorn.log 2>&1 & echo $! > $pid_file
}

option=$1

if [ $option == "--reload" ]; then
    kill_now
    start_new
    echo "reload done"
elif [ $option == "--stop" ]; then
    kill_now
    echo "stop done"
elif [ $option == "--start" ]; then
    start_new
    echo "start done"
else
    echo "Wrong option!"
fi
