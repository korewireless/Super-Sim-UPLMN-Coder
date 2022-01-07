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
import sys


'''
FUNCTIONS
'''

'''
Assemble a PLMN string from MCC, MNC values
'''
def plmn_encoder(mcc, mnc):
    # Use 'F' for unused columns, ie. '81' -> '81F'
    if len(mnc) < 3: mnc += "FFF"[:3 - len(mnc)]
    if len(mcc) < 3: mcc += "FFF"[:3 - len(mcc)]
    if len(mnc) > 3: mnc = mnc[:3]
    if len(mcc) > 3: mcc = mcc[:3]

    # Rearrange octets
    plmn = mcc + mnc
    plmn = plmn[1] + plmn[0] + plmn[5] + plmn[2] + plmn[4] + plmn[3]

    # Add the RAT value [E-UTRAN (4G) + GSM]
    return plmn + "4080"


'''
Turn a PLMN entry, eg. '1300144080' into MCC, MNC values (tuple)
'''
def plmn_decoder(plmn):
    # Rearrange octets and output
    mcc = (plmn[1] + plmn[0] + plmn[3]).replace("F", "")
    mnc = (plmn[5] + plmn[4] + plmn[2]).replace("F", "")
    lte = int(plmn[6] + plmn[7], 16)
    gsm = int(plmn[8] + plmn[9], 16)
    return (mcc, mnc, lte, gsm)


'''
Determine the PLMN entry's LTE mode
'''
def decode_lte(byte_value):
    sub_lte = ["E-UTRAN in WB-S1, NB-S1 modes", "E-UTRAN in NB-S1 mode only",
               "E-UTRAN in WB-S1 mode only", "E-UTRAN in WB-S1, NB-S1 modes"]
    code = ""
    if byte_value & 0x80: code += "UTRAN, "
    if byte_value & 0x40:
        code += (sub_lte[(byte_value & 0x30) >> 4] + ", ")
    if byte_value & 0x08: code += "NG-RAN, "
    if len(code): code = code[:-2]
    if byte_value & 0x07 > 0: code += " -- WARNING: Reserved bits set"
    return code


'''
Determine the PLMN entry's GSM/CDMA mode
'''
def decode_gsm(byte_value):
    sub_gsm = ["GSM + EC-GSM-IoT", "GSM",
               "EC-GSM-IoT", "GSM + EC-GSM-IoT"]
    code = ""
    if byte_value & 0x80:
        code += (sub_gsm[(byte_value & 0x0C) >> 2] + ", ")
    if byte_value & 0x40: code += "GSM COMPACT, "
    if byte_value & 0x20: code += "CDMA2000 HRPD, "
    if byte_value & 0x10: code += "CDMA2000 1xRTT, "
    if len(code): code = code[:-2]
    if byte_value & 0x03 > 0: code += " -- WARNING: Reserved bits set"
    return code


'''
Decode a complete or partial UPLMN table
For example, the AT command:
    'AT+CRSM=176,28512,0,0,10'
yields:
    '+CRSM: 144,0,32F405408032F4514080',
which can be decoded with the -p switch:
    'python plmn_codec.py -p 144,0,32F405408032F4514080'
to give:
    1. MCC: 234 MNC: 50 RAT(s): E-UTRAN in WB-S1 mode and NB-S1 mode, GSM and EC-GSM-IoT
    2. MCC: 234 MNC: 15 RAT(s): E-UTRAN in WB-S1 mode and NB-S1 mode, GSM and EC-GSM-IoT

Returns an empty string on error
'''
def decode_table(data):
    # Find the PLMN entry
    parts = data.split(",")
    nets = parts[len(parts) - 1]

    # The entry must contain a multiple of ten characters
    if len(nets) % 10 != 0: return ""

    count = 1
    pairs = ""
    for j in range(0, len(nets), 10):
        mcc, mnc, lte, gsm = plmn_decoder(nets[j:j + 10])
        lte = decode_lte(lte)
        gsm = decode_gsm(gsm)
        pairs += "{}. MCC: {} MNC: {} RAT(s): {}, {}\n".format(count, mcc, mnc, lte, gsm)
        count += 1
    return pairs[:-1]


'''
Show an error message then exit with
the specified error code
'''
def show_err_and_exit(msg, code=1):
    print("[ERROR]",msg)
    sys.exit(code)


'''
Show the utility help
'''
def show_help():
    show_version()
    print("\nEncode and decode Super SIM UPLMN table entries.\n")
    print("Usage:\n\n  codec.py [-p <ENCODED_PLMNS>] [-h] <MCC> <MNC> ... <MCC> <MNC>\n")
    print("Options:\n")
    print("  -p / --plmn     An AT command-ready coded PLMN string. You")
    print("                  can include multiple -p switches.")
    print("  -h / --help     This help information.")
    print()


'''
Show the utility name and version
'''
def show_version():
    print("PLMN Codec 1.0.0 copyright (c) 2022 Twilio")


'''
Primary code
'''
def main(args):
    entries = []
    arg_is_value = False
    last_option = ""

    if len(args):
        for index, item in enumerate(args):
            if arg_is_value:
                arg_is_value = False
                if item[0] == "-":
                    show_err_and_exit("Missing value after option " + last_option)
                result = decode_table(item)
                if result:
                    print(result)
                else:
                    show_err_and_exit("Malformed PLMNS data: " + item)
                continue

            if item.lower() in ("-h", "--help"):
                show_help()
                sys.exit(0)

            if item.lower() in ("-p", "--plmn"):
                last_option = item
                arg_is_value = True
                if index == len(args) - 1:
                    show_err_and_exit("Missing value after option " + last_option)
                continue

            if item[0] == "-":
                show_err_and_exit("Unknown option: " + item)

            entries.append(item)
    else:
        show_version()
        sys.exit(0)

    entry_count = len(entries)
    if entry_count % 2 != 0:
        show_err_and_exit("An MCC-MNC pairing is incomplete")

    if entry_count:
        plmn_list = ""
        for i in range(0, entry_count, 2):
            plmn_list += plmn_encoder(entries[i], entries[i + 1])
        print("AT+CRSM=214,28512,0,0,{},{}".format(len(plmn_list) // 2, plmn_list))


'''
RUNTIME START
'''
if __name__ == '__main__':
    main(sys.argv[1:])
