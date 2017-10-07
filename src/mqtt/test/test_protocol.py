from unittest import TestCase

from mqtt.protocolstream import parse
from mqtt.packet import PacketType, ConnectReturnCodes, PacketClass

from .examples import (
    CONNECT_PACKET,
    CONNACK_PACKET,
    LONG_PACKET,
    SIMPLE_PUBLISH,
    PUBLISH_QOS_1,
    PUBACK,
    PINGREQ,
    PINGRESP,
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
        self.assertEqual(remaining, b'')
        connect = packets[0].packet

        self.assertIsInstance(connect, PacketClass[PacketType.CONNECT])
        self.assertEqual(connect.keep_alive, 60)
        self.assertEqual(connect.client_identifier, "mosqsub|18215-medina.la")

    def test_connack_packet_basic(self):

        packets, remaining = parse(CONNACK_PACKET)
        self.assertEqual(remaining, b'')
        connack = packets[0].packet

        self.assertIsInstance(connack, PacketClass[PacketType.CONNACK])
        self.assertEqual(connack.session_present, False)
        self.assertEqual(connack.return_code, ConnectReturnCodes.ACCEPTED)


    def test_publish_packet_basic(self):

        packets, remaining = parse(SIMPLE_PUBLISH)
        self.assertEqual(remaining, b'')
        publish = packets[0].packet

        self.assertIsInstance(publish, PacketClass[PacketType.PUBLISH])
        self.assertEqual(publish.packet_identifier, None)
        self.assertEqual(publish.duplicate, False)
        self.assertEqual(publish.qos, 0)
        self.assertEqual(publish.retain, False)
        self.assertEqual(publish.topic, "mqttexample")
        self.assertEqual(publish.payload, b"test!")

    def test_publish_packet_qos_1(self):

        packets, remaining = parse(PUBLISH_QOS_1)
        self.assertEqual(remaining, b'')
        publish = packets[0].packet

        self.assertIsInstance(publish, PacketClass[PacketType.PUBLISH])
        self.assertEqual(publish.packet_identifier, 1)
        self.assertEqual(publish.duplicate, False)
        self.assertEqual(publish.qos, 1)
        self.assertEqual(publish.retain, False)
        self.assertEqual(publish.topic, "mqttexample")
        self.assertEqual(publish.payload, b"test!")

    def test_puback(self):

        packets, remaining = parse(PUBACK)
        self.assertEqual(remaining, b'')
        puback = packets[0].packet

        self.assertIsInstance(puback, PacketClass[PacketType.PUBACK])
        self.assertEqual(puback.packet_identifier, 1)

    def test_pingreq(self):

        packets, remaining = parse(PINGREQ)
        self.assertEqual(remaining, b'')
        pkt = packets[0].packet

        self.assertIsInstance(pkt, PacketClass[PacketType.PINGREQ])

    def test_pingresp(self):

        packets, remaining = parse(PINGRESP)
        self.assertEqual(remaining, b'')
        pkt = packets[0].packet

        self.assertIsInstance(pkt, PacketClass[PacketType.PINGRESP])
