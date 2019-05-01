import bencode

__encoding = "utf-8"


def encode_routes(routes):
    return bencode.bencode(routes).encode(__encoding)


def decode_routes(data):
    return bencode.bdecode(data.decode(__encoding))
