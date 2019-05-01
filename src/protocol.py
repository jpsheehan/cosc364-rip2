#/usr/bin/python3

"""

    protocol.py

    COSC364 RIP Assignment

    Date: 02/05/2019

    Written by:
     - Will Cowper (81163265)
     - Jesse Sheehan (53366509)
    
"""

import bencode

__encoding = "utf-8"


def encode(data):
    return bencode.bencode(data).encode(__encoding)


def decode(data):
    return bencode.bdecode(data.decode(__encoding))

class Packet:

    def __init__(self, link_cost = -1, routes = [], triggered=0):
        self.link_cost = link_cost
        self.routes = routes
        self.triggered = triggered
    
    def from_data(self, data):
        d = decode(data)
        self.link_cost = d["link-cost"]
        self.routes = d["routes"]
        self.triggered = d["triggered"]
    
    def to_data(self):
        return encode({
            "link-cost": self.link_cost,
            "routes": self.routes,
            "triggered": self.triggered
        })

    
