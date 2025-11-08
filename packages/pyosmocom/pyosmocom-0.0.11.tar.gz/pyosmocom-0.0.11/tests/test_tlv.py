#!/usr/bin/env python3

# (C) 2022 by Harald Welte <laforge@osmocom.org>
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from construct import Int8ub, GreedyBytes
from osmocom.tlv import *
from osmocom.utils import h2b

class TestBerTlv(unittest.TestCase):
    def test_BerTlvTagDec(self):
        res = bertlv_parse_tag(b'\x01')
        self.assertEqual(res, ({'tag':1, 'constructed':False, 'class': 0}, b''))
        res = bertlv_parse_tag(b'\x21')
        self.assertEqual(res, ({'tag':1, 'constructed':True, 'class': 0}, b''))
        res = bertlv_parse_tag(b'\x81\x23')
        self.assertEqual(res, ({'tag':1, 'constructed':False, 'class': 2}, b'\x23'))
        res = bertlv_parse_tag(b'\x1f\x8f\x00\x23')
        self.assertEqual(res, ({'tag':0xf<<7, 'constructed':False, 'class': 0}, b'\x23'))

    def test_BerTlvLenDec(self):
        self.assertEqual(bertlv_encode_len(1), b'\x01')
        self.assertEqual(bertlv_encode_len(127), b'\x7f')
        self.assertEqual(bertlv_encode_len(128), b'\x81\x80')
        self.assertEqual(bertlv_encode_len(0x123456), b'\x83\x12\x34\x56')

    def test_BerTlvLenEnc(self):
        self.assertEqual(bertlv_parse_len(b'\x01\x23'), (1, b'\x23'))
        self.assertEqual(bertlv_parse_len(b'\x7f'), (127, b''))
        self.assertEqual(bertlv_parse_len(b'\x81\x80'), (128, b''))
        self.assertEqual(bertlv_parse_len(b'\x83\x12\x34\x56\x78'), (0x123456, b'\x78'))

    def test_BerTlvParseOne(self):
        res = bertlv_parse_one(b'\x81\x01\x01');
        self.assertEqual(res, ({'tag':1, 'constructed':False, 'class':2}, 1, b'\x01', b''))

class TestComprTlv(unittest.TestCase):
    def test_ComprTlvTagDec(self):
        res = comprehensiontlv_parse_tag(b'\x12\x23')
        self.assertEqual(res, ({'tag': 0x12, 'comprehension': False}, b'\x23'))
        res = comprehensiontlv_parse_tag(b'\x92')
        self.assertEqual(res, ({'tag': 0x12, 'comprehension': True}, b''))
        res = comprehensiontlv_parse_tag(b'\x7f\x12\x34')
        self.assertEqual(res, ({'tag': 0x1234, 'comprehension': False}, b''))
        res = comprehensiontlv_parse_tag(b'\x7f\x82\x34\x56')
        self.assertEqual(res, ({'tag': 0x234, 'comprehension': True}, b'\x56'))

    def test_ComprTlvTagEnc(self):
        res  = comprehensiontlv_encode_tag(0x12)
        self.assertEqual(res, b'\x12')
        res  = comprehensiontlv_encode_tag({'tag': 0x12})
        self.assertEqual(res, b'\x12')
        res  = comprehensiontlv_encode_tag({'tag': 0x12, 'comprehension':True})
        self.assertEqual(res, b'\x92')
        res  = comprehensiontlv_encode_tag(0x1234)
        self.assertEqual(res, b'\x7f\x12\x34')
        res  = comprehensiontlv_encode_tag({'tag': 0x1234, 'comprehension':True})
        self.assertEqual(res, b'\x7f\x92\x34')

class TestDgiTlv(unittest.TestCase):
    def test_DgiTlvLenEnc(self):
        self.assertEqual(dgi_encode_len(10), b'\x0a')
        self.assertEqual(dgi_encode_len(254), b'\xfe')
        self.assertEqual(dgi_encode_len(255), b'\xff\x00\xff')
        self.assertEqual(dgi_encode_len(65535), b'\xff\xff\xff')
        with self.assertRaises(ValueError):
            dgi_encode_len(65536)

    def testDgiTlvLenDec(self):
        self.assertEqual(dgi_parse_len(b'\x0a\x0b'), (10, b'\x0b'))
        self.assertEqual(dgi_parse_len(b'\xfe\x0b'), (254, b'\x0b'))
        self.assertEqual(dgi_parse_len(b'\xff\x00\xff\x0b'), (255, b'\x0b'))


