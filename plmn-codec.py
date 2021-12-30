#!/usr/bin/env python3

'''
Super SIM UPLMN Codec

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
from sys import exit, argv


'''
FUNCTIONS
'''
def plmn_encoder(mcc, mnc):
    # Assemble a PLMN string from MCC, MNC values
    # NOTE: Use 'F' for unused columns, ie. '81' -> '81F'
    if len(mnc) < 3: mnc += "FFF"[:3 - len(mnc)]
    if len(mcc) < 3: mcc += "FFF"[:3 - len(mcc)]
    if len(mnc) > 3: mnc = mnc[:3]
    if len(mcc) > 3: mcc = mcc[:3]

    # Rearrange octets
    plmn = mcc + mnc
    plmn = plmn[1] + plmn[0] + plmn[5] + plmn[2] + plmn[4] + plmn[3]

    # Add the RAT value [E-UTRAN (4G) + GSM]
    return plmn + "4080"


def plmn_decoder(plmn):
    # Turn a PLMN entry into MCC, MNC values (tuple)
    # Rearrange octets and output
    mcc = (plmn[1] + plmn[0] + plmn[3]).replace("F", "")
    mnc = (plmn[5] + plmn[4] + plmn[2]).replace("F", "")
    return (mcc, mnc)


def decode_table(data):
    parts = data.split(",")
    nets = parts[len(parts) - 1]
    if len(nets) % 10 != 0:
        show_err_and_exit("Malformed PLMNS data: " + nets)
        exit(1)

    count = 1
    for i in range(0, len(nets), 10):
        try:
            mcc, mnc = plmn_decoder(nets[i:i + 6])
            print(str(count) + ".","MCC:",mcc,"MNC:",mnc)
            count += 1
        except:
            print("")


def show_err_and_exit(msg, code=1):
    print("[ERROR]",msg)
    exit(code)


def show_help():
    # Show the utility help
    show_version()
    print("\nEncode and decode Super SIM UPLMN table entries.\n")
    print("Usage:\n\n  codec.py [-p <ENCODED_PLMNS>] [-h] <MCC> <MNC> ... <MCC> <MNC>\n")
    print("Options:\n")
    print("  -p / --plmn     An AT command-ready coded PLMN string. You")
    print("                  can include multiple -p switches.")
    print("  -h / --help     This help information.")
    print()


def show_version():
    # Show the utility version info
    print("PLMN codec 1.0.0 copyright (c) 2022 Twilio")


'''
RUNTIME START
'''
if __name__ == '__main__':
    entries = []
    arg_is_value = False
    option = ""

    if len(argv) > 1:
        for index, item in enumerate(argv):
            if index == 0: continue

            if arg_is_value:
                arg_is_value = False
                if item[0] == "-":
                    show_err_and_exit("Missing value after option " + option)
                decode_table(item)
                continue

            if item in ("-h", "--help"):
                show_help()
                exit(0)

            if item in ("-p", "--plmn"):
                option = item
                arg_is_value = True
                if index == len(argv) - 1:
                    show_err_and_exit("Missing value after option " + option)
                continue

            if item[0] == "-":
                show_err_and_exit("Unknown option: " + item)

            entries.append(item)

    if len(entries) % 2 != 0:
        show_err_and_exit("An MCC-MNC pairing is incomplete")

    if len(entries) > 0:
        plmns = ""
        for i in range(0, len(entries), 2):
            plmns += plmn_encoder(entries[i], entries[i + 1])
        print("AT+CRSM=214,28512,0,0," + str(len(plmns) // 2) + "," + plmns)