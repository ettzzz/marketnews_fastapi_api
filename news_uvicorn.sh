ps aux|grep fastapi|awk '{print $2}'|xargs kill -9
uvicorn draft:app --host 127.0.0.1 --port 7705 --reload >> ./uvicorn.log 2>&1 &
