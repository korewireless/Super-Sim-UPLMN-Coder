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
    return (mcc, mnc)


'''
Decode a complete or partial UPLMN table
For example, the AT command:
    'AT+CRSM=176,28512,0,0,10'
yields:
    '+CRSM: 144,0,32F405408032F4514080',
which can be decoded with the -p switch:
    'python plmn_codec.py -p 144,0,32F405408032F4514080'
to give:
    1. MCC: 234 MNC: 50
    2. MCC: 234 MNC: 15
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
        mcc, mnc = plmn_decoder(nets[j:j + 6])
        pairs += (str(count) + ". MCC: " + mcc + " MNC: " + mnc + "\n")
        count += 1
    return pairs


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
RUNTIME START
'''
if __name__ == '__main__':
    entries = []
    arg_is_value = False
    last_option = ""

    if len(sys.argv) > 1:
        for index, item in enumerate(sys.argv):
            if index == 0: continue

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

            if item in ("-h", "--help"):
                show_help()
                sys.exit(0)

            if item in ("-p", "--plmn"):
                last_option = item
                arg_is_value = True
                if index == len(sys.argv) - 1:
                    show_err_and_exit("Missing value after option " + last_option)
                continue

            if item[0] == "-":
                show_err_and_exit("Unknown option: " + item)

            entries.append(item)

    if len(entries) % 2 != 0:
        show_err_and_exit("An MCC-MNC pairing is incomplete")

    if len(entries) > 0:
        plmn_list = ""
        for i in range(0, len(entries), 2):
            plmn_list += plmn_encoder(entries[i], entries[i + 1])
        print("AT+CRSM=214,28512,0,0," + str(len(plmn_list) // 2) + "," + plmn_list)
