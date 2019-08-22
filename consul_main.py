import time
import requests
import random
import consul

Check = consul.Check


def check_node_status(node):
    ret = 0
    for check in node["Checks"]:
        if check["Status"] == "passing":
            print(check["CheckID"], " check passing.")
        else:
            print(check["CheckID"], " check error.")
            ret -= 1
    return ret


def check_node_resource(node):
    node_name = node["Node"]["Node"]
    addr = node["Service"]["Address"]
    port = node["Service"]["Port"]
    url = "http://" + addr + ":" + str(port)
    session = requests.Session()
    response = session.get(url, timeout=5)
    print(response.json()["ret"])
    if response.json()["ret"] == 0:
        return {"ret": 0, "node_name": node_name, "url": url}
    else:
        print(response.json()["msg"])
        return {"ret": -1, "node_name": node_name, "url": url}


def get_idle_node(c, service_name):
    node_dict = {"busy": [], "idle": []}
    index, nodes = c.health.service(service_name)
    # node_list = [node for node in nodes]
    print(nodes)

    for node in nodes:
        # print(check_node_status(node))
        if (check_node_status(node) == 0):
            r = check_node_resource(node)
            if (r["ret"] == 0):
                node_dict["idle"].append(r["url"])
            else:
                node_dict["busy"].append(r['url'])
    leng = len(node_dict["idle"])
    if leng > 0:
        return node_dict["idle"][random.randint(0, leng-1)]
    else:
        print("resources are exhausted")
        return False


consul_host = "172.16.81.1"
consul_port = 9000
service_name = "foo"
c = consul.Consul(host=consul_host, port=consul_port)

while True:
    node_url = get_idle_node(c, service_name)
    if (node_url):
        print(node_url)
        session = requests.Session()
        response = session.get(node_url + "/?test=test", timeout=5)
        print(response.json()["ret"])
        if response.json()["ret"] == 0:
            print("task start")
        else:
            print(response.json()["msg"])
    time.sleep(5)
