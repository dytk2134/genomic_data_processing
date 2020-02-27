#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2020)

import os
import sys
import subprocess
import logging

__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

def generate_sample_ids(input_files):
    sample_ids = list()
    for input_file in input_files:
        filename = os.path.splitext(os.path.basename(input_file))[0]
        sample_ids.append(filename)
    return sample_ids

def merge_files(input_files, skip, index, target, default):
    merge_dict = dict()

    for idx, input_file in enumerate(input_files):
        with open(input_file, 'r') as in_f:
            for line_idx, line in enumerate(in_f):
                if line_idx < skip:
                    continue
                else:
                    line = line.strip()
                    if line:
                        tokens = line.split('\t')
                        try:
                            if tokens[index] not in merge_dict:
                                merge_dict[tokens[index]] = [default] * len(input_files)
                            else:
                                if merge_dict[tokens[index]][idx] != default and merge_dict[tokens[index]][idx] != tokens[target]:
                                    logger.warning('Index (Column %d) is not unique. Duplicate values find: %s.' % (index, tokens[index]))
                        except IndexError:
                            logger.error('Index Column: %d, out of range.' % (index))
                            sys.exit(1)
                        try:
                            merge_dict[tokens[index]][idx] = tokens[target]
                        except IndexError:
                            logger.error('Target Column: %d, out of range.' % (target))
                            sys.exit(1)

    return merge_dict

def output_result(merge_dict, sample_ids, output_file):
    with open(output_file, 'w') as out_f:
        # header
        outline = ['#Index']
        outline.extend(sample_ids)
        out_f.write('\t'.join(outline) + '\n')
        # merge result
        for index in merge_dict:
            outline = [index]
            outline.extend(merge_dict[index])
            out_f.write('\t'.join(outline) + '\n')

def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=dedent("""\

    This script is for merging tab-separated values (TSV) files together.

    Quick start:
    %(prog)s -i Sample1.tsv Sample2.tsv -s Sample1 Sample2 -skip 1 -index 0 -targe 1 -default "0" -o merge.tsv
    """))
    # argument
    parser.add_argument('-i', '--input_files', nargs='+', help='Input files', required=True)
    parser.add_argument('-s', '--sample_ids', nargs='+', help='Sample id list')
    parser.add_argument('-skip', '--skip', type=int, help='Skip first N lines in input files, default: 0 (0-based)', default=0)
    parser.add_argument('-index', '--index', type=int, help='Specify the column number for building index, default: 0 (0-based)', default=0)
    parser.add_argument('-target', '--target', type=int, help='Give specific column for merging files, default: 1 (0-based)', default=1)
    parser.add_argument('-default', '--default', type=str, help='Set a default value, default: NA', default='NA')
    parser.add_argument('-o', '--output_file', type=str, help='Specify the output filename. Default: merge.tsv', default='merge.tsv')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # check if items in input_files and sample_ids list is the same
    if args.sample_ids:
        if not len(args.input_files) == len(args.sample_ids):
            logger.error('The number of input files and sample ids is not identical.')
            sys.exit(1)
    else:
        args.sample_ids = generate_sample_ids(args.input_files)
    # check if skip > 0
    if args.skip < 0:
        logger.error('Opthon --skip does not accept negative integer: %d' % (args.skip))
        sys.exit(1)

    # merge
    merge_dict = merge_files(args.input_files, args.skip, args.index, args.target, args.default)

    # write out
    output_result(merge_dict, args.sample_ids, args.output_file)

if __name__ == '__main__':
    main()