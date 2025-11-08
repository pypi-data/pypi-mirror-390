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

from osmocom.utils import *

class TestHexstr(unittest.TestCase):
    def test_cmp(self):
        s = hexstr('aBcD')
        self.assertEqual(s, 'abcd')
        self.assertEqual(s, 'ABCD')
        self.assertEqual(s, 'AbCd')
        self.assertEqual(s, hexstr('AbCd'))

    def test_tobytes(self):
        s = hexstr('aBcDeF')
        self.assertEqual(s.to_bytes(), b'\xab\xcd\xef')

    def test_tobytes_odd(self):
        s2 = hexstr('aBc')
        with self.assertRaises(ValueError):
            s2.to_bytes()

    def test_frombytes(self):
        s = hexstr.from_bytes(b'\x01\x02\xaa')
        self.assertEqual(s, '0102aa')

    def test_slice(self):
        s = hexstr('abcdef')
        slice1 = s[-2:]
        self.assertTrue(isinstance(slice1, hexstr))
        self.assertEqual(slice1, 'ef')
        slice2 = s[1]
        self.assertTrue(isinstance(slice2, hexstr))
        self.assertEqual(slice2, 'b')

    def test_str_lower(self):
        self.assertEqual(str(hexstr('ABCD')), 'abcd')


class Test_int_bytes_required(unittest.TestCase):

    def test_int_bytes_required(self):

        tests = [
            # unsigned positive numbers
            ( 1, 0, False ),
            ( 1, 1, False ),
            ( 1, 255, False ),
            ( 2, 256, False ),
            ( 2, 65535, False ),
            ( 3, 65536, False ),
            ( 2, 65535, False ),
            ( 3, 16777215, False ),
            ( 4, 16777216, False ),

            # signed positive numbers
            ( 1, 0, True ),
            ( 1, 1, True ),
            ( 1, 127, True ),
            ( 2, 128, True ),
            ( 2, 32767, True ),
            ( 3, 32768, True ),

            # signed negative numbers
            ( 1, -0, True ),
            ( 1, -1, True ),
            ( 1, -128, True ),
            ( 2, -129, True ),
            ( 2, -32768, True ),
            ( 3, -32769, True ),
        ]

        for t in tests:
            self.assertEqual(t[0], int_bytes_required(t[1], signed = t[2]))


if __name__ == "__main__":
	unittest.main()
