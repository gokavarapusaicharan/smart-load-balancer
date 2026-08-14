import os
import json
import threading
import copy
import tempfile

from load_balancer.config import SERVERS, ALGORITHM

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "dashboard_data.json")

state_lock = threading.RLock()

state = {
    "current_algorithm": "round_robin",
    "round_robin_index": 0,
    "servers": [
        {
            "id": server["id"],
            "host": server["host"],
            "port": server["port"],
            "is_alive": True,
            "active_connections": 0,
            "requests_processed": 0,
            "current_request": "Idle"
        }
        for server in SERVERS
    ]
}
def get_current_algorithm():
    with state_lock:
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("current_algorithm", "round_robin")
        except:
            return state["current_algorithm"]


def set_current_algorithm(algorithm):
    with state_lock:
        state["current_algorithm"] = algorithm

        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {
                "current_algorithm": algorithm,
                "servers": state["servers"]
            }

        data["current_algorithm"] = algorithm

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

def save_state():
    import time

    os.makedirs(DATA_DIR, exist_ok=True)

    current_algorithm = get_current_algorithm()

    public_state = {
        "current_algorithm": current_algorithm,
        "servers": state["servers"]
    }

    for _ in range(10):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(public_state, f, indent=4)
            return
        except PermissionError:
            time.sleep(0.1)

    print("[State Manager] Failed to save dashboard state due to file lock.")

def initialize_state():
    with state_lock:
        for server in state["servers"]:
            server["is_alive"] = True
            server["active_connections"] = 0
            server["requests_processed"] = 0
            server["current_request"] = "Idle"

        state["round_robin_index"] = 0
        save_state()


def get_dashboard_state():
    with state_lock:
        return {
            "current_algorithm": state["current_algorithm"],
            "servers": copy.deepcopy(state["servers"])
        }


def get_alive_servers():
    with state_lock:
        return [server for server in state["servers"] if server["is_alive"]]


def select_round_robin_server():
    with state_lock:
        alive_servers = [server for server in state["servers"] if server["is_alive"]]

        if not alive_servers:
            return None

        selected_server = alive_servers[state["round_robin_index"] % len(alive_servers)]
        state["round_robin_index"] += 1

        return selected_server


def select_least_connections_server():
    with state_lock:
        alive_servers = [server for server in state["servers"] if server["is_alive"]]

        if not alive_servers:
            return None

        min_connections = min(server["active_connections"] for server in alive_servers)

        least_loaded_servers = [
            server for server in alive_servers
            if server["active_connections"] == min_connections
        ]

        selected_server = least_loaded_servers[state["round_robin_index"] % len(least_loaded_servers)]
        state["round_robin_index"] += 1
        print("Least Connections Status:",[(s["id"], s["active_connections"]) for s in state["servers"]])

        return selected_server

def select_and_start_request(algorithm, request_data):
    with state_lock:
        alive_servers = [s for s in state["servers"] if s["is_alive"]]

        if not alive_servers:
            return None

        if algorithm == "round_robin":
            selected = alive_servers[state["round_robin_index"] % len(alive_servers)]
            state["round_robin_index"] += 1

        elif algorithm == "least_connections":
            min_conn = min(s["active_connections"] for s in alive_servers)
            least_servers = [s for s in alive_servers if s["active_connections"] == min_conn]
            selected = least_servers[state["round_robin_index"] % len(least_servers)]
            state["round_robin_index"] += 1

        else:
            return None

        selected["active_connections"] += 1
        selected["requests_processed"] += 1
        selected["current_request"] = request_data

        save_state()
        return selected.copy()
def mark_request_started(server_id, request_data):
    with state_lock:
        for server in state["servers"]:
            if server["id"] == server_id:
                server["active_connections"] += 1
                server["requests_processed"] += 1
                server["current_request"] = request_data
                break

        save_state()


def mark_request_finished(server_id):
    with state_lock:
        for server in state["servers"]:
            if server["id"] == server_id:
                server["active_connections"] = max(0, server["active_connections"] - 1)

                if server["active_connections"] == 0:
                    server["current_request"] = "Idle"
                else:
                    server["current_request"] = f"{server['active_connections']} requests processing"

                break

        save_state()


def update_server_health(server_id, is_alive):
    with state_lock:
        for server in state["servers"]:
            if server["id"] == server_id:
                previous_status = server["is_alive"]
                server["is_alive"] = is_alive

                if not is_alive:
                    server["active_connections"] = 0
                    server["current_request"] = "Down"
                elif previous_status is False:
                    server["current_request"] = "Idle"

                break

        save_state()