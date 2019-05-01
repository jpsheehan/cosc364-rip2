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

        for output_port in self.config.output_ports:

            # add self to the routes
            routes = [{
                    "destination": self.config.router_id,
                    "cost": 0,
                    "next-hop": self.config.router_id
                }]
            
            if len(self.rt) == 0:
                self.log("advertising self to " + str(output_port.router_id))

            for route in self.rt:
                
                cost = route.cost
                destination = route.destination
                
                # poison reverse
                if self.rt[destination].nextHop == output_port.router_id: # and destination != output_port.router_id:
                    cost = 16
                
                if self.rt[destination].garbage:
                    cost = 16

                routes.append({
                    "destination": destination,
                    "cost": cost,
                    "next-hop": self.config.router_id
                })

            packet = protocol.Packet(output_port.cost, routes)
            sock.sendto(packet.to_data(), ('localhost', output_port.port))
    
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

        if packet.triggered:
            self.log("got a triggered updates from " + str(packet.routes[0]["destination"]))

        # self.log("got packet from " + str(packet.routes[0]["next-hop"]) + " with " + str(len(packet.routes)) + " routes")

        for route in packet.routes:

            route_destination = route["destination"]
            route_cost = route["cost"]
            route_next_hop = route["next-hop"]

            destination_entry = self.rt[route_destination]
            # next_hop_entry = self.rt[route_next_hop]

            is_destination_in_table = destination_entry is not None
            # is_next_hop_in_table = next_hop_entry is not None
            
            is_destination_unreachable = route_cost >= 16
            # is_next_hop_unreachable = packet.link_cost >= 16

            # is_destination_a_neighbor = route_next_hop == route_destination

            total_destination_cost = route_cost + packet.link_cost

            if route_destination == self.config.router_id:
                continue

            if not is_destination_in_table and not is_destination_unreachable:

                # put the destination in the table
                self.rt.add_entry(route_destination, route_next_hop, total_destination_cost)
                self.log("added new router " + str(route_destination) + " via " + str(route_next_hop) + " with a cost of " + str(total_destination_cost))
            
            elif is_destination_in_table:

                is_destination_garbage = destination_entry.garbage

                if total_destination_cost < destination_entry.cost:

                    # if not is_destination_garbage:
                    # update the cost and the hop in the table
                    self.rt.set_cost(route_destination, total_destination_cost)
                    self.rt.set_garbage(route_destination, False)
                    self.rt.set_next_hop(route_destination, route_next_hop)
                    self.log("found new route to " + str(route_destination) + " via " + str(route_next_hop) + " with a cost of " + str(total_destination_cost))
                    
                    # else:
                    #     pass
                
                elif route_next_hop == destination_entry.nextHop:
                    
                    # if is_destination_unreachable and packet.triggered:
                    #     # mark as garbage
                    #     # trigger update
                    #     self.rt.set_garbage(route_destination, True)
                    #     triggered_updates.append(destination_entry)
                    #     self.log("marked " + str(route_destination) + " as garbage 1")

                    if not is_destination_unreachable and not is_destination_garbage:
                        # keep alive
                        self.rt.reset_age(route_destination)

                    elif not is_destination_garbage:
                        # mark as garbage
                        # trigger update
                        self.rt.set_garbage(route_destination, True)
                        triggered_updates.append(destination_entry)
                        self.log("marked " + str(route_destination) + " as garbage")
                    
                    
                        
                
                # else:
                #     # hop is different and the cost is worse or equal
                #     pass

                
            
            # if not is_next_hop_in_table and not is_next_hop_unreachable:
            #     # put the next hop in the table
            #     # self.rt.add_entry()
            #     pass
            























            # if route["destination"] == self.config.router_id:
            #     # if route["next-hop"] == self.config.router_id:
            #     #     continue
            #     # self.log("swapped " + str(route["destination"]) + " and " + str(route["next-hop"]))
            #     # route["destination"] = route["next-hop"]
            #     # route["cost"] = 0
            #     continue

            # next_hop_entry = self.rt[route["next-hop"]]
            # destination_entry = self.rt[route["destination"]]

            # if next_hop_entry is None:
            #     total_cost = route["cost"] + packet.link_cost
            # else:
            #     total_cost = route["cost"] + next_hop_entry.cost
            
            # is_infinite = total_cost >= 16
            # if total_cost > 16:
            #     total_cost = 16

            # # new destination with a non-infinite cost (<16) (add)
            # # take the cost from the route plus the link cost
            # if destination_entry is None:
            #     if not is_infinite:
            #         # NEW ROUTE!
            #         self.rt.add_entry(route["destination"],
            #                           route["next-hop"], total_cost)
            #         self.log("new route for " + str(route["destination"]) + " found via " + str(route["next-hop"]) + " with a cost of " + str(total_cost))
            #     else:
            #         # self.log("new route for " + str(route["destination"]) + " via " + str(route["next-hop"]) + " is infinite, ignoring")
            #         self.log("dropped packet for new router " + str(route["destination"]))

            # else:
            #     # Known destinations

            #     # known destination but lower cost (update)
            #     # take the cost from the route plus the link cost
            #     if total_cost < destination_entry.cost:
            #         self.rt.set_cost(destination_entry.destination, total_cost)
            #         self.rt.set_garbage(destination_entry.destination, False)
            #         self.rt.set_next_hop(
            #             destination_entry.destination, route["next-hop"])
            #         self.rt.reset_age(destination_entry.destination)
            #         self.log("cheaper route for " + str(route["destination"]) + " found via " + str(route["next-hop"]) + " with a cost of " + str(total_cost))

            #     # if destination, next-hop is the same but infinite cost
            #     # set the cost in table to infinite, set garbage
            #     elif is_infinite and destination_entry.nextHop == route["next-hop"] and not destination_entry.garbage:
            #         self.rt.set_garbage(destination_entry.destination, True)
            #         triggered_updates.append(self.rt[destination_entry.destination])
            #         self.log("router " + str(destination_entry.destination) + " has been marked as garbage")
                
            #     elif is_infinite and destination_entry.nextHop == route["next-hop"] and destination_entry.garbage:
            #         # comes back online!!!
            #         self.rt.set_garbage(destination_entry.nextHop, False)
            #         self.rt.set_cost(destination_entry.nextHop, total_cost)
            #         self.log("HERE 1")
            #         # self.log("router " + str(destination_entry.destination) + " has come back online")

            #     # if destination, next-hop and non-infinite cost from route is the same as table then reset age
            #     elif destination_entry.nextHop == route["next-hop"] and not is_infinite:
            #         if total_cost == destination_entry.cost:
            #             pass
            #         self.rt.reset_age(destination_entry.destination)

            #     else:
            #         if is_infinite:
            #             self.log("infinite here ")
            #         else:
            #             self.log("finite here " + str(total_cost) + " >= " + str(destination_entry.cost))
        
        if len(triggered_updates) > 0:
            self.process_triggered_updates(triggered_updates)

        return None

    def process_triggered_updates(self, routes):
        sock = self.input_ports[0]
        for output_port in self.config.output_ports:

            packet_routes = [{
                    "destination": route.destination,
                    "cost": 16,
                    "next-hop": route.nextHop
                } for route in routes]
            
            # packet_routes.append({
            #         "destination": self.config.router_id,
            #         "cost": 0,
            #         "next-hop": self.config.router_id
            #     })

            self.log("sending triggered updates to " + str(output_port.router_id))
            p = protocol.Packet(output_port.cost, packet_routes, 1)
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
        self.periodic_timer.trigger()

        # only block for half a second at a time
        blocking_time =1.0

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
                raise Exception("SOMETHOING BAD HAPPENED")
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
