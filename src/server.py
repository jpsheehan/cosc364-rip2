#!/usr/bin/python3

"""

    server.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""

import socket
import select
import time

import timer
import routing_table
import routing_table_entry
import protocol
import utils
import bencode


def create_input_socket(port, host='localhost'):
    """
        Creates a new UDP socket.
    """
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
        """
            Writes to the information log (for a maximum of 10 lines).
        """
        self.loglines.append(message)
        while len(self.loglines) > 10:
            self.loglines = self.loglines[1:]

    def process_incoming_data(self, addr, data):
        """
            Called when incoming data is received. The data returned from this function is sent back through the socket. If None is returned, nothing will be sent.
        """

        triggered_updates = []
        packet = protocol.Packet()
        
        if not packet.from_data(data):
            self.log("invalid packet hash")
            return

        if packet.triggered:
            self.log("got a triggered updates from " + str(packet.routes[0]["next-hop"]))

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
                # Flood triggered update. If we are using that route then also begin garbage collection. 
                if packet.triggered and not is_destination_garbage:
                    self.rt.set_garbage(route_destination, True)
                    triggered_updates.append(destination_entry)
                    self.log("marked " + str(route_destination) + " as garbage")


                if total_destination_cost < destination_entry.cost:

                    # if not is_destination_garbage:
                    # update the cost and the hop in the table
                    self.rt.set_cost(route_destination, total_destination_cost)
                    self.rt.set_garbage(route_destination, False)
                    self.rt.set_next_hop(route_destination, route_next_hop)
                    self.log("found new route to " + str(route_destination) + " via " + str(route_next_hop) + " with a cost of " + str(total_destination_cost))
                
                elif route_next_hop == destination_entry.nextHop:

                    if not is_destination_unreachable and not is_destination_garbage:
                        # keep alive
                        self.rt.reset_age(route_destination)

                    elif not is_destination_garbage:
                        # mark as garbage
                        # trigger update
                        self.rt.set_garbage(route_destination, True)
                        triggered_updates.append(destination_entry)
                        self.log("marked " + str(route_destination) + " as garbage")
        
        if len(triggered_updates) > 0:
            self.process_triggered_updates(triggered_updates)

        return None

    def process_triggered_updates(self, routes):
        """
            Processes the triggered updates.
        """
        sock = self.input_ports[0]
        for output_port in self.config.output_ports:

            packet_routes = [{
                    "destination": route.destination,
                    "cost": 16,
                    "next-hop": route.nextHop
                } for route in routes]

            self.log("sending triggered updates to " + str(output_port.router_id))
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

            # redisplay the screen
            self.print_display()

            # update the timer, may call process_periodic_update
            self.periodic_timer.update()

            # may call process_triggered_updates
            self.rt.update(self.process_triggered_updates)

            # display the information log
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
                if sock in self.input_ports:
                    self.input_ports.remove(sock)
                    sock.close()
                raise Exception("A socket raised an error")
            
            # update the loop time
            loop_time = time.time()

# some tests:
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
