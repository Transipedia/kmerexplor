#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
Merge multiples countTags outputs

input: countTags output files with 'tag' and 'tag_name' column and one or more counts
output: stdout by default or file if --output used. If suffix file name is '.gz', file
will be gzipped
"""

import os
import sys
import argparse
import gzip
from collections import OrderedDict


__appname__ = "merge_countTags"
__shortdesc__ = "merge multiples countTags output files"
__licence__ = "none"
__version__ = "0.1"
__author__ = "Benoit Guibert <benoit.guibert@free.fr>"


def main():
    """ Function doc """
    args = usage()
    check_output(args)
    table = merge_countTags_files(args)
    output_table(table, args)


def usage():
    """
    Help function with argument parser.
    https://docs.python.org/3/howto/argparse.html?highlight=argparse
    """
    parser = argparse.ArgumentParser()
    ### OPTION
    parser.add_argument("files",
                        help="countTags_file_1, countTags_file_2, [...] ",
                        nargs='+',
                        metavar=('file1 [...]'),
                       )
    parser.add_argument('-o', '--output',
                        default='-',
                        help="Merged file name, compressed with '.gz' suffix (default: stdout)",
                        metavar=('merged file'),
                       )
    ### VERSIONNING
    parser.add_argument('-v', '--version',
                        action='version',
                        version="%(prog)s version: {}".format(__version__)
                       )
    ### Go to "usage()" without arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def check_output(args):
    """ Is output existing ? """
    if os.path.exists(args.output):
        overwrite = input("Output file already exists, overwrite ? [Y,n]: ")
        if overwrite.lower() == 'n':
            sys.exit("Program aborted by user")


def merge_countTags_files(args):
    """ Merge countTags file, gzipped or not. """
    table = {'samples': [], 'counts': OrderedDict()}
    ### for each countTags file
    for i,file in enumerate(args.files):
        ### open file, gzipped or plain text
        try:
            if file[-3:] == '.gz':
                fh = gzip.open(file, 'rt')
            else:
                fh = open(file)
        except FileNotFoundError:
            sys.exit(f"FileNotFoundError: no such file '{file}'.")

        ### from header, pick name of samples
        tag, tag_names, *samples = fh.readline().split('\t')
        samples = [os.path.basename(s).rstrip('\n').rstrip('.gz').rstrip('.fastq') for s in samples]
        table['samples'] += samples
        ### add counts
        for line in fh:
            kmer, ident, *counts = line.split()
            # print(kmer, ident, counts)
            if (kmer, ident) in table['counts']:
                table['counts'][(kmer, ident)] += counts
            else:
                table['counts'][(kmer, ident)] = counts
        fh.close
    return table


def output_table(table, args):
    """ Function doc """
    ### output is stdout
    if args.output == '-':
        print('tag', 'tag_names', *table['samples'], sep='\t')
        for kmer, counts in table['counts'].items():
            print(*kmer, *counts, sep='\t')
    ### output is a file
    else:
        ### compressed file
        if args.output[-3:] == '.gz':
            fh = gzip.open(args.output, 'wt')
        ### Plain text file
        else:
            fh = open(args.output, 'w')

        fh.write("tag\ttag_names\t{}\n".format('\t'.join(table['samples'])))
        for kmer, counts in table['counts'].items():
            fh.write("{}\t{}\n".format('\t'.join(kmer), '\t'.join(counts)))
        fh.close()


if __name__ == "__main__":
    main()
