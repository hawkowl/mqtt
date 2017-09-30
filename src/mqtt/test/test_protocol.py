from unittest import TestCase

from mqtt.protocolstream import parse
from mqtt.packet import PacketType

from .examples import (
    CONNECT_PACKET,
    LONG_PACKET,
    SIMPLE_PUBLISH,
)

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

    def test_multiple_packets(self):

        packets, remaining = parse(CONNECT_PACKET + SIMPLE_PUBLISH)

        self.assertEqual(len(packets), 2)
        self.assertEqual(packets[0].packet_type, PacketType.CONNECT)
        self.assertEqual(packets[1].packet_type, PacketType.PUBLISH)
        self.assertEqual(remaining, b'')


class PacketParsingTests(TestCase):

    def test_connect_packet_basic(self):

        packets, remaining = parse(CONNECT_PACKET)
        connect = packets[0].packet

        self.assertEqual(connect.keep_alive, 60)
        self.assertEqual(connect.client_identifier, "mosqsub|18215-medina.la")

    def test_publish_packet_basic(self):

        packets, remaining = parse(SIMPLE_PUBLISH)
        self.assertEqual(remaining, b'')
        publish = packets[0].packet

        self.assertEqual(publish.packet_identifier, None)
        self.assertEqual(publish.duplicate, False)
        self.assertEqual(publish.qos, 0)
        self.assertEqual(publish.retain, False)
        self.assertEqual(publish.topic, "mqttexample")
        self.assertEqual(publish.payload, b"test!")
