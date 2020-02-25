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

def fasta_reader(fasta_file):
    magic_number = b'\x1f\x8b\x08'
    fasta_dict = dict()
    # check if file exist
    if not os.path.exists(fasta_file):
        logger.error('%s: No Such file or directory' % (fasta_file))
        sys.exit(1)
    with open(fasta_file, 'rb') as in_f:
        file_start = in_f.read(len(magic_number))
    if file_start.startswith(magic_number):
        in_f = gzip.open(fasta_file, 'rb')
    else:
        in_f = open(fasta_file, 'r')
    fasta_dict = dict()
    fasta_id = None
    for line in in_f:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        line = line.strip()
        if len(line) > 0:
            if line[0] == '>':
                fasta_id = line[1:]
                fasta_dict[fasta_id] = {
                    'sequence_list': list(),
                    'seqs': str()
                }

            else:
                fasta_dict[fasta_id]['sequence_list'].append(line)
                fasta_dict[fasta_id]['seqs'] += line
    in_f.close()
    return fasta_dict

def replace_reserved_char(fasta_id):
    # Linux reserved characters
    reserved_char = set(['/', '>', '<', ':', '&', '\'', '\"', '\\'])
    new_fasta_id = str()
    fasta_ids = fasta_id.split(' ')
    for c in fasta_ids[0]:
        if c in reserved_char:
            new_c = '_'
        else:
            new_c = c
        new_fasta_id += new_c
    return new_fasta_id

def main():
    import argparse
    from textwrap import dedent
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=dedent("""\
    This script is for filtering sequences by sequence length.

    Quick start:
    %(prog)s -i protein_fasta_protein_homolog_model.fasta protein_fasta_protein_knockout_model.fasta -l 50 -p _filtered -r report.txt
    """))
    # argument
    parser.add_argument('-i', '--input_files', nargs='+', help='fasta files', required=True)
    parser.add_argument('-l', '--length', type=int, help='filtered sequences that were <[length] in fasta file, default: 50', default=50)
    parser.add_argument('-p', '--postfix', type=str, help='The filename postfix for modified features, default: _filtered', default='_filtered')
    parser.add_argument('-r', '--report', type=str, help='Generate a table of comparison between old and new IDs. default: report.txt', default='report.txt')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    with open(args.report, 'w') as report_out:
        for input_file in args.input_files:
            report_out.write('#filename: %s\n' % (input_file))
            # header
            outline = ['#Old_Fasta_ID', 'New_Fasta_ID', 'Length', 'Status']
            report_out.write('\t'.join(outline) + '\n')

            filename, fileext = os.path.splitext(input_file)
            output_file = filename + args.postfix + fileext
            fasta_dict = fasta_reader(input_file)
            # filter by length
            with open(output_file, 'w') as out_f:
                for fasta_id in fasta_dict:
                    if len(fasta_dict[fasta_id]['seqs']) < args.length:
                        outline = [fasta_id, 'NA', str(len(fasta_dict[fasta_id]['seqs'])), 'remove']
                    else:
                        new_fasta_id = replace_reserved_char(fasta_id)
                        outline = [fasta_id, new_fasta_id, str(len(fasta_dict[fasta_id]['seqs'])), 'remain']
                        out_f.write('>' + new_fasta_id + '\n')
                        for line in fasta_dict[fasta_id]['sequence_list']:
                            out_f.write(line + '\n')
                    report_out.write('\t'.join(outline) + '\n')

if __name__ == '__main__':
    main()