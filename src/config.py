#!/usr/bin/python3

"""

    config.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""

import configparser
import os
import random


class Config:

    def __init__(self):
        self.router_id = 0
        self.input_ports = []
        self.output_ports = []
        self.periodic_update = 0

    def parse_file(self, file):
        c = read_config_file(file)
        self.router_id = c["routerId"]
        self.input_ports = c["inputPorts"]
        self.output_ports = [
            OutputPort(o["outputPort"], o["cost"], o["routerId"]) for o in c["outputPorts"]
        ]
        self.periodic_update = c["periodicUpdate"]

    def __str__(self):
        return "Config <id={0}, input_ports={1}, output_ports={2}, periodic_update={3:.3}s>".format(self.router_id, self.input_ports, self.output_ports, self.periodic_update)

    def __repr__(self):
        return self.__str__()


class OutputPort:
    def __init__(self, port, cost, id):
        self.router_id = id
        self.port = port
        self.cost = cost

    def __str__(self):
        return "OutputPort <id={0}, port={1}, cost={2}>".format(self.router_id, self.port, self.cost)

    def __repr__(self):
        return self.__str__()


def read_config_file(file):
    """
    Parses a given file and returns a dict containing the routerID, input ports
    and output ports with their cost and next hop
    """
    #Create an instance of configparser object
    config = configparser.ConfigParser()
    config.read_file(file)
    # dict declartion
    router = {}
    # Reading in each section of the config
    routerId = (config.get('DEFAULT', 'router-id'))
    inputPorts = (config.get('DEFAULT', 'input-ports'))
    outputPorts = (config.get('DEFAULT', 'output-ports'))
    # Checks config file for periodic timer override or defaults to standard
    periodicUpdate = config.get("DEFAULT", "periodic-update", fallback=3.0)

    # Validating all parameters
    router["routerId"] = check_router_id(routerId)
    router["inputPorts"] = check_input_ports(inputPorts)
    router["outputPorts"] = check_output_ports(router, outputPorts)
    router["periodicUpdate"] = check_periodic_update(periodicUpdate)

    return router


def check_periodic_update(periodicUpdate):
    """
    Reduces the chance of collisons and other nasties by implementing a random wait to the periodicUpdate
    """
    return periodicUpdate + (random.random() * 2 - 1)


def check_router_id(routerId):
    """
    Takes a routerID string from the config and checks it
    Returns it back as an int if its valid
    """
    try:
        routerId = int(routerId)
    except:
        raise TypeError("RouterID must be an integer")
    if (routerId > 64000 or routerId < 1):
        raise ValueError("RouterID must be between 1 and 64000")
    return routerId


def check_input_ports(inputPorts):
    """
    Takes a string of inputports from the config
    Validates and then returns them as a list
    """
    try:
        inputPorts = [int(port.strip()) for port in inputPorts.split(',')]
    except:
        raise TypeError("Input ports should be comma seperated ints")
    for port in inputPorts:
        if (port > 64000 or port < 1024):
            raise ValueError("Port should be between 1024 and 64000")
    if len(inputPorts) != len(set(inputPorts)):
        raise ValueError("Ports should be unique")
    return inputPorts


def check_output_ports(router, outputPorts):

    """
    Takes an incomplete router dict containing a routerID and input ports
    Tests the routerID and input ports against a list of outputPorts
    Returns a list of outputPorts if they are all valid.

    """
    outportPortList = []
    try:
        outputPorts = [port.strip() for port in outputPorts.split(',')]
    except:
        raise TypeError(
            "Outport ports should be comma seperated in the form PORT-COST-ID")
    for output in outputPorts:
        config = {}
        output = output.split('-')
        output = [int(i) for i in output]
        config["cost"] = output[1]

        if (output[0] > 64000 or output[0] < 1024):
            raise ValueError("Port should be between 1024 and 64000")
        if output[2] == router["routerId"]:
            raise ValueError("Output port routerID matches own routerID")
        if any(d.get('routerId', None) == output[2] for d in outportPortList):
            raise ValueError("RouterID already exists in output list")
        config["routerId"] = output[2]
        if output[0] in router["inputPorts"]:
            raise ValueError("Outport port is shared with an input port")
        if any(d.get('outputPort', None) == output[0] for d in outportPortList):
            raise ValueError("OutputPort already in use")
        config["outputPort"] = output[0]
        outportPortList.append(config)

    return outportPortList

def open_config_file(filePath):
    """
    Takes a filepath as argument, validates it and returns a Config object
    """
    file = open(filePath, 'r')
    if file.mode == 'r':
        config = Config()
        config.parse_file(file)
    else:
        print("Error opening file")
    return config
