#!/usr/bin/env python3

'''
Super SIM UPLMN Codec

@version    1.0.0
@author     Tony Smith (@smittytone)
@copyright  Twilio, Inc.
@licence    MIT

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
IMPORTS
'''
import unittest
from plmn_codec import plmn_encoder, plmn_decoder, decode_table

'''
TEST CASES
'''
class CodecTests(unittest.TestCase):

    def test_plmn_encoder(self):
        # Basic cases
        self.assertEqual(plmn_encoder("310", "410"), "1300144080")
        self.assertEqual(plmn_encoder("310", "260"), "1300624080")

        # Over-long MCC, MNC
        self.assertEqual(plmn_encoder("3108", "410333"), "1300144080")

        # Short MNC
        self.assertEqual(plmn_encoder("289", "88"), "82F9884080")


    def test_plmn_decoder(self):
        # Basic cases
        self.assertEqual(plmn_decoder("1300144080"), ("310", "410"))
        self.assertEqual(plmn_decoder("1300624080"), ("310", "260"))

        # Over-long PLMN
        self.assertEqual(plmn_decoder("1300624080FFFFFF"), ("310", "260"))

        # Short MNC
        self.assertEqual(plmn_decoder("82F9884080"), ("289", "88"))


    def test_decode_table(self):
        # Basic cases
        self.assertEqual(decode_table("AT+CRSM=214,28512,0,0,10,13006240801300144080"), "1. MCC: 310 MNC: 260\n2. MCC: 310 MNC: 410\n")
        self.assertEqual(decode_table("10,13006240801300144080"), "1. MCC: 310 MNC: 260\n2. MCC: 310 MNC: 410\n")
        self.assertEqual(decode_table("13006240801300144080"), "1. MCC: 310 MNC: 260\n2. MCC: 310 MNC: 410\n")
        self.assertEqual(decode_table("+CRSM: 144,0,13006240801300144080"), "1. MCC: 310 MNC: 260\n2. MCC: 310 MNC: 410\n")

        # Short table entry
        self.assertEqual(decode_table("82F988408"), "")


'''
RUNTIME START
'''
if __name__ == '__main__':
    unittest.main()