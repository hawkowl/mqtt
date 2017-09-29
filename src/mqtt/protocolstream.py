
import attr
import bitstruct

from enum import IntEnum

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

    if data[1:2] == 0xFF:
        # Above 128
        if data[2:3] == 0xFF:
            # Above 16383
            if data[3:4] == 0xFF:
                # Above 2097151
                length = 'u'
        else:
            length = bitstruct.unpack('u16', data[1:3])
            bit_chop = 2

    else:
        length, = bitstruct.unpack('u8', data[1:2])
        bit_chop = 1


    if len(data) < 1 + bit_chop + length:
        # Not the whole packet yet
        return None, data

    packet = Packet(
        packet_type=PacketType(packet_type),
        flags = (flag1, flag2, flag3, flag4),
        body = data[1 + bit_chop:length])

    data = data[1 + bit_chop + length:]

    return packet, data


def parse(data):

    packets = []

    while True:
        packet, data = parse_next_packet(data)

        if packet:
            packets.append(packet)
        else:
            return packets, data
