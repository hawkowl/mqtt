import attr
import bitstruct

from .packet import PacketType, parse_into_packet, ParseFailure


@attr.s
class Frame(object):

    packet_type = attr.ib()
    flags = attr.ib()
    body = attr.ib()
    _packet = attr.ib(default=None)

    @property
    def packet(self):
        if self._packet:
            return self._packet
        else:
            self._packet = parse_into_packet(self.packet_type,
                                             self.flags, self.body)
            return self._packet


def parse_next_frame(data):
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

    # Figure out the length of the packet
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

    # Do we have the whole packet?
    if len(data) < 1 + seek_point + packet_length:
        # Not the whole packet yet
        return None, data

    # Build the frame
    frame = Frame(
        packet_type=PacketType(packet_type),
        flags=(flag1, flag2, flag3, flag4),
        body=data[1 + seek_point:packet_length + 1 + seek_point])

    # Return the data we didn't consume
    data = data[1 + seek_point + packet_length:]

    return frame, data


def parse(data):

    frames = []

    while True:
        frame, data = parse_next_frame(data)

        if frame:
            frames.append(frame)
        else:
            return frames, data
