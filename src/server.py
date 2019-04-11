import socket
import select

# Creates a TCP IPv4 socket, binds it the host and port, and begins listening


def create_socket(port, host='localhost'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    return sock


# Listens on all input ports for incoming RIP messages
def server(config):
    inputs = list(map(create_socket, config["input-ports"]))

    while inputs:
        readable, _, exceptional = select.select(
            inputs, [], inputs)

        for sock in readable:
            conn, addr = sock.accept()
            conn.close()
            print("connected good socket", addr)

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
        ]
    }
    server(config)
