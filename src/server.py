import socket
import select

import timer
from routing_table import RoutingTable

# Creates a TCP IPv4 socket, binds it the host and port, and begins listening


def create_input_socket(port, host='localhost'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    return sock


def create_output_socket(output_data, host='localhost'):
    port = output_data["port"]
    router_id = output_data["router-id"]
    link_cost = output_data["link-cost"]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


# Handles the incoming data
def handle_incoming_data(conn):
    buffer = conn.recv(1024)
    conn.send(buffer)


def handle_timer():
    print("send update message to neighbours...")


# Listens on all input ports for incoming RIP messages
def server(config):
    inputs = list(map(create_input_socket, config["input-ports"]))
    outputs = []

    def update_handler():
        for output in config["output-ports"]:
            outputs.append(create_output_socket(output))
            # print("Sending update to port", output["port"])

    timer.init(config["periodic-timeout"], update_handler)
    timer.start()

    rt = RoutingTable()

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs, 1)

        # every second, we check for routes to invalidate in the routing table
        if len(readable) == 0 and len(writable) == 0 and len(exceptional) == 0:
            rt.invalidate()

        for sock in readable:
            conn, addr = sock.accept()
            handle_incoming_data(conn)
            conn.close()
            print("connected good socket", addr)

        for sock in writable:
            outputs.remove(sock)
            sock.send("data".encode("utf-8"))
            # print("sent update")

        # removes a socket from the input list if it raised an error
        for sock in exceptional:
            print("connected bad socket")
            if sock in inputs:
                inputs.remove(sock)
            sock.close()


if __name__ == "__main__":
    config = {
        "input-ports": [
            12345,
            12346,
            12347
        ],
        "periodic-timeout": 5,
        "output-ports": [
            {
                "port": 22345,
                "router-id": 12,
                "link-cost": 1
            },
            {
                "port": 22346,
                "router-id": 13,
                "link-cost": 1
            }
        ]
    }
    server(config)
