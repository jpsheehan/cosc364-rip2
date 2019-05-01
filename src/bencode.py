"""
A bencoding implementation based on the official specification (https://wiki.theory.org/index.php/BitTorrentSpecification#Bencoding)

"""


def bencode(value):
    """
    Test Integer Encoding:
    >>> bencode(42)
    'i42e'
    >>> bencode(0)
    'i0e'
    >>> bencode(-42)
    'i-42e'

    Test String Encoding:
    >>> bencode("spam")
    '4:spam'
    >>> bencode("i")
    '1:i'
    >>> bencode("")
    '0:'
    >>> bencode("COSC364 is the greatest course evarrrr!")
    '39:COSC364 is the greatest course evarrrr!'

    Test List Encoding:
    >>> bencode(["spam", 42])
    'l4:spami42ee'

    Test Dictionary Encoding:
    >>> bencode({"bar": "spam", "foo": 42})
    'd3:bar4:spam3:fooi42ee'

    """

    # integer encoding
    if type(value) is int:
        return "i" + str(value) + "e"

    # string encoding
    if type(value) is str:
        return str(len(value)) + ":" + value

    # list encoding
    if type(value) is list:
        return "l" + "".join(map(bencode, value)) + "e"

    # dictionary encoding
    if type(value) is dict:
        # TODO: keys should be in alphabetical order
        # TODO: check that the key is a string
        return "d" + "".join([bencode(k) + bencode(v) for k, v in value.items()]) + "e"

    raise ValueError(str(type(value)) +
                     " must be one of int, str, list or dict")


def bdecode(string, returnLength=False):
    """
    >>> bdecode("i42e")
    42
    >>> bdecode("i0e")
    0
    >>> bdecode("i-42e")
    -42

    >>> bdecode("i42e", True)
    (42, 4)
    >>> bdecode("i0e", True)
    (0, 3)
    >>> bdecode("i-42e", True)
    (-42, 5)

    >>> bdecode("4:spam")
    'spam'
    >>> bdecode("1:i")
    'i'
    >>> bdecode("0:")
    ''
    >>> bdecode("39:COSC364 is the greatest course evarrrr!")
    'COSC364 is the greatest course evarrrr!'

    >>> bdecode("4:spam", True)
    ('spam', 6)
    >>> bdecode("1:i", True)
    ('i', 3)
    >>> bdecode("0:", True)
    ('', 2)
    >>> bdecode("39:COSC364 is the greatest course evarrrr!", True)
    ('COSC364 is the greatest course evarrrr!', 42)

    >>> bdecode("l4:spami42ee")
    ['spam', 42]
    >>> bdecode("l4:spami42el9:more spami-42eee")
    ['spam', 42, ['more spam', -42]]

    >>> bdecode("l4:spami42ee", True)
    (['spam', 42], 12)
    >>> bdecode("l4:spami42el9:more spami-42eee", True)
    (['spam', 42, ['more spam', -42]], 30)

    >>> bdecode("d3:bar4:spam3:fooi42ee")
    {'bar': 'spam', 'foo': 42}
    >>> bdecode("d3:bar4:spam3:fooi42e4:listl4:spami42el9:more spami-42eeee")
    {'bar': 'spam', 'foo': 42, 'list': ['spam', 42, ['more spam', -42]]}

    >>> bdecode("d3:bar4:spam3:fooi42ee", True)
    ({'bar': 'spam', 'foo': 42}, 22)
    >>> bdecode("d3:bar4:spam3:fooi42e4:listl4:spami42el9:more spami-42eeee", True)
    ({'bar': 'spam', 'foo': 42, 'list': ['spam', 42, ['more spam', -42]]}, 58)

    """

    value = None
    length = 0

    # integer decoding
    if string[0] == 'i':

        # get the end of the integer string
        end = string.find('e')
        if end == -1:
            raise ValueError(string[0:10] + "... is not a bencoded integer")

        # get the integer from the string (this may throw a ValueError)
        value = int(string[1:end])

        # update the length to account for the entire integer string
        length = end + 1

    # string decoding
    elif string[0].isnumeric():

        # get the end of the string length
        length_end = string.find(':')
        if length_end == -1:
            raise ValueError(string[0:10] + "... is not a bencoded string")

        # get the string length as an integer
        str_length = int(string[0:length_end])

        # get the actual string
        value = string[length_end + 1:length_end + 1 + str_length]

        # update the length to be the length of the string including the string length
        length = length_end + 1 + str_length

    # list decoding
    elif string[0] == 'l':

        # set the offset to 1 to account for the starting 'l'
        offset = 1
        value = []

        while string[offset] != 'e':

            # decode the inner value
            inner_value, inner_length = bdecode(string[offset:], True)
            offset += inner_length

            # update the list
            value.append(inner_value)

        # update the length to account for the closing 'e'
        length = offset + 1

    # dictionary decoding
    elif string[0] == 'd':

        # set the offset to 1 to account for the starting 'd'
        offset = 1

        # in Python >= 3.6, the dictionary implementation remembers the
        # insertion order
        value = {}

        while string[offset] != 'e':

            # decode the key
            inner_key, inner_length = bdecode(string[offset:], True)
            offset += inner_length
            # TODO: inner_key should be a string

            # decode the value
            inner_value, inner_length = bdecode(string[offset:], True)
            offset += inner_length

            # update the dictionary
            value[inner_key] = inner_value

        # TODO: validate that the keys are in alphabetical order

        # update the length to account for the closing 'e'
        length = offset + 1

    # return the length as well if requested
    if returnLength:
        return value, length
    else:
        return value


if __name__ == "__main__":
    import doctest
    doctest.testmod()
