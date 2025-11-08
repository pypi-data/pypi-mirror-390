#!/usr/bin/env python3

import unittest
from osmocom.utils import b2h, h2b
from osmocom.construct import *
# pylint: disable=no-name-in-module
from construct import FlagsEnum

class TestGreedyInt(unittest.TestCase):
    tests = [
        ( b'\x80', 0x80 ),
        ( b'\x80\x01', 0x8001 ),
        ( b'\x80\x00\x01', 0x800001 ),
        ( b'\x80\x23\x42\x01', 0x80234201 ),
    ]

    def test_GreedyInt_decoder(self):
        gi = GreedyInteger()
        for t in self.tests:
            self.assertEqual(gi.parse(t[0]), t[1])
    def test_GreedyInt_encoder(self):
        gi = GreedyInteger()
        for t in self.tests:
            self.assertEqual(t[0], gi.build(t[1]))
        pass

class TestUtils(unittest.TestCase):
    def test_filter_dict(self):
        inp = {'foo': 0xf00, '_bar' : 0xba5, 'baz': 0xba2 }
        out = {'foo': 0xf00, 'baz': 0xba2 }
        self.assertEqual(filter_dict(inp), out)

    def test_filter_dict_nested(self):
        inp = {'foo': 0xf00, 'nest': {'_bar' : 0xba5}, 'baz': 0xba2 }
        out = {'foo': 0xf00, 'nest': {}, 'baz': 0xba2 }
        self.assertEqual(filter_dict(inp), out)


class TestUcs2Adapter(unittest.TestCase):
    # the three examples from TS 102 221 Annex A
    EXAMPLE1 = b'\x80\x00\x30\x00\x31\x00\x32\x00\x33'
    EXAMPLE2 = b'\x81\x05\x13\x53\x95\xa6\xa6\xff\xff'
    EXAMPLE3 = b'\x82\x05\x05\x30\x2d\x82\xd3\x2d\x31'
    ad = Ucs2Adapter(GreedyBytes)

    def test_example1_decode(self):
        dec = self.ad._decode(self.EXAMPLE1, None, None)
        self.assertEqual(dec, "0123")

    def test_example2_decode(self):
        dec = self.ad._decode(self.EXAMPLE2, None, None)
        self.assertEqual(dec, "S\u0995\u09a6\u09a6\u09ff")

    def test_example3_decode(self):
        dec = self.ad._decode(self.EXAMPLE3, None, None)
        self.assertEqual(dec, "-\u0532\u0583-1")

    testdata = [
        # variant 2 with only GSM alphabet characters
        ( "mahlzeit", '8108006d61686c7a656974' ),
        # variant 2 with mixed GSM alphabet + UCS2
        ( "mahlzeit\u099523", '810b136d61686c7a656974953233' ),
        # variant 3 due to codepoint exceeding 8 bit
        ( "mahl\u8023zeit", '820980236d61686c807a656974' ),
        # variant 1 as there is no common codepoint pointer / prefix
        ( "\u3000\u2000\u1000", '80300020001000' ),
    ]

    def test_data_decode(self):
        for string, encoded_hex in self.testdata:
            encoded = h2b(encoded_hex)
            dec = self.ad._decode(encoded, None, None)
            self.assertEqual(dec, string)

    def test_data_encode(self):
        for string, encoded_hex in self.testdata:
            encoded = h2b(encoded_hex)
            re_enc = self.ad._encode(string, None, None)
            self.assertEqual(encoded, re_enc)

