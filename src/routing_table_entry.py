class RoutingTableEntry:
    
    def __init__(self, destination, nextHop, cost):
        self.destination = destination
        self.nextHop = nextHop
        self.cost = cost
        self.age = 0
        self.garbage = False
        
    