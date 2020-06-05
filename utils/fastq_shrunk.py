#!/usr/bin/env python3
# -*- coding:utf8 -*-


import os
import sys
import argparse
import gzip


__appname__ = "fastq_shrunk"
__shortdesc__ = "reduce fastq (can be compressed) as one line per 'factor'"
__licence__ = "none"
__version__ = "0.1"
__author__ = "Benoit Guibert <benoit.guibert@free.fr>"


def main():
    """ Function doc """
    args = usage()
    factor = args.factor * 4 # because 4 lines per read
    for file in args.files:
        fh = open_fastq(file)
        next_valid_bloc = 0
        dest_file = set_dest_file(file, prefix=args.prefix)
        with gzip.open(dest_file, 'wt') as dst_fh:
            for i,line in enumerate(fh):
                if i >= next_valid_bloc:
                    dst_fh.write(line)
                    if i == next_valid_bloc + 3:
                        next_valid_bloc += factor


def set_dest_file(file, prefix='reduced_'):
    """ Function doc """
    dir = os.path.dirname(file)
    filename = f'{prefix}{os.path.basename(file)}'
    return os.path.join(filename)


def usage():
    """
    Help function with argument parser.
    https://docs.python.org/3/howto/argparse.html?highlight=argparse
    """
    parser = argparse.ArgumentParser(description = f'Description: {__shortdesc__}.')
    parser.add_argument("files",
                        help="fastq files to shrunk (gzipped or not)",
                        nargs='+',
                        default=sys.stdin,
                        metavar=('fastq_file'),
                       )
    parser.add_argument("-f", "--factor",
                        help="for 1 read conserved, remove 'factor' reads (default 10)",
                        metavar="factor",
                        default=10,
                        type=int,
                       )
    parser.add_argument("-p", "--prefix",
                        help="prefix to output name (default 'reduced_')",
                        metavar="prefix",
                        default='reduced_',
                        type=str,
                       )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{__version__}"
                       )
    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()


def open_fastq(fastq_file):
    """ Function doc """
    if os.path.isfile(fastq_file):
        if fastq_file[-3:] == '.gz' or fastq_file[-4:] == 'fgz':
            fh = gzip.open(fastq_file, 'rt')
        else:
            fh = open(fastq_file)
    else:
        print("\n FileError: file '{}' not Found.\n".format(fastq_file))
        sys.exit(ending(args))
    return fh


if __name__ == "__main__":
    main()
