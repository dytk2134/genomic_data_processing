#!/usr/bin/env python
# Contributed by Li-Mei Chiang <dytk2134 [at] gmail [dot] com> (2018)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

"""

Changelog:

"""

import sys
import logging
import subprocess
import os
import re
import uuid

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

    Extract the specified regions from the bigwig file.

    Quick start:
    %(prog)s -in_b input.bigwig -regions region.txt -f genome.fasta -out_b output.bigwig
    """))
    # argument
    parser.add_argument('-in_b', '--input_bigwig', type=str, help='Input Bigwig file', required=True)
    parser.add_argument('-regions', '--regions', type=str, help='Input a file that contain the list of the specified regions. Regions can be specified as: RNAME[:STARTPOS[-ENDPOS]]', required=True)
    parser.add_argument('-f', '--fasta', type=str, help='The genome fasta')
    parser.add_argument('-out_b', '--output_bigwig', type=str, help='Output Bigwig file', required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    # check if bigwigToBedGraph and bedGraphToBigwig is in the path
    missing_tool = False
    try:
        check = subprocess.Popen(['bigWigToBedGraph'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        logger.error('bigwigToBedGraph is not in the $PATH')
        missing_tool = True
    except subprocess.CalledProcessError:
        pass
    try:
        check = subprocess.Popen(['bedGraphToBigWig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        logger.error('bedGraphToBigwig is not in the $PATH')
        missing_tool = True
    except subprocess.CalledProcessError:
        pass
    if missing_tool:
        sys.exit()

    rm_tmp_list = []
    temp_dir = os.path.dirname(args.input_bigwig)

    # generate chrom.size file
    chrom = os.path.join(temp_dir, 'chrom.size')
    if os.path.exists(chrom):
        chrom += str(uuid.uuid1())
    rm_tmp_list.append(chrom)
    with open(chrom, 'w') as chrom_f:
        sequence_length = fasta_file_sequence_length(args.fasta)
        for scaffold in sequence_length:
            chrom_f.write(scaffold + '\t' + str(sequence_length[scaffold]['length']) + '\n')
    # get bedGraph subset
    Subset_bedGraph = list()
    with open(args.regions, 'r') as scaffold_f:
        for line in scaffold_f:
            line = line.strip()
            if line:
                regions = list(filter(None, re.compile("(\w+):(\d+)-(\d+)").split(line)))
                if len(regions) == 0:
                    logger.warning('Failed to recognize the region: %s' % (line))
                    continue
                else:
                    # chr1:123-456
                    output_file = os.path.join(temp_dir, line + '.bedgraph' )
                    if os.path.exists(output_file):
                        output_file += str(uuid.uuid1())
                    rm_tmp_list.append(output_file)
                    Subset_bedGraph.append(output_file)
                    cmd = ['bigWigToBedGraph', args.input_bigwig, output_file]
                    for idx, value in enumerate(regions):
                        if idx == 0:
                            cmd.append('-chrom=' + regions[0])
                        elif idx == 1:
                            cmd.append('-start=' + regions[1])
                        elif idx == 2:
                            cmd.append('-end=' + regions[2])
                    subprocess.Popen(cmd).wait()
    output_file = os.path.join(temp_dir, 'merge.bedgraph')
    if os.path.exists(output_file):
        output_file += str(uuid.uuid1())
    rm_tmp_list.append(output_file)
    cmd = ['cat'].extend(Subset_bedGraph)
    cat_stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    tmp_out = open(output_file, 'w')
    subprocess.Popen(['sort', '-k1,1', '-k2,2n'], stdin=cat_stdout.stdout, stdout=tmp_out)
    tmp_out.close()
    # convert bedGraph to bigwig
    subprocess.Popen(['bedGraphToBigWig', output_file, chrom, args.output_bigwig]).wait()
    # remove all the tmp file
    for rmfile in rm_tmp_list:
        if os.path.exists(rmfile):
            os.remove(rmfile)
