
import attr
import bitstruct

from enum import IntEnum

class ParseFailure(ValueError):
    pass


class PacketType(IntEnum):
    CONNECT = 1
    CONNACK = 2


@attr.s
class Packet(object):

    packet_type = attr.ib()
    flags = attr.ib()
    body = attr.ib()


def parse_next_packet(data):
    """
    Parse the next packet from this MQTT data stream.
    """

    if not data:
        return None, b''

    if len(data) < 2:
        # Not enough data yet
        return None, data

    packet_type, flag1, flag2, flag3, flag4 = bitstruct.unpack('u4b1b1b1b1', data[0:1])
    length = None

    seek_point = 0
    seek_multiplier = 1
    packet_length = 0
    encoded_byte = -1

    while (encoded_byte & 128) != 0:

        seek_point += 1

        if len(data) < 1 + seek_point:
            # Not enough data
            return None, data

        encoded_byte, = bitstruct.unpack('u8', data[seek_point:seek_point+1])

        packet_length += (encoded_byte & 127) * seek_multiplier
        seek_multiplier = seek_multiplier * 128

        if seek_multiplier > 128 * 128 * 128:
            raise ParseFailure()

    if len(data) < 1 + seek_point + packet_length:
        # Not the whole packet yet
        return None, data

    packet = Packet(
        packet_type=PacketType(packet_type),
        flags = (flag1, flag2, flag3, flag4),
        body = data[1 + seek_point:packet_length])

    data = data[1 + seek_point + packet_length:]

    return packet, data


def parse(data):

    packets = []

    while True:
        packet, data = parse_next_packet(data)

        if packet:
            packets.append(packet)
        else:
            return packets, data
