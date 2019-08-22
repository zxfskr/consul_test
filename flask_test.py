from flask import Flask, Response, request
import json
import consul
import socket
import multiprocessing
from multiprocessing import Process, Queue, pool
import random
import time

app = Flask(__name__)
c = consul.Consul()
q1 = Queue()


def long_time_task(ip, q):
    while True:
        # q.get()
        print("long time ", q.get())
        # print(ip, q.get())
        index, data = c.kv.get(ip+"_status")
        if data:
            if data["Value"].decode() == "idle":
                c.kv.put(ip+"_status", "busy")
                print("do working...")
                time.sleep(20)
                print("working finish.")
                c.kv.put(ip+"_status", "idle")
            else:
                print("agent busy")
                time.sleep(5)
        else:
            print("new start.")
            c.kv.put(ip+"_status", "idle")


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


@app.route("/", methods=["GET"])
def flask_test():
    test = 0
    test = request.values.get('test')
    str = ""
    ret = 0
    if test:
        index, data = c.kv.get(ip+"_status")
        if data:
            if data["Value"].decode() == "idle":
                # c.kv.put(ip+"_status", "idle")
                q1.put("task")
                str = "task start"
                ret = 0
            else:
                print("agent busy")
                str = "agent busy"
                ret = -1
        else:
            str = "agent starting..."
            c.kv.put(ip+"_status", "idle")
            q1.put("task")
            ret = 0

        return Response(json.dumps({"ret": ret, "msg": str}), mimetype='text/json')
    else:
        index, data = c.kv.get(ip+"_status")
        if data:
            if data["Value"].decode() == "idle":
                str = "agent idle"
                ret = 0
            else:
                print("agent busy")
                str = "agent busy"
                ret = -1
        else:
            str = "agent starting..."
            c.kv.put(ip+"_status", "idle")
            ret = 0

        return Response(json.dumps({"ret": ret, "msg": str}), mimetype='text/json')


def main():
    ip = get_host_ip()
    index, data = c.kv.get(ip+"_status")
    if not data:
        print("agent starting...")
        c.kv.put(ip+"_status", "idle")

    p1 = Process(target=long_time_task, args=(ip, q1,))
    p1.start()  # 启动进程
    # print(q1.get())     # 从队列中取出一个项目，并打印
    # p1.join()   # 阻塞进程
    # print(q.get())
    # logging.config.fileConfig(config.LOG_CONFIG_FILE)
    app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    print("Sub-process(es) done.")


if __name__ == '__main__':
    try:
        ip = get_host_ip()
        main()
    except Exception as e:
        print(str(e))
    finally:
        print("del")
        c.kv.delete(ip+"_status")
