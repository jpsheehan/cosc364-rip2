import bencode

__encoding = "utf-8"


def encode(data):
    return bencode.bencode(data).encode(__encoding)


def decode(data):
    return bencode.bdecode(data.decode(__encoding))
