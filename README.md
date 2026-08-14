Smart Load Balancer with Health Monitoring

A Python-based load balancer that dynamically distributes client requests across multiple backend servers using Round Robin and Least Connections algorithms, with real-time server health monitoring and a Flask dashboard.

Features
Round Robin & Least Connections request routing
Health monitoring to detect and bypass unavailable servers
Concurrent request handling using Python threading
Dynamic server state tracking — health, active connections, and requests
Flask dashboard for real-time monitoring
Supports multiple backend server instances

Architecture
                    Client
                      │
                      ▼
              ┌───────────────┐
              │ Load Balancer │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Server 1    Server 2    Server 3 ... Server N
          │           │           │
          └───────────┼───────────┘
                      ▼
               Health Monitor
                      │
                      ▼
              Flask Dashboard

Tech Stack

Python · Flask · Threading · HTTP · JSON · HTML/CSS/JavaScript
