#!/usr/bin/python3

"""

    __main__.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""

import sys
import os.path

import server
import config


def print_usage():
    print("TODO: usage")


def print_filename_error(filename):
    print("TODO: filename error")


def print_config_error(err):
    print("TODO: config error", err)


def main():

    if len(sys.argv) != 2:
        print_usage()
        return -1

    filename = sys.argv[1]
    file = None
    conf = None

    if filename == '--':
        file = sys.stdin
    else:
        if not os.path.exists(filename):
            print_filename_error(filename)
            return -1
        else:
            file = open(filename, "r")

    try:
        print("Reading configuration file... ", end='')
        conf = config.Config()
        conf.parse_file(file)
        print("done!")

        print("Starting RIP router #" + str(conf.router_id))
        s = server.Server(conf)
        s.start()

    except Exception as err:
        raise err


if __name__ == "__main__":
    main()
