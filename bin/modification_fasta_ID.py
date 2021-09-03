#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2020)

import os
import sys
import gzip
import logging

__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)


def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=dedent("""\
    This script is used to modify ID in FASTA file

    Quick start:
    %(prog)s 
    """))
    # argument
    parser.add_argument('-i', '--input_file', type=str, help='input FASTA file ', required=True)
    parser.add_argument('-o', '--output_file', type=str, help='Specify the output filename', required=True)
    parser.add_argument('-s', '--summary', type=str, help='summary', required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    ids_dict = dict()
    transfor_dict = {
        '1': 'A',
        '2': 'B',
        '3': 'C',
        '4': 'D',
        '5': 'E',
        '6': 'F',
        '7': 'G',
        '8': 'I',
        '9': 'J',
        '0': 'K'
    }
    with open(args.output_file, 'w') as out_f:
        with open(args.input_file, 'r') as in_f:
            for line in in_f:
                line = line.strip()
                if line:
                    if line[0] == '>':
                        lines = line.split(' ')
                        IDs = lines[0][1:]
                        newIDs = str()
                        for i in IDs:
                            if i in transfor_dict:
                                newIDs += transfor_dict[i]
                            else:
                                newIDs += i
                        ids_dict[IDs] = newIDs
                        line = '>' + newIDs
                out_f.write(line + '\n')

    with open(args.summary, 'w') as out_f:
        for ID in ids_dict:
            outline = [ID, ids_dict[ID]]
            out_f.write('\t'.join(outline) + '\n')
if __name__ == '__main__':
    main()
