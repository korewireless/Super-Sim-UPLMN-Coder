# Super SIM UPLMN Codec

A basic but handy SIM UPLMN (User-controlled Public Land Mobile Network) table coder and decoder. Use it to generate and check Super SIM UPLMN table entries. For more details see [**How and Why You Can Set Super SIM’s Network Attach Priority List**](https://www.twilio.com/docs/iot/supersim/how-and-why-to-set-super-sims-uplmn-table).

## Requirements

This utility requires Python 3 installed on your system.

## Usage

Call the utility from the command line. Use it to prepare new UPLMN table entries and to check existing entries.

#### Encoding

To encode MCC-MNC (Mobile Country Code, Mobile Network Code) pairs, supply a sequence of these as arguments. You must include each pair in this order: MCC first, followed by MNC.

Values are not checked for validity.

**Examples**

```
$ python plmn_codec.py 310 410
AT+CRSM=214,28512,0,0,5,1300144080
```

```
$ python plmn_codec.py 310 410 310 260
AT+CRSM=214,28512,0,0,10,13001440801300624080
```

```
$ python plmn_codec.py 310 410 310
[ERROR] An MCC-MNC pairing is incomplete
```

The output is in the form of an usage-ready AT command set to write (`214`) the entered values to the SIM’s UPLMN table (`28512`) with an offset of zero (`0,0` — MSB and LSB of the offset), ie. at the start of the table. You can edit the offset before sending the command if you need to insert values further into the UPLMN table. The number of bytes (`10`) is calculated and added to the command for you.

Each MCC-MNC paring is appended with RAT (Radio Access Technology) values, ie. `4080`. This indicates a primary preferred RAT of 4G (`40`) and a secondary RAT of GSM (`80`). For full details of the encoding, please see [**ETSI Technical Specification 131 102**](https://www.etsi.org/deliver/etsi_ts/131100_131199/131102/15.05.00_60/ts_131102v150500p.pdf).


#### Decoding

You can decode UPLMN table entries, or entire tables, with the `-p` option.

**Examples**

```
$ python plmn_codec.py -p '+CRSM: 144,0,1300144080'
1 MCC: 310 MNC: 410
```

```
$ python plmn_codec.py -p AT+CRSM=214,28512,0,0,10,13006240801300144080
1 MCC: 310 MNC: 260
2 MCC: 310 MNC: 410
```

```
$ python plmn_codec.py -p 13006240801300144080
1 MCC: 310 MNC: 260
2 MCC: 310 MNC: 410
```

```
$ python plmn_codec.py -p 1300624
[ERROR] Malformed PLMNS data: 1300624
```

You can include as many `-p` options and accompanying arguments as you require.

## Copyright

This source code is copyright 2022, Twilio Inc.

## Licence

This source code is made available under the terms of the [MIT Licence](LICENSE.md).