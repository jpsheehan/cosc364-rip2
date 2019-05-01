import socket
import select
import time

import timer
import routing_table
import routing_table_entry
import protocol
import utils
import bencode


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
        self.loglines = []

    def print_display(self):
        """
            Displays useful information for the user.
        """

        # clear the screen
        utils.clear_terminal()

        # print info about this router
        print("RIP Router #" + str(self.config.router_id))
        print("Uptime: {0} seconds".format(
            round(self.periodic_timer.getElapsed())))

        # print the routing table
        print(self.rt)

        # print other info
        print("Press Ctrl+C to quit")

    def process_periodic_update(self, dt):
        """
            Called when the periodic timer is triggered.
        """
        # send destination, next hop and total cost of each routing entry to each input port
        sock = self.input_ports[0]

        for outport in self.config.output_ports:

            # add self to the routes
            routes = [{
                    "destination": self.config.router_id,
                    "cost": 0,
                    "next-hop": self.config.router_id
                }]

            for route in self.rt:
                
                cost = route.cost
                destination = route.destination
                
                if self.rt[destination].nextHop == outport.router_id:
                    cost = 16

                routes.append({
                    "destination": destination,
                    "cost": cost,
                    "next-hop": self.config.router_id
                })

            packet = protocol.Packet(outport.cost, routes)
            sock.sendto(packet.to_data(), ('localhost', outport.port))
    
    def log(self, message):
        self.loglines.append(message)
        while len(self.loglines) > 10:
            self.loglines = self.loglines[1:]

    def process_incoming_data(self, addr, data):
        """
            Called when incoming data is received. The data returned from this function is sent back through the socket. If None is returned, nothing will be sent.
        """

        triggered_updates = []
        packet = protocol.Packet()
        packet.from_data(data)

        for route in packet.routes:

            if route["destination"] == self.config.router_id:
                continue

            next_hop_route = self.rt[route["next-hop"]]
            table_entry = self.rt[route["destination"]]

            # if self.config.router_id == 3 and route["destination"] == 4 or self.config.router_id == 4 and route["destination"] == 3:
            #     self.log("link_cost: " + str(packet.link_cost))
            #     self.log("route: " + str(route))

            if next_hop_route is None:
                total_cost = route["cost"] + packet.link_cost
            else:
                total_cost = route["cost"] + next_hop_route.cost
            
            is_infinite = total_cost >= 16

            # new destination with a non-infinite cost (<16) (add)
            # take the cost from the route plus the link cost
            if table_entry is None:
                if not is_infinite:
                    # NEW ROUTE!
                    self.rt.add_entry(route["destination"],
                                      route["next-hop"], total_cost)
                    self.log("new route for " + str(route["destination"]) + " found via " + str(route["next-hop"]) + " with a cost of " + str(total_cost))
                else:
                    self.log("new route for " + str(route["destination"]) + " via " + str(route["next-hop"]) + " is infinite, ignoring")

            else:
                # Known destinations

                # known destination but lower cost (update)
                # take the cost from the route plus the link cost
                if total_cost < table_entry.cost:
                    self.rt.set_cost(table_entry.destination, total_cost)
                    self.rt.set_garbage(table_entry.destination, False)
                    self.rt.set_next_hop(
                        table_entry.destination, route["next-hop"])
                    self.rt.reset_age(table_entry.destination)
                    self.log("cheaper route for " + str(route["destination"]) + " found via " + str(route["next-hop"]) + " with a cost of " + str(total_cost))

                # if destination, next-hop is the same but infinite cost
                # set the cost in table to infinite, set garbage
                elif is_infinite and table_entry.nextHop == route["next-hop"] and not table_entry.garbage:
                    self.rt.set_garbage(table_entry.destination, True)
                    triggered_updates.append(self.rt[table_entry.destination])
                    self.log("router " + str(table_entry.destination) + " has been marked as garbage")
                
                elif is_infinite and table_entry.nextHop == route["next-hop"] and table_entry.garbage:
                    # comes back online!!!
                    self.rt.set_garbage(table_entry.nextHop, False)
                    self.rt.set_cost(table_entry.nextHop, packet.link_cost)
                    self.log("router " + str(table_entry.destination) + " has come back online")

                # if destination, next-hop and non-infinite cost from route is the same as table then reset age
                elif table_entry.nextHop == route["next-hop"] and not is_infinite:
                    self.rt.reset_age(table_entry.destination)

                else:
                    pass
        
        if len(triggered_updates) > 0:
            self.process_triggered_updates(triggered_updates)

        return None

    def process_triggered_updates(self, routes):
        sock = self.input_ports[0]
        for output_port in self.config.output_ports:

            packet_routes = [{
                    "destination": route.destination,
                    "cost": 16,
                    "next-hop": self.config.router_id
                } for route in routes]
            
            packet_routes.append({
                    "destination": self.config.router_id,
                    "cost": 0,
                    "next-hop": self.config.router_id
                })

            p = protocol.Packet(output_port.cost, packet_routes)
            sock.sendto(p.to_data(), ('localhost', output_port.port))

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
        blocking_time = 0.1

        loop_time = time.time()

        while self.input_ports:
            readable, _writable, exceptional = select.select(
                self.input_ports, [], self.input_ports, blocking_time)

            # increment the age
            dt = time.time() - loop_time
            self.rt.increment_age(dt)

            self.print_display()

            self.periodic_timer.update()

            self.rt.update(self.process_triggered_updates)

            print("")
            print("Information Log:")
            for line in self.loglines:
                print(" ", line)

            # iterate through all sockets that have data waiting on them
            for sock in readable:
                data, addr = sock.recvfrom(4096)
                resp = self.process_incoming_data(addr, data)

                if resp is not None:
                    sock.sendto(resp, addr)

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
    c.output_ports = [
        config.OutputPort(22345, 1, 12),
        config.OutputPort(22346, 1, 13)
    ]

    s = Server(c)
    s.start()
