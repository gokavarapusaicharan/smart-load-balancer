HOST = "127.0.0.1"
LOAD_BALANCER_PORT = 9000
BUFFER_SIZE = 4096

HEALTH_CHECK_INTERVAL = 3
SERVER_TIMEOUT = 3

# choose: "round_robin" or "least_connections"
ALGORITHM = "least_connections"

SERVERS = [
    {"id": 1, "host": "127.0.0.1", "port": 8001},
    {"id": 2, "host": "127.0.0.1", "port": 8002},
    {"id": 3, "host": "127.0.0.1", "port": 8003},
    {"id": 4, "host": "127.0.0.1", "port": 8004},
]