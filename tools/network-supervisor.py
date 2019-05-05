#!/usr/bin/network-supervisor

import sys
import os
import os.path
import subprocess

DEFAULT_ROOT = "./configs/networks/"
__VERSION__ = "0.1"


STARTED_ROUTERS = {}


def get_network_list(root):
    return os.listdir(root)


def get_router_list(network, root):
    return os.listdir(os.path.join(root, network))


def start_router(router, network, root):
    global STARTED_ROUTERS
    if network not in STARTED_ROUTERS:
        STARTED_ROUTERS[network] = {}

    if router not in STARTED_ROUTERS[network]:
        STARTED_ROUTERS[network][router] = get_subprocess(
            root, network, router)


def stop_router(router, network, root):
    global STARTED_ROUTERS
    if network not in STARTED_ROUTERS:
        STARTED_ROUTERS[network] = {}

    if router in STARTED_ROUTERS[network]:
        STARTED_ROUTERS[network][router].terminate()
        del STARTED_ROUTERS[network][router]


def start_all_routers(network, root):
    for router in get_router_list(network, root):
        start_router(router, network, root)


def stop_all_routers(network, root):
    for router in get_router_list(network, root):
        stop_router(router, network, root)


def get_is_router_started(network, router):
    global STARTED_ROUTERS
    if network not in STARTED_ROUTERS:
        return False

    if router not in STARTED_ROUTERS[network]:
        return False

    return True


def get_valid_input(range_min, range_max, other_options, prompt="> "):
    valid_options = []
    valid_options.extend([c.upper() for c in other_options])
    valid_options.extend([str(i) for i in range(range_min, range_max + 1)])
    choice = input(prompt).upper()
    while choice not in valid_options:
        choice = input(prompt).upper()
    return choice


def print_menu(list_items, tuple_items, prompt="> "):
    for i, item in enumerate(list_items):
        print("{0:>3}: {1}".format(i + 1, item))
    for k, v in tuple_items:
        print("{0:>3}: {1}".format(k, v))
    choice = get_valid_input(1, len(list_items), [k for k, _v in tuple_items])
    return choice


def get_subprocess(root, network, router):
    fullpath = os.path.abspath(os.path.join(root, network, router))

    if os.name == "posix":
        return subprocess.Popen("gnome-terminal --title \"Router {0}\" --window -e \"bash -c \\\"python3 src {1}\\\"\"")

    elif os.name == "nt":
        return subprocess.Popen("start \"Router {0}\" cmd /K python src {1}".format(router, fullpath), shell=True)

    else:
        return "echo \"unsupported system\""


def clear_terminal():
    # the terminal clear command for linux
    if os.name == "posix":
        os.system("clear")

    # the console cls command for windows
    elif os.name == "nt":
        os.system("cls")

    # otherwise, just print 25 newlines
    else:
        for _ in range(25):
            print("")


def main(root):
    if not os.path.exists(root) or not os.path.isdir(root):
        print("error: '{0}' must be an existing directory".format(root))
        return

    quit = False
    state = 0
    choice = None
    selected_network = None
    selected_router = None
    infoMessage = None

    while not quit:
        clear_terminal()
        print_version()
        print("")

        if infoMessage is not None:
            print("***INFO***:", infoMessage, "\n")

        if state == 0:
            print("Networks List:")
            network_list = get_network_list(root)
            if len(network_list) > 0:
                choice = print_menu(
                    network_list, [("R", "Refresh List"), ("Q", "Quit")])
                if choice == 'Q':
                    quit = True
                elif choice == 'R':
                    pass
                else:
                    selected_network = network_list[int(choice) - 1]
                    state = 1
            else:
                choice = print_menu([], [("R", "Refresh List"), ("Q", "Quit")])
                if choice == 'Q':
                    quit = True
                else:
                    pass
        elif state == 1:
            print("Routers in {0}:".format(selected_network))
            router_list = get_router_list(selected_network, root)
            display_list = ["{0}{1}".format(r, " (STARTED)" if get_is_router_started(
                selected_network, r) else "") for r in router_list]
            if len(router_list) > 0:
                choice = print_menu(
                    display_list, [("A", "All Routers"), ("R", "Refresh List"), ("B", "Back to Networks")])
                if choice == 'R':
                    pass
                elif choice == 'B':
                    if len(STARTED_ROUTERS[selected_network]) > 0:
                        infoMessage = "You must stop all routers!"
                    else:
                        state = 0
                        infoMessage = None
                elif choice == "A":
                    state = 3
                else:
                    selected_router = router_list[int(choice) - 1]
                    state = 2
            else:
                choice = print_menu(
                    [], [("R", "Refresh List"), ("B", "Back to Networks")])
                if choice == 'R':
                    pass
                elif choice == 'B':
                    state = 0
        elif state == 2:
            status = "STOPPED"
            if get_is_router_started(selected_network, selected_router):
                status = "STARTED"
            print("Router {0} ({1}):\n".format(selected_router, status))
            choice = print_menu([], [("U", "Bring Router Up"),
                                     ("D", "Bring Router Down"), ("B", "Back to Router List")])
            if choice == 'U':
                if not get_is_router_started(selected_network, selected_router):
                    start_router(
                        selected_router, selected_network, root)
                    infoMessage = "Started router {0}".format(selected_router)
                else:
                    infoMessage = "Router {0} is already started!".format(
                        selected_router)
            elif choice == 'D':
                if not get_is_router_started(selected_network, selected_router):
                    infoMessage = "Router {0} has not been started!".format(
                        selected_router)
                else:
                    stop_router(selected_router, selected_network, root)
                    infoMessage = "Stopped router {0}".format(selected_router)
            else:
                infoMessage = None
                state = 1


def print_version():
    print("network-supervisor.py v{0}".format(__VERSION__))


def print_usage():
    print("usage: {0} [network folder]".format(sys.argv[0]))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 1:
        main(DEFAULT_ROOT)
    else:
        print_version()
        print_usage()
