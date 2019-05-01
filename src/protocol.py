import bencode

__encoding = "utf-8"


def encode(data):
    return bencode.bencode(data).encode(__encoding)


def decode(data):
    return bencode.bdecode(data.decode(__encoding))

class Packet:

    def __init__(self, link_cost = -1, routes = []):
        self.link_cost = link_cost
        self.routes = routes
    
    def from_data(self, data):
        d = decode(data)
        self.link_cost = d["link-cost"]
        self.routes = d["routes"]
    
    def to_data(self):
        return encode({
            "link-cost": self.link_cost,
            "routes": self.routes
        })

    