class TestUtils(unittest.TestCase):
    def test_camel_to_snake(self):
        cases = [
            ('CamelCase', 'camel_case'),
            ('CamelCaseUPPER', 'camel_case_upper'),
            ('Camel_CASE_underSCORE', 'camel_case_under_score'),
        ]
        for c in cases:
            self.assertEqual(camel_to_snake(c[0]), c[1])

    def test_flatten_dict_lists(self):
        inp = [
                { 'first': 1 },
                { 'second': 2 },
                { 'third': 3 },
                ]
        out = { 'first': 1, 'second':2, 'third': 3}
        self.assertEqual(flatten_dict_lists(inp), out)

    def test_flatten_dict_lists_nodict(self):
        inp = [
                { 'first': 1 },
                { 'second': 2 },
                { 'third': 3 },
                4,
                ]
        self.assertEqual(flatten_dict_lists(inp), inp)

    def test_flatten_dict_lists_nested(self):
        inp = {'top': [
                { 'first': 1 },
                { 'second': 2 },
                { 'third': 3 },
                ] }
        out = {'top': { 'first': 1, 'second':2, 'third': 3 } }
        self.assertEqual(flatten_dict_lists(inp), out)

class TestTranscodable(unittest.TestCase):
    class XC_constr_class(Transcodable):
        _construct = Int8ub
        def __init__(self):
            super().__init__();

    def test_XC_constr_class(self):
        """Transcodable derived class with _construct class variable"""
        xc = TestTranscodable.XC_constr_class()
        self.assertEqual(xc.from_bytes(b'\x23'), 35)
        self.assertEqual(xc.to_bytes(), b'\x23')

    class XC_constr_instance(Transcodable):
        def __init__(self):
            super().__init__();
            self._construct = Int8ub

    def test_XC_constr_instance(self):
        """Transcodable derived class with _construct instance variable"""
        xc = TestTranscodable.XC_constr_instance()
        self.assertEqual(xc.from_bytes(b'\x23'), 35)
        self.assertEqual(xc.to_bytes(), b'\x23')

    class XC_method_instance(Transcodable):
        def __init__(self):
            super().__init__();
        def _from_bytes(self, do):
            return ('decoded', do)
        def _to_bytes(self):
            return self.decoded[1]

    def test_XC_method_instance(self):
        """Transcodable derived class with _{from,to}_bytes() methods"""
        xc = TestTranscodable.XC_method_instance()
        self.assertEqual(xc.to_bytes(), b'')
        self.assertEqual(xc.from_bytes(b''), None)
        self.assertEqual(xc.from_bytes(b'\x23'), ('decoded', b'\x23'))
        self.assertEqual(xc.to_bytes(), b'\x23')

class TestIE(unittest.TestCase):
    class MyIE(IE, tag=0x23, desc='My IE description'):
        _construct = Int8ub
        def to_ie(self):
            return self.to_bytes()

    def test_IE_empty(self):
        ie = TestIE.MyIE()
        self.assertEqual(ie.to_dict(), {'my_ie': None})
        self.assertEqual(repr(ie), 'MyIE(None)')
        self.assertEqual(ie.is_constructed(), False)

    def test_IE_from_bytes(self):
        ie = TestIE.MyIE()
        ie.from_bytes(b'\x42')
        self.assertEqual(ie.to_dict(), {'my_ie': 66})
        self.assertEqual(repr(ie), 'MyIE(66)')
        self.assertEqual(ie.is_constructed(), False)
        self.assertEqual(ie.to_bytes(), b'\x42')
        self.assertEqual(ie.to_ie(), b'\x42')

class TestCompact(unittest.TestCase):
    class IE_3(COMPACT_TLV_IE, tag=0x3):
        _construct = GreedyBytes
    class IE_7(COMPACT_TLV_IE, tag=0x7):
        _construct = GreedyBytes
    class IE_5(COMPACT_TLV_IE, tag=0x5):
        _construct = GreedyBytes
    # pylint: disable=undefined-variable
    class IE_Coll(TLV_IE_Collection, nested=[IE_3, IE_7, IE_5]):
        _construct = GreedyBytes
    def test_ATR(self):
        atr = h2b("31E073FE211F5745437531301365")
        c = self.IE_Coll()
        c.from_tlv(atr)
        self.assertEqual(c.children[0].tag, 3)
        self.assertEqual(c.children[0].to_bytes(), b'\xe0')
        self.assertEqual(c.children[1].tag, 7)
        self.assertEqual(c.children[1].to_bytes(), b'\xfe\x21\x1f')
        self.assertEqual(c.children[2].tag, 5)
        self.assertEqual(c.children[2].to_bytes(), b'\x45\x43\x75\x31\x30\x13\x65')
        self.assertEqual(c.to_tlv(), atr)


if __name__ == "__main__":
	unittest.main()
