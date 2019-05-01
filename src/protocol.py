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
import binascii

__encoding = "utf-8"


def encode(data):
    """
        Encodes the raw data, including a checksum.
    """
    body = bencode.bencode(data).encode(__encoding)
    crc = binascii.crc32(body)
    return crc.to_bytes(4, "big") + body


def decode(data):
    """
        Decodes raw data, checks the validity and returns the dictionary containing the data.
        Returns None if the data is invalid.
    """
    try:
        # get the CRC32 code
        crc = int.from_bytes(data[:4], "big")

        # get the body
        body = data[4:]

        # return None if the checksum is incorrect
        if crc != binascii.crc32(body):
            return None

        # return the decoded data if the checksum is correct
        else:
            return bencode.bdecode(body.decode(__encoding))
    except:
        return None

class Packet:
    """
        A Packet is used to send and receive updates from other RIP routers.
    """

    def __init__(self, link_cost = -1, routes = [], triggered=0):
        """
            Creates a new Packet.
        """
        self.link_cost = link_cost
        self.routes = routes
        self.triggered = triggered
    
    def from_data(self, data):
        """
            Sets the packet information from some raw data.
            Returns True if successful.
        """
        d = decode(data)

        if d is not None:
            self.link_cost = d["link-cost"]
            self.routes = d["routes"]
            self.triggered = d["triggered"]
            return True
        else:
            return False
    
    def to_data(self):
        """
            Returns the raw data to be sent.
        """
        return encode({
            "link-cost": self.link_cost,
            "routes": self.routes,
            "triggered": self.triggered
        })

    
