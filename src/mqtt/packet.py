import attr
import bitstruct

from enum import IntEnum, Enum


class ParseFailure(ValueError):
    pass


class PacketType(IntEnum):
    CONNECT = 1
    CONNACK = 2
    PUBLISH = 3
    PUBACK = 4
    PUBREC = 5
    PUBREL = 6
    PUBCOMP = 7
    SUBSCRIBE = 8
    SUBACK = 9
    UNSUBSCRIBE = 10
    UNSUBACK = 11
    PINGREQ = 12
    PINGRESP = 13
    DISCONNECT = 14


class ConnectReturnCodes(IntEnum):
    ACCEPTED = 0
    UNACCEPTABLE_PROTOCOL = 1
    IDENTIFIER_REJECTED = 2
    SERVER_UNAVAILABLE = 3
    BAD_USER_OR_PASSWORD = 4
    NOT_AUTHORIZED = 5


def parse_utf8(data):
    """
    Parse a length-prefixed UTF-8 string and return the string and unused data.
    """
    length, = bitstruct.unpack('u16', data[0:2])
    string = data[2:length+2].decode('utf8')
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


@attr.s
class CONNACK(object):

    session_present = attr.ib()
    return_code = attr.ib()

    @classmethod
    def _parse(cls, flags, body):

        if not flags == (False, False, False, False):
            raise ParseFailure()

        if not len(body) == 2:
            raise ParseFailure()

        reserved, session_present, ret_code = bitstruct.unpack('u7b1u8', body)

        if reserved != 0:
            # Byte 1 is the "Connect Acknowledge Flags". Bits 7-1 are reserved
            # and MUST be set to 0.
            raise ParseFailure()

        return cls(
            session_present=session_present,
            return_code=ConnectReturnCodes(ret_code)
        )


@attr.s
class PUBLISH(object):

    duplicate = attr.ib()
    qos = attr.ib()
    retain = attr.ib()
    topic = attr.ib()
    payload = attr.ib()
    packet_identifier = attr.ib()

    @classmethod
    def _parse(cls, flags, body):

        if flags[1] and flags[2]:
            # A PUBLISH Packet MUST NOT have both QoS bits set to 1. If a
            # Server or Client receives a PUBLISH Packet which has both QoS
            # bits set to 1 it MUST close the Network Connection
            # [MQTT-3.3.1-4].
            raise ParseFailure()

        # Repack and unpack the flags
        dup, qos, retain = bitstruct.unpack(
            "p4b1u2b1", bitstruct.pack('p4b1b1b1b1', *flags))

        if qos not in [0, 1, 2]:
            raise ParseFailure()

        topic, body = parse_utf8(body)

        if qos != 0:
            packet_identifier, = bitstruct.unpack('u16', body[0:2])
            payload = body[2:]
        else:
            packet_identifier = None
            payload = body

        return cls(
            duplicate=dup,
            qos=qos,
            retain=retain,
            topic=topic,
            payload=payload,
            packet_identifier=packet_identifier
        )


@attr.s
class PUBACK(object):

    packet_identifier = attr.ib()

    @classmethod
    def _parse(cls, flags, body):

        # Needs to be 2 bytes long
        if not len(body) == 2:
            raise ParseFailure()

        packet_identifier, = bitstruct.unpack('u16', body)

        return cls(packet_identifier=packet_identifier)


PacketClass = {
    PacketType.CONNECT: CONNECT,
    PacketType.CONNACK: CONNACK,
    PacketType.PUBLISH: PUBLISH,
    PacketType.PUBACK: PUBACK,
}


def parse_into_packet(message_type, flags, body):

    class_to_use = PacketClass[message_type]
    return class_to_use._parse(flags, body)
