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
        self.rt = routing_table.RoutingTable(config, self.log)
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
            
            # if len(self.rt) == 0:
            #     self.log("advertising self to " + str(output_port.router_id))

            for route in self.rt:
                
                cost = route.cost
                destination = route.destination
                
                # poison reverse by setting cost to 16 when announcing routes back from where they were learned
                if self.rt[destination].nextHop == output_port.router_id:
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

        for route in packet.routes:

            route_destination = route["destination"]
            route_cost = route["cost"]
            route_next_hop = route["next-hop"]

            destination_entry = self.rt[route_destination]

            """ Check route is valid before any processing is done"""
            # route lists ourself as the destination (useless) or as the next hop (invalid) and should be dropped
            if route_destination == self.config.router_id or route_next_hop == self.config.router_id:
                continue
            
            # route contains a negative cost and should be dropped 
            if (route_cost < 0) or (packet.link_cost < 0):
                continue

            """ route is valid and should be processed"""

            # total cost is the link cost added to the cost contained in the packet
            total_destination_cost = route_cost + packet.link_cost

            is_destination_unreachable = (total_destination_cost >= 16)

            # clamp cost to maximum of 16
            if is_destination_unreachable:
                total_destination_cost = 16

            # is the destination routerID knonwn
            is_destination_in_table = destination_entry is not None
            
            # New valid route
            if not is_destination_in_table and not is_destination_unreachable:

                # put the destination in the table
                self.rt.add_entry(route_destination, route_next_hop, total_destination_cost)
                self.log("added new router " + str(route_destination) + " via " + str(route_next_hop) + " with a cost of " + str(total_destination_cost))
            
            # Route already exists in table
            elif is_destination_in_table:

                is_destination_garbage = destination_entry.garbage

                # Check for a better route.
                if total_destination_cost < destination_entry.cost:
                    self.rt.set_cost(route_destination, total_destination_cost)
                    self.rt.set_garbage(route_destination, False)
                    self.rt.set_next_hop(route_destination, route_next_hop)

                    self.log("found new route to " + str(route_destination) + " via " + str(route_next_hop) + " with a cost of " + str(total_destination_cost))

                # Check for worse route from the same hop
                elif route_next_hop == destination_entry.nextHop and total_destination_cost > destination_entry.cost:
                    if is_destination_unreachable:
                        # garbage it if we haven't seen it before, otherwise ignore it
                        if not is_destination_garbage:
                            self.rt.set_garbage(route_destination, True)
                            triggered_updates.append(destination_entry)
                            self.log("processed a triggered update from " + str(packet.routes[0]["next-hop"]) + " marked " + str(route_destination) + " as garbage")
                    
                    # We got a worse route from the samehop but its not infinite. As a neighbour we MUST update to the higher cost.
                    else:
                        self.rt.set_cost(route_destination, total_destination_cost)
                        self.rt.reset_age(route_destination)

                # Check for worse route from a different hop and ignore it
                elif total_destination_cost > destination_entry.cost:
                    #self.log("Worse route to " + str(route_destination) + " ignoring it")
                    continue

                # Check for same route and keep it alive
                elif route_next_hop == destination_entry.nextHop and total_destination_cost == destination_entry.cost:
                    # We dont want to keep alive infinite weight routes
                    if not is_destination_garbage:
                        self.rt.reset_age(route_destination)

        if len(triggered_updates) > 0:
            self.log("sending triggered updates")
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
                    "next-hop": self.config.router_id
                } for route in routes]

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

        # only block for a second at a time
        blocking_time =1

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

if __name__ == "__main__":
    pass
