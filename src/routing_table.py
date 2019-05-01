import os


class RoutingTable:

    def __init__(self):
        self.__routes = []

    def add_entry(self, route):
        self.__routes.append(route)

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
                route["router_id"], route["next_hop"], route["cost"], route["age"], route["garbage"]))
        s.append("+------------+------------+------------+------------+------------+")
        return os.linesep.join(s)


if __name__ == "__main__":
    r = RoutingTable()
    r.add_entry({
        "router_id": "A",
        "next_hop": "B",
        "cost": 7,
        "age": 30,
        "garbage": False
    })
    print(r)
