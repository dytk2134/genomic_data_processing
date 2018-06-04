#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

"""
Compare the annotation between manual annotation and Entrez gene. 
Changelog:

"""

import sys
import logging
import subprocess
import os

__version__ = '1.0.0'

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(lh)


def fasta_file_sequence_length(fasta_file):
    # get the length of the sequence in the fasta_file
    # sequence_length = {'SequenceID': {'length': Sequence_length, 'state': True}
    # True: finished; False: processing
    sequence_length = dict()
    sequence_id = None
    with open(fasta_file, 'rb') as fasta_file_f:
        for line in fasta_file_f:
            line = line.strip()
            if len(line) != 0:
                if line[0] == '>':
                    lines = line.split(' ')
                    if sequence_id == None:
                        # the first sequence
                        sequence_id = lines[0][1:]
                    elif sequence_id != lines[0][1:]:
                        # next sequence
                        sequence_length[sequence_id]['state'] = True
                        sequence_id = lines[0][1:]
                    if sequence_id not in sequence_length:
                        sequence_length[sequence_id] = {
                            'length': 0,
                            'state': False
                        }
                    else:
                        if sequence_length[sequence_id]['state'] == True:
                            logger.warning('Duplicate ID found! %s' % (sequence_id))
                else:
                    sequence_length[sequence_id]['length'] += len(line)
    return sequence_length


if __name__ == '__main__':
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\
    Compare the annotation between manual annotation and Entrez gene.

    Quick start:
    %(prog)s [something]
    """))
    # argument
    parser.add_argument('-bigwig', '--bigwig', type=str, help='Input Bigwig file', required=True)
    parser.add_argument('-regions', '--regions', type=str, help='List of the specified regions. Regions can be specified as: RNAME[:STARTPOS[-ENDPOS]]', required=True)
    parser.add_argument('-f', '--fasta', type=str, help='the scaffold.txt')
    parser.add_argument('-o', '--out', type=str, help='output_dir')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    # output chrom.size
    with open(os.path.join(args.out, 'chrom.size'), 'w') as chrom_f:
        sequence_length = fasta_file_sequence_length(args.fasta)
        for scaffold in sequence_length:
            chrom_f.write(scaffold + '\t' + str(sequence_length[scaffold]['length']) + '\n')
    Subset_bedGraph = list()
    with open(args.scaffolds, 'r') as scaffold_f:
        for line in scaffold_f:
            line = line.strip()
            if line:
                output_file = os.path.join(args.out, line + '.bedgraph' )
                Subset_bedGraph.append(output_file)
                subprocess.Popen(['bigWigToBedGraph', args.bigwig, output_file, '-chrom='+line]).wait()
    cmd = 'cat %s | sort -k1,1 -k2,2n > %s' % (' '.join(Subset_bedGraph), os.path.join(args.out, 'output.bedgraph'))
    subprocess.call(cmd, shell=True)
    subprocess.Popen(['bedGraphToBigWig', os.path.join(args.out, 'output.bedgraph'), os.path.join(args.out, 'chrom.size'), os.path.join(args.out, 'output.bigwig')]).wait()

    