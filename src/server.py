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


# Handles the incoming data
def handle_incoming_data(conn):
    buffer = conn.recv(1024)
    conn.send(buffer)


def handle_timer():
    print("send update message to neighbours...")


# Listens on all input ports for incoming RIP messages
def server(config):
    inputs = list(map(create_input_socket, config["input-ports"]))

    timer.init(config["periodic-timeout"], handle_timer)
    timer.start()

    rt = RoutingTable()

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, [], inputs, 1)

        # every second, we check for routes to invalidate in the routing table
        if len(readable) == 0 and len(writable) == 0 and len(exceptional) == 0:
            rt.invalidate()

        for sock in readable:
            conn, addr = sock.accept()
            handle_incoming_data(conn)
            conn.close()
            print("connected good socket", addr)

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
        "periodic-timeout": 5
    }
    server(config)
