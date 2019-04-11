#!/usr/bin/python3
import os
import sys


def get_network_name():
    network_name = None
    while network_name is None:
        try:
            network_name = input("Enter network name: ")
            network_name = network_name.strip()
            if not network_name.isalnum():
                print("Network name must be alpha-numeric")
                network_name = None
        except:
            print("ASD")
            return None
    return network_name


def get_router_ids():
    router_ids = []
    while len(router_ids) == 0:
        try:
            line = input("Enter router ids seperated by spaces: ")
            router_ids = [id for id in line.strip().split(" ")]
            is_valid = True
            for id in router_ids:
                if not id.isalnum():
                    is_valid = False
                    break

            if not is_valid:
                print("All ids must be alpha-numeric")
                router_ids = None
        except:
            return None
    return router_ids


def get_link_cost(fromId, toId):
    link_cost = None
    while link_cost is None:
        try:
            line = input("Enter link cost between routers '" +
                         str(fromId) + "' and '" + str(toId) + "': ")
            line = line.strip()
            if not line.isnumeric() or int(line) < 0:
                print("Link cost must be a positive integer (or 0 for infinity)")
            else:
                link_cost = int(line)
        except Exception as e:
            print(e)
            return None
    return link_cost


def main():
    network_name = get_network_name()
    if network_name is None:
        return

    router_ids = get_router_ids()
    if router_ids is None:
        return

    configs = {}
    port_number_max = 55500
    for index, fromId in enumerate(router_ids):
        for toId in router_ids[index + 1:]:
            link_cost = get_link_cost(fromId, toId)
            if link_cost is None:
                return

            if link_cost == 0:
                continue

            to_port_number = port_number_max
            port_number_max += 1
            from_port_number = port_number_max
            port_number_max += 1

            if fromId not in configs:
                configs[fromId] = {"output-ports": [],
                                   "input-ports": [], "router-id": fromId}
            configs[fromId]["output-ports"].append(
                (to_port_number, link_cost, toId))
            configs[fromId]["input-ports"].append(from_port_number)

            if toId not in configs:
                configs[toId] = {"output-ports": [],
                                 "input-ports": [], "router-id": toId}
            configs[toId]["output-ports"].append(
                (from_port_number, link_cost, fromId))
            configs[toId]["input-ports"].append(to_port_number)

    # assign port numbers
    root_path = os.path.join("configs", "networks", network_name)
    if not os.path.exists(root_path):
        os.mkdir(root_path)
        print("Created directory", root_path)

    for key in configs:
        config = configs[key]
        filename = os.path.join(root_path, config["router-id"] + ".conf")
        with open(filename, "w") as f:
            f.write("; " + filename + "\n")
            f.write("; created with tools/generate_network.py\n")
            f.write("\n")
            f.write("[DEFAULT]")
            f.write("router-id " + str(config["router-id"]) + "\n")
            f.write("input-ports " + ", ".join([str(x)
                                                for x in config["input-ports"]]) + "\n")
            f.write("output-ports " + ", ".join([str(x[0]) + "-" + str(x[1]) + "-" + str(x[2])
                                                 for x in config["output-ports"]]) + "\n")
            f.write("\n")
            print("Created", filename)

    # print("Creating ", network_name, "with", configs)


if __name__ == "__main__":
    main()
