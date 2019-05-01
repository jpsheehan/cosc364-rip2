import socket
import select
import time

import timer
import routing_table
import protocol
import utils


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
        self.rt = routing_table.RoutingTable(config)
        self.config = config
        self.input_ports = []
        self.periodic_timer = None

    def print_display(self):
        """
            Displays useful information for the user.
        """

        # clear the screen
        utils.clear_terminal()

        # print info about this router
        print("RIP Router #" + str(self.config.router_id))
        print("Uptime: {0:.3} seconds".format(
            self.periodic_timer.getElapsed()))
        # print the routing table
        print(self.rt)

        # print other info
        print("Press Ctrl+C to quit")

    def process_periodic_update(self, dt):
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

    def process_triggered_updates(self, routes):
        print("Do triggered update for ", routes)

    def start(self):
        """
            Starts the server.
        """

        # set up the input ports
        self.input_ports = list(
            map(create_input_socket, self.config.input_ports))

        # start the periodic timer
        self.periodic_timer = timer.Timer(
            self.config.periodic_update, self.process_periodic_update)
        self.periodic_timer.start()

        # only block for half a second at a time
        blocking_time = 1.0

        for port in self.config.input_ports:
            print("listening on port", port)

        loop_time = time.time()

        while self.input_ports:
            readable, _writable, exceptional = select.select(
                self.input_ports, [], self.input_ports, blocking_time)

            # increment the age
            dt = time.time() - loop_time
            self.rt.increment_age(dt)

            self.periodic_timer.update()

            self.rt.update(self.process_triggered_updates)

            self.print_display()

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

            loop_time = time.time()


if __name__ == "__main__":
    import config

    c = config.Config()
    c.router_id = 11
    c.input_ports = [
        12345,
        12346,
        12347
    ]
    c.periodic_update = 5
    c.output_ports = [
        config.OutputPort(22345, 1, 12),
        config.OutputPort(22346, 1, 13)
    ]

    s = Server(c)
    s.start()
