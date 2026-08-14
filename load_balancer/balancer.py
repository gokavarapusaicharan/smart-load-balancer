import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading

from load_balancer.config import HOST, LOAD_BALANCER_PORT, BUFFER_SIZE
from load_balancer.health_checker import start_health_check
from load_balancer.state_manager import (
    initialize_state,
    get_current_algorithm,
    select_and_start_request,
    mark_request_finished
)
from common.logger import logger


def is_valid_request(data):
    return data is not None and data.strip() != ""


def forward_to_backend(server, data):
    backend_socket = None

    try:
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.settimeout(30)
        backend_socket.connect((server["host"], server["port"]))
        backend_socket.sendall(data.encode())

        response = backend_socket.recv(BUFFER_SIZE).decode()
        return response

    except Exception as e:
        return f"Server {server['id']} failed while processing request: {e}"

    finally:
        if backend_socket:
            backend_socket.close()


def handle_client(client_socket, client_addr):
    selected_server = None

    try:
        data = client_socket.recv(BUFFER_SIZE).decode()

        if not is_valid_request(data):
            client_socket.sendall("Invalid request".encode())
            return

        algorithm = get_current_algorithm()

        selected_server = select_and_start_request(algorithm, data)

        if selected_server is None:
            client_socket.sendall("No active backend servers available".encode())
            return

        logger.info(f"Request '{data}' handled by Server {selected_server['id']}")
        print(
            f"[Load Balancer] Algorithm: {algorithm} | "
            f"Request '{data}' -> Server {selected_server['id']}"
        )

        response = forward_to_backend(selected_server, data)
        client_socket.sendall(response.encode())

    except Exception as e:
        try:
            client_socket.sendall(f"Load balancer error: {e}".encode())
        except:
            pass
        print(f"[Load Balancer] Error: {e}")

    finally:
        if selected_server is not None:
            mark_request_finished(selected_server["id"])

        client_socket.close()


def start_load_balancer():
    initialize_state()

    lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lb_socket.bind((HOST, LOAD_BALANCER_PORT))
    lb_socket.listen()

    print(f"[Load Balancer] Running on {HOST}:{LOAD_BALANCER_PORT}")

    threading.Thread(target=start_health_check, daemon=True).start()

    while True:
        client_socket, client_addr = lb_socket.accept()

        threading.Thread(
            target=handle_client,
            args=(client_socket, client_addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    start_load_balancer()