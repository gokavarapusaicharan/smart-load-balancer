import sys
import os
import json
import socket
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request
from load_balancer.state_manager import set_current_algorithm

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "dashboard_data.json")

LOAD_BALANCER_HOST = "127.0.0.1"
LOAD_BALANCER_PORT = 9000
BUFFER_SIZE = 4096


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/status")
def status():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/set_algorithm", methods=["POST"])
def set_algorithm():
    data = request.get_json()
    algorithm = data.get("algorithm")

    if algorithm not in ["round_robin", "least_connections"]:
        return jsonify({"error": "Invalid algorithm"}), 400

    set_current_algorithm(algorithm)
    return jsonify({"algorithm": algorithm})

def send_to_load_balancer(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOAD_BALANCER_HOST, LOAD_BALANCER_PORT))
    client_socket.sendall(message.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    client_socket.close()
    return response

@app.route("/send_requests", methods=["POST"])
def send_requests():
    uploaded_file = request.files.get("request_file")

    if not uploaded_file:
        return jsonify({"error": "No file uploaded"}), 400

    lines = uploaded_file.read().decode().splitlines()

    outputs = [""] * len(lines)
    threads = []

    def worker(index, request_text):
        try:
            response = send_to_load_balancer(request_text)
            outputs[index] = f"{request_text} -> {response}"
        except Exception as e:
            outputs[index] = f"{request_text} -> Error: {e}"

    for i, line in enumerate(lines):
        request_text = line.strip()

        if not request_text:
            continue

        t = threading.Thread(
            target=worker,
            args=(i, request_text)
        )

        threads.append(t)
        t.start()

        # IMPORTANT: delay between incoming requests
        time.sleep(0.3)

    for t in threads:
        t.join()

    return jsonify({"outputs": outputs})
if __name__ == "__main__":
    app.run(debug=True, port=5000)