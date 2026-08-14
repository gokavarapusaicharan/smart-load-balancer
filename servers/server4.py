import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading

from common.logger import logger

HOST = "127.0.0.1"
PORT = 8004
SERVER_ID = 4


def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        print(f"[Server {SERVER_ID}] Processing: {data}")

        time.sleep(2)

        response = f"Response from Server {SERVER_ID}: handled request '{data}'"
        conn.sendall(response.encode())

    except Exception as e:
        print(f"[Server {SERVER_ID}] Error: {e}")

    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    logger.info(f"Server {SERVER_ID} started on {HOST}:{PORT}")
    print(f"[Server {SERVER_ID}] Running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()