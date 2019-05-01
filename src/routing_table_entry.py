class RoutingTableEntry:

    def __init__(self, destination, nextHop, cost):
        self.destination = destination
        self.nextHop = nextHop
        self.cost = cost
        self.age = 0.0
        self.garbage = False

    def __str__(self):
        return "RouteTableEntry <destination={0}, nextHop={1}, cost={2}, age={3}, garbage={4}>".format(self.destination, self.nextHop, self.cost, round(self.age, 2), self.garbage)

    def __repr__(self):
        return self.__str__()
