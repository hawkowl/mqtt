from unittest import TestCase

from mqtt.protocolstream import parse
from mqtt.packet import PacketType


CONNECT_PACKET = bytes((
    0x10, 0x25, 0x00, 0x06, 0x4d, 0x51, 0x49, 0x73,
    0x64, 0x70, 0x03, 0x02, 0x00, 0x3c, 0x00, 0x17,
    0x6d, 0x6f, 0x73, 0x71, 0x73, 0x75, 0x62, 0x7c,
    0x31, 0x38, 0x32, 0x31, 0x35, 0x2d, 0x6d, 0x65,
    0x64, 0x69, 0x6e, 0x61, 0x2e, 0x6c, 0x61))

LONG_PACKET =  bytes((0x10, 0x80, 0x01) + (0x00,) * 128)


class StreamParsingTests(TestCase):

    def test_single_packet(self):

        packets, remaining = parse(CONNECT_PACKET)

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0].packet_type, PacketType.CONNECT)
        self.assertEqual(remaining, b'')

    def test_incomplete_packet(self):

        packets, remaining = parse(CONNECT_PACKET + CONNECT_PACKET[0:5])

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0].packet_type, PacketType.CONNECT)
        self.assertEqual(remaining, CONNECT_PACKET[0:5])

    def test_super_long_packet(self):

        packets, remaining = parse(LONG_PACKET)

        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0].packet_type, PacketType.CONNECT)
        self.assertEqual(remaining, b'')


class PacketParsingTests(TestCase):

    def test_connect_packet_basic(self):

        packets, remaining = parse(CONNECT_PACKET)
        connect_packet = packets[0].packet

        print(connect_packet)