class TestTrailerAdapter(unittest.TestCase):
    Privileges = FlagsEnum(StripTrailerAdapter(GreedyBytes, 3), security_domain=0x800000,
                                          dap_verification=0x400000,
                                          delegated_management=0x200000, card_lock=0x100000,
                                          card_terminate=0x080000, card_reset=0x040000,
                                          cvm_management=0x020000, mandated_dap_verification=0x010000,
                                          trusted_path=0x8000, authorized_management=0x4000,
                                          token_management=0x2000, global_delete=0x1000,
                                          global_lock=0x0800, global_registry=0x0400,
                                          final_application=0x0200, global_service=0x0100,
                                          receipt_generation=0x80, ciphered_load_file_data_block=0x40,
                                          contactless_activation=0x20, contactless_self_activation=0x10)
    PrivilegesSteps = FlagsEnum(StripTrailerAdapter(GreedyBytes, 3, steps = [1,3]), security_domain=0x800000,
                                          dap_verification=0x400000,
                                          delegated_management=0x200000, card_lock=0x100000,
                                          card_terminate=0x080000, card_reset=0x040000,
                                          cvm_management=0x020000, mandated_dap_verification=0x010000,
                                          trusted_path=0x8000, authorized_management=0x4000,
                                          token_management=0x2000, global_delete=0x1000,
                                          global_lock=0x0800, global_registry=0x0400,
                                          final_application=0x0200, global_service=0x0100,
                                          receipt_generation=0x80, ciphered_load_file_data_block=0x40,
                                          contactless_activation=0x20, contactless_self_activation=0x10)
    IntegerSteps = StripTrailerAdapter(GreedyBytes, 4, steps = [2,4])
    Integer = StripTrailerAdapter(GreedyBytes, 4)

    examples = ['00', '80', '8040', '400010']
    def test_encdec(self):
        for e in self.examples:
            dec = self.Privileges.parse(h2b(e))
            reenc = self.Privileges.build(dec)
            self.assertEqual(e, b2h(reenc))

    def test_encdec_integer(self):
        enc = self.IntegerSteps.build(0x10000000)
        self.assertEqual(b2h(enc), '1000')
        enc = self.IntegerSteps.build(0x10200000)
        self.assertEqual(b2h(enc), '1020')
        enc = self.IntegerSteps.build(0x10203000)
        self.assertEqual(b2h(enc), '10203000')
        enc = self.IntegerSteps.build(0x10203040)
        self.assertEqual(b2h(enc), '10203040')

        enc = self.Integer.build(0x10000000)
        self.assertEqual(b2h(enc), '10')
        enc = self.Integer.build(0x10200000)
        self.assertEqual(b2h(enc), '1020')
        enc = self.Integer.build(0x10203000)
        self.assertEqual(b2h(enc), '102030')
        enc = self.Integer.build(0x10203040)
        self.assertEqual(b2h(enc), '10203040')

    def test_enc(self):
        enc = self.Privileges.build({'dap_verification' : True})
        self.assertEqual(b2h(enc), '40')
        enc = self.Privileges.build({'dap_verification' : True, 'global_service' : True})
        self.assertEqual(b2h(enc), '4001')
        enc = self.Privileges.build({'dap_verification' : True, 'global_service' : True, 'contactless_self_activation' : True})
        self.assertEqual(b2h(enc), '400110')

        enc = self.PrivilegesSteps.build({'dap_verification' : True})
        self.assertEqual(b2h(enc), '40')
        enc = self.PrivilegesSteps.build({'dap_verification' : True, 'global_service' : True})
        self.assertEqual(b2h(enc), '400100')
        enc = self.PrivilegesSteps.build({'dap_verification' : True, 'global_service' : True, 'contactless_self_activation' : True})
        self.assertEqual(b2h(enc), '400110')


class TestStripHeaderAdapter(unittest.TestCase):

    IntegerSteps = StripHeaderAdapter(GreedyBytes, 4, steps = [2,4])
    Integer = StripHeaderAdapter(GreedyBytes, 4)

    def test_encdec_integer_reverse(self):
        enc = self.IntegerSteps.build(0x40)
        self.assertEqual(b2h(enc), '0040')
        enc = self.IntegerSteps.build(0x3040)
        self.assertEqual(b2h(enc), '3040')
        enc = self.IntegerSteps.build(0x203040)
        self.assertEqual(b2h(enc), '00203040')
        enc = self.IntegerSteps.build(0x10203040)
        self.assertEqual(b2h(enc), '10203040')

        enc = self.Integer.build(0x40)
        self.assertEqual(b2h(enc), '40')
        enc = self.Integer.build(0x3040)
        self.assertEqual(b2h(enc), '3040')
        enc = self.Integer.build(0x203040)
        self.assertEqual(b2h(enc), '203040')
        enc = self.Integer.build(0x10203040)
        self.assertEqual(b2h(enc), '10203040')


