import os
from routing_table_entry import RoutingTableEntry
import config


class RoutingTable:

    def __init__(self, config):
        self.__routes = []
        self.routerID = config.router_id
        for route in config.output_ports:
            self.add_entry(route.router_id, route.port, route.cost)

    def add_entry(self, destination, nextHop, totalCost):
        route = RoutingTableEntry(destination, nextHop, totalCost)
        self.__routes.append(route)

    def set_garbage(self, routerID, isGarbage):
        index = self.get_index(routerID)
        self.__routes[index].garbage = isGarbage
        self.reset_age(routerID)

    def reset_age(self, routerID):
        index = self.get_index(routerID)
        self.__routes[index].age = 0

    def increment_age(self, time):
        for entry in self.__routes:
            entry.age += time

    def delete_entry(self, routerID):
        index = self.get_index(routerID)
        del self.__routes[index]

    def get_index(self, routerID):
        for i, route in enumerate(self.__routes):
            if route.destination == routerID:
                return i
        return -1  # Not found

    def set_cost(self, routerID, cost):
        index = self.get_index(routerID)
        self.__routes[index].cost = cost

    def set_next_hop(self, routerID, nextHop):
        index = self.get_index(routerID)
        self.__routes[index].nextHop = nextHop

    def invalidate(self):
        pass

    def __str__(self):
        s = [
            "+------------+------------+------------+------------+------------+",
            "| Dest.      | Next Hop   | Total Cost | Age        | Garbage?   |",
            "+------------+------------+------------+------------+------------+"
        ]
        for route in self.__routes:
            s.append("| {0:<10} | {1:<10} | {2:<10} | {3:<10.4} | {4:<10} |".format(
                route.destination, route.nextHop, route.cost, route.age, route.garbage))
        s.append("+------------+------------+------------+------------+------------+")
        return os.linesep.join(s)


if __name__ == "__main__":
    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.split(current_directory)[0]
    file_path = os.path.join(parent_directory, 'configs/good/01.conf')
    config = config.open_config_file(file_path)
    r = RoutingTable(config)
    print(r)
