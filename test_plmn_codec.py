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
from plmn_codec import plmn_encoder, plmn_decoder, decode_table, decode_lte, decode_gsm, main


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
        self.assertEqual(plmn_decoder("1300144080"), ("310", "410", 64, 128))
        self.assertEqual(plmn_decoder("1300624080"), ("310", "260", 64, 128))

        # Over-long PLMN
        self.assertEqual(plmn_decoder("1300624080FFFFFF"), ("310", "260", 64, 128))

        # Short MNC
        self.assertEqual(plmn_decoder("82F9884080"), ("289", "88", 64, 128))


    def test_decode_table(self):
        # Basic cases
        self.assertEqual(decode_table("AT+CRSM=214,28512,0,0,10,13006240801300144080"), "1. MCC: 310 MNC: 260 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT\n2. MCC: 310 MNC: 410 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT")
        self.assertEqual(decode_table("10,13006240801300144080"), "1. MCC: 310 MNC: 260 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT\n2. MCC: 310 MNC: 410 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT")
        self.assertEqual(decode_table("13006240801300144080"), "1. MCC: 310 MNC: 260 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT\n2. MCC: 310 MNC: 410 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT")
        self.assertEqual(decode_table("+CRSM: 144,0,13006240801300144080"), "1. MCC: 310 MNC: 260 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT\n2. MCC: 310 MNC: 410 RAT(s): E-UTRAN in WB-S1, NB-S1 modes, GSM + EC-GSM-IoT")

        # Short table entry
        self.assertEqual(decode_table("82F988408"), "")


    def test_decode_lte(self):
        self.assertEqual(decode_lte(0xFF), "UTRAN, E-UTRAN in WB-S1, NB-S1 modes, NG-RAN -- WARNING: Reserved bits set")
        self.assertEqual(decode_lte(0x00), "")
        self.assertEqual(decode_lte(0x01), " -- WARNING: Reserved bits set")
        self.assertEqual(decode_lte(0x02), " -- WARNING: Reserved bits set")
        self.assertEqual(decode_lte(0x50), "E-UTRAN in NB-S1 mode only")


    def test_decode_gsm(self):
        self.assertEqual(decode_gsm(0xFF), "GSM + EC-GSM-IoT, GSM COMPACT, CDMA2000 HRPD, CDMA2000 1xRTT -- WARNING: Reserved bits set")
        self.assertEqual(decode_gsm(0x00), "")
        self.assertEqual(decode_gsm(0x01), " -- WARNING: Reserved bits set")
        self.assertEqual(decode_gsm(0x02), " -- WARNING: Reserved bits set")
        self.assertEqual(decode_gsm(0x84), "GSM")
        self.assertEqual(decode_gsm(0x88), "EC-GSM-IoT")


    # main() tests: arguments
    def test_main_missing_final_arg(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-p","13006240801300144080","-p"])
            self.assertEqual(cm.exception.code, 1)


    def test_main_missing_inline_arg(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-p"])
            self.assertEqual(cm.exception.code, 1)


    def test_main_bad_arg(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-q","13006240801300144080"])
            self.assertEqual(cm.exception.code, 1)


    def test_main_malformed_table(self):
        with self.assertRaises(SystemExit) as cm:
            main(["-p","130062408013001440"])
            self.assertEqual(cm.exception.code, 1)


    def test_main_mispaired_mcc_mnc(self):
        with self.assertRaises(SystemExit) as cm:
            main(["310", "410", "310"])
            self.assertEqual(cm.exception.code, 1)


    def test_main_no_args(self):
        with self.assertRaises(SystemExit) as cm:
            main([])
            self.assertEqual(cm.exception.code, 0)


'''
RUNTIME START
'''
if __name__ == '__main__':
    unittest.main()