import os
from routing_table_entry import RoutingTableEntry


class RoutingTable:

    def __init__(self):
        self.__routes = []

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
                
    def increment_age(self, routerID, time):
        index = self.get_index(routerID)
        self.__routes[index].age += time
        
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
            s.append("| {0:<10} | {1:<10} | {2:<10} | {3:<10} | {4:<10} |".format(
                route.destination, route.nextHop, route.cost, route.age, route.garbage))
        s.append("+------------+------------+------------+------------+------------+")
        return os.linesep.join(s)

if __name__ == "__main__":
    r = RoutingTable()
    r.add_entry(1, 2, 3)
    r.add_entry(4, 5, 6)
    print(r)
    #r.increment_age(1,1)
    #r.set_garbage(1, True)
    #r.increment_age(4,1)
    #print(r)
    #r.reset_age(1)
    #print(r)
    #print(r)
    #r.delete_entry(4)
    #print(r)
    #r.set_cost(1,5)
    #print(r)
    #r.set_next_hop(1,7)
    #print(r)
