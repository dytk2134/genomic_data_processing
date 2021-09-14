#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2020)

import os
import sys
import logging
from Bio import SeqIO

__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)

def abi2fasta(input_files):
    fasta_dict = dict()
    for input_file in input_files:
        record = SeqIO.read(input_file, 'abi')
        if record.id in fasta_dict:
            logger.error('Duplicate Seq ID: %s' % (record.id))
            sys.exit(1)
        fasta_dict[record.id] = record.seq
    return fasta_dict

def write_fasta(fasta_dict, output_prefix):
    output_file = output_prefix + '.fasta'
    with open(output_file, 'w') as out_f:
        for seq_id in fasta_dict:
            out_f.write('>' + seq_id + '\n')
            seqs = [str(fasta_dict[seq_id])[i:i+80] for i in range(0, len(str(fasta_dict[seq_id])), 80)]
            for seq in seqs:
                out_f.write(seq + '\n')
def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\
    This script is for converting ABI files to FASTA files.

    Quick start:
    %(prog)s 
    """))
    # argument
    parser.add_argument('-i', '--input_files', nargs='+', help='Input ABI files', required=True)
    parser.add_argument('-o', '--output_prefix', type=str, help='Specify the output prefix', default='output')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    fasta_dict = abi2fasta(args.input_files)
    write_fasta(fasta_dict, args.output_prefix)



if __name__ == '__main__':
    main()