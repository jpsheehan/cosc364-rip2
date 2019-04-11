import socket
import select
import signal

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


def handle_timer(signum, frame):
    print("cool beans", signum)
    start_timer()


def start_timer():
    signal.signal(signal.SIGALRM, handle_timer)
    signal.alarm(5)

# Listens on all input ports for incoming RIP messages


def server(config):
    inputs = list(map(create_input_socket, config["input-ports"]))

    start_timer()

    while inputs:
        readable, _writable, exceptional = select.select(
            inputs, [], inputs)

        # if len(readable) == 0 and len(writable) == 0 and len(exceptional) == 0:
        #     print("timeout yo!")

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
