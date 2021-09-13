#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2020)

import os
import sys
import pandas as pd
import pyreadstat
import logging

__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

def sav_to_tsv(input_file, output_file):
    if not os.path.exists(input_file):
        logger.error('%s: No Such file or directory' % (input_file))
        sys.exit(1)
    # read sav file
    df, meta = pyreadstat.read_sav(input_file)
    # add sav tags to first row
    df.loc[-1] = meta.column_labels
    df.index = df.index + 1
    df.sort_index(inplace=True)
    # write out
    df.to_csv(output_file, sep='\t', index=False)

def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=dedent("""\

    example:
    %(prog)s -i input.sav -o output.tsv

    version:
    """ + __version__))
    # argument
    parser.add_argument('-i', '--input', type=str, help='input sav', required=True)
    parser.add_argument('-o', '--output', type=str, default='output.tsv', help='output tsv')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    sav_to_tsv(args.input, args.output)


if __name__ == '__main__':
    main()