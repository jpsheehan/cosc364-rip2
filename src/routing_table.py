#!/usr/bin/python3

"""

    routing_table.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""


import os
from routing_table_entry import RoutingTableEntry
import config


class RoutingTable:
    """
        The RoutingTable represents the list of RoutingTableEntries for a router.
    """

    def __init__(self, config, logging_function = None):
        """
            Creates a new RoutingTable based on the Config.
        """
        self.__routes = []
        self.routerID = config.router_id
        self.__logging_function = logging_function

    def add_entry(self, destination, nextHop, totalCost):
        """
            Adds a new RoutingTableEntry to the RoutingTable.
        """
        route = RoutingTableEntry(destination, nextHop, totalCost)
        self.__routes.append(route)

    def set_garbage(self, routerID, isGarbage):
        """
            Sets the garbage flag of the entry.
        """
        index = self.get_index(routerID)
        self.__routes[index].garbage = isGarbage
        self.reset_age(routerID)
        if isGarbage:
            self.set_cost(routerID, 16)
    
    def log(self, message):
        if self.__logging_function is not None:
            self.__logging_function(message)
        else:
            print(message)
    
    def reset_age(self, routerID):
        """
            Resets the age of the entry to 0.
        """
        index = self.get_index(routerID)
        self.__routes[index].age = 0.0

    def increment_age(self, time):
        """
            Increments the age of all entries in the RoutingTable.
        """
        for entry in self.__routes:
            if entry.destination != self.routerID:
                entry.age += time

    def delete_entry(self, routerID):
        """
            Deletes an entry with the specific routerID from the RoutingTable.
        """
        index = self.get_index(routerID)
        del self.__routes[index]

    def get_index(self, routerID):
        """
            Gets the index of the entry with the routerID. Returns -1 if not found.
        """
        for i, route in enumerate(self.__routes):
            if route.destination == routerID:
                return i
        return -1  # Not found

    def set_cost(self, routerID, cost):
        """
            Sets the cost of the entry.
        """
        index = self.get_index(routerID)
        self.__routes[index].cost = cost

    def set_next_hop(self, routerID, nextHop):
        """
            Sets the next hop of the entry.
        """
        index = self.get_index(routerID)
        self.__routes[index].nextHop = nextHop

    def update(self, triggered_update_callback):
        """
            Performs house-keeping on the entries.
            The `triggered_update_callback` is for performing triggered updates.
        """
        remove_routes = []
        triggered_routes = []

        for route in self.__routes:
            if route.age > 10 and not route.garbage:
                self.log("marked router " + str(route.destination) + " as garbage")
                self.set_garbage(route.destination, True)
                triggered_routes.append(route)

            if route.age > 20 and route.garbage:
                self.log("purged router " + str(route.destination) + " from database")
                remove_routes.append(route)

        if len(triggered_routes) != 0:
            triggered_update_callback(triggered_routes)

        for route in remove_routes:
            self.__routes.remove(route)

    def __getitem__(self, routerId):
        """
            Gets the entry with the given routerId.
        """
        index = self.get_index(routerId)
        if index != -1:
            return self.__routes[index]
        return None

    def __iter__(self):
        """
            Returns the iterator of the routes.
        """
        return iter(self.__routes)

    def __len__(self):
        """
            Returns the number of routes this RoutingTable has.
        """
        return len(self.__routes)

    def __str__(self):
        """
            Returns a human-readable RoutingTable that can be printed to the terminal.
        """
        s = [
            "+------------+------------+------------+------------+------------+",
            "| Dest.      | Next Hop   | Total Cost | Age        | Garbage?   |",
            "+------------+------------+------------+------------+------------+"
        ]
        for route in self.__routes:
            s.append("| {0:<10} | {1:<10} | {2:<10} | {3:<10} | {4:<10} |".format(
                route.destination, route.nextHop, route.cost, round(route.age, 2), route.garbage))
        s.append("+------------+------------+------------+------------+------------+")
        return os.linesep.join(s)