class TestAdapters(unittest.TestCase):
    def test_dns_adapter(self):
        ad = DnsAdapter(GreedyBytes)
        td = [
            (b'\x08internet', 'internet'),
            (b'\x03www\x07example\x03com', 'www.example.com'),
        ]
        for enc, exp_dec in td:
            with self.subTest(type='decode', name=exp_dec):
                dec = ad._decode(enc, None, None)
                self.assertEqual(dec, exp_dec)
            with self.subTest(type='encode', name=exp_dec):
                re_enc = ad._encode(exp_dec, None, None)
                self.assertEqual(re_enc, enc)

    def test_plmn_adapter(self):
        ad = PlmnAdapter(Bytes(3))
        td = [
            (bytes.fromhex('62f210'),'262-01'),
            (bytes.fromhex('21f354'),"123-45"),
            (bytes.fromhex('216354'),"123-456"),
            (bytes.fromhex('030251'),"302-150")
        ]
        for enc, exp_dec in td:
            with self.subTest(type='decode', name=exp_dec):
                dec = ad._decode(enc, None, None)
                self.assertEqual(dec, exp_dec)
            with self.subTest(type='encode', name=exp_dec):
                re_enc = ad._encode(exp_dec, None, None)
                self.assertEqual(re_enc, enc)


class TestAsn1DerInteger(unittest.TestCase):

    tests = [
        # positive numbers
        ( b'\x00', 0 ),
        ( b'\x01', 1 ),
        ( b'\x02', 2 ),
        ( b'\x7f', 127 ),
        ( b'\x00\x80', 128 ),
        ( b'\x00\x81', 129 ),
        ( b'\x00\xfe', 254 ),
        ( b'\x01\x00', 256 ),
        ( b'\x01\x01', 257 ),
        ( b'\x7f\xff', 32767 ),
        ( b'\x00\x80\x00', 32768 ),
        ( b'\x00\x80\x01', 32769 ),
        ( b'\x00\xff\xfe', 65534 ),
        ( b'\x00\xff\xff', 65535 ),
        ( b'\x01\x00\x00', 65536 ),

        # negative numbers
        ( b'\x00', -0 ),
        ( b'\xff', -1 ),
        ( b'\xfe', -2 ),
        ( b'\x81', -127 ),
        ( b'\x80', -128 ),
        ( b'\xff\x7f', -129 ),
        ( b'\xff\x02', -254 ),
        ( b'\xff\x00', -256 ),
        ( b'\xfe\xff', -257 ),
        ( b'\x80\x01', -32767 ),
        ( b'\x80\x00', -32768 ),
        ( b'\xff\x7f\xff', -32769 ),
        ( b'\xff\x00\x02', -65534 ),
        ( b'\xff\x00\x01', -65535 ),
        ( b'\xff\x00\x00', -65536 ),
    ]

    def test_encode(self):
        adi = Asn1DerInteger()

        # Verfiy with chosen numbers
        for t in self.tests:
            self.assertEqual(t[0], adi.build(t[1]))

        # Verify that ITU-T X.690 8.3.2 is always complied with (for standard two's
        # complement that should always be the case)
        for i in range(-100000,100000):
            res = adi.build(i)
            if len(res) > 1:
                self.assertFalse(int(res[0]) == 0xff and int(res[1]) & 0x80 == 0x80)
                self.assertFalse(int(res[0]) == 0x00 and int(res[1]) & 0x80 == 0x00)

    def test_decode(self):
        adi = Asn1DerInteger()

        # Verfiy with chosen numbers
        for t in self.tests:
            self.assertEqual(t[1], adi.parse(t[0]))


if __name__ == "__main__":
	unittest.main()
