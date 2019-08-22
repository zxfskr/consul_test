import time
import requests
import random
import socket
# import pytest
import consul
# import consul.std

Check = consul.Check


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


consul_host = get_host_ip()
consul_port = 8500
service_name = "foo"
# c = consul.Consul()
c = consul.Consul(host=consul_host, port=consul_port)

addr = "http://{0}:{1}".format(consul_host, '10000')
c.agent.service.register(
    "foo",
    service_id="foo"+consul_host,
    address=consul_host,
    port=10000,
    # ttl="10s"
    check=Check.http(addr, "10s", deregister="90ms"),
)
