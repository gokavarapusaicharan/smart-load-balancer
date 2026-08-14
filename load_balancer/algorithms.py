from load_balancer.state_manager import (
    select_round_robin_server,
    select_least_connections_server
)


class LoadBalancingAlgorithms:

    def round_robin(self):
        return select_round_robin_server()

    def least_connections(self):
        return select_least_connections_server()