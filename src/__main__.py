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
    """
        Prints the usage of the program.
    """
    print("usage: {0} <config_filename>".format(sys.argv[0]))


def print_filename_error(filename):
    """
        Prints a filename error.
    """
    print("Error: {0} doesn't exist.".format(filename))


def print_config_error():
    """
        Prints a configuration file error.
    """
    print("Error: Couldn't read the configuration file.")


def main():
    """
        The main entry point to the program.
    """

    if len(sys.argv) != 2:
        print_usage()
        return -1

    filename = sys.argv[1]
    file = None
    conf = None

    # accepts config from stdin
    if filename == '--':
        file = sys.stdin
    
    # or from a file
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
        
    except:
        print_config_error()
        return -1

    try:
        print("Starting RIP router #" + str(conf.router_id))
        s = server.Server(conf)
        s.start()

    # Ignore KeyboardInterrupts
    except KeyboardInterrupt:
        pass

    # Re-raise other exceptions
    except Exception as err:
        raise err


if __name__ == "__main__":
    main()
