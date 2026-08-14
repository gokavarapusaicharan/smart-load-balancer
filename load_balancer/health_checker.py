import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import time

from load_balancer.config import SERVERS, HEALTH_CHECK_INTERVAL, SERVER_TIMEOUT
from load_balancer.state_manager import update_server_health
from common.logger import logger


def is_server_alive(server):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(SERVER_TIMEOUT)
        sock.connect((server["host"], server["port"]))
        sock.close()
        return True

    except Exception:
        return False


def start_health_check():
    while True:
        for server in SERVERS:
            alive = is_server_alive(server)

            update_server_health(server["id"], alive)

            if not alive:
                logger.warning(f"Server {server['id']} is DOWN")

        time.sleep(HEALTH_CHECK_INTERVAL)