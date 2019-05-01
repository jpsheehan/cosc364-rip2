import socket
import select

import timer
import routing_table
import protocol


# Creates a UDP IPv4 socket and binds it the host and port
def create_input_socket(port, host='localhost'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    return sock


class Server:

    def __init__(self, config):
        """
            Creates a new server with a configuration.
        """
        self.rt = routing_table.RoutingTable()
        self.config = config
        self.input_ports = []
        self.periodic_timer = None

    def process_periodic_update(self):
        """
            Called when the periodic timer is triggered.
        """
        print("periodic update")

    def process_incoming_data(self, addr, data):
        """
            Called when incoming data is received. The data returned from this function is sent back through the socket. If None is returned, nothing will be sent.
        """
        print("recieved:", data)
        return "thanks!"

    def start(self):
        """
            Starts the server.
        """

        # set up the input ports
        self.input_ports = list(
            map(create_input_socket, self.config["input-ports"]))

        # start the periodic timer
        self.periodic_timer = timer.Timer(1, self.process_periodic_update)
        self.periodic_timer.start()

        # only block for half a second at a time
        blocking_time = 0.5

        while self.input_ports:
            readable, _writable, exceptional = select.select(
                self.input_ports, [], self.input_ports, blocking_time)

            self.periodic_timer.update()

            # iterate through all sockets that have data waiting on them
            for sock in readable:
                data, addr = sock.recvfrom(4096)
                resp = self.process_incoming_data(addr, protocol.decode(data))

                if resp is not None:
                    sock.sendto(protocol.encode(resp), addr)

            # removes a socket from the input list if it raised an error
            for sock in exceptional:
                print("connected bad socket")
                if sock in self.input_ports:
                    self.input_ports.remove(sock)
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
    s = Server(config)
    s.start()
