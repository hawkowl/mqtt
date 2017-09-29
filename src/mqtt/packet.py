import attr
import bitstruct

from enum import IntEnum, Enum


class ParseFailure(ValueError):
    pass


class PacketType(IntEnum):
    CONNECT = 1
    CONNACK = 2


def parse_utf8(data):
    """
    Parse a length-prefixed UTF-8 string and return the string and unused data.
    """
    length, = bitstruct.unpack('u16', data[0:2])
    string = data[2:length].decode('utf8')
    return string, data[2 + length:]


@attr.s
class CONNECT(object):

    keep_alive = attr.ib()
    client_identifier = attr.ib()

    @classmethod
    def _parse(cls, flags, body):

        if not flags == (False, False, False, False):
            raise ParseFailure()

        # Header Parsing
        protocol_name, body = parse_utf8(body)
        protocol_level = body[0]

        flag_user_name, flag_password, will_retain, will_qos, will_flag, clean_session, reserved = bitstruct.unpack('b1b1b1u2b1b1b1', body[1:2])

        if reserved:
            # The Server MUST validate that the reserved flag in the CONNECT
            # Control Packet is set to zero and disconnect the Client if it is
            # not zero [MQTT-3.1.2-3].
            raise ParseFailure()

        keep_alive, = bitstruct.unpack('u16', body[2:4])

        # Payload Parsing
        client_identifier, body = parse_utf8(body[4:])

        # todo: the rest of the garbage here
        if will_flag:
            will_topic, body = parse_utf8(body)
            will_message, body = parse_utf8(body)
        else:
            will_topic = None
            will_message = None

        return cls(keep_alive=keep_alive,
                   client_identifier=client_identifier)


PacketClass = {
    PacketType.CONNECT: CONNECT
}


def parse_into_packet(message_type, flags, body):

    class_to_use = PacketClass[message_type]
    return class_to_use._parse(flags, body)
