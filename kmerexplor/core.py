#!/usr/bin/env python3
# -*- coding:utf8 -*-


""" Module Doc

input:
  Mandatory
    - fastq or output countTags files
  Optionnal
    - tags file
    - yaml file
output:
  - counts.tsv
  - kmerexplor.html
  - in lib directory
    - echarts-en.min.js
    - scripts.js
    - styles.css
"""


import os
import sys
import argparse
import multiprocessing
# from functools import partial       # to send multiple arguments with pool.starmap
import tempfile
import gzip
import glob
import subprocess

from common import *
import checkFile as cf
import samples
from counts import Counts
from mk_results import TSV, HTML
import info
from opt_actions import DumpAction, ShowTagsAction


def main():
    """ Function doc """
    ### 1. Manage command line arguments
    args = usage()
    nprocs, files = args.cores, args.files
    if args.debug: print("Arguments:", args)
    ### create directory for temporay files
    args.tmp_dir = tempfile.mkdtemp(prefix=info.APPNAME + "-", dir=args.tmp_dir)

    ### 2. get kmers size
    kmer_size = get_kmers_size(args)

    ### 3. Test validity files (Multiprocessed)
    with multiprocessing.Pool(processes=nprocs) as pool:
        # results = pool.map_async(partial(is_valid, args),files)        # Alternative
        results = pool.starmap_async(is_valid, [(file, args) for file in files])
        results.wait()
        files_in_error = []
        valid_types = set()
        ### Manage results
        for type,errmsg in results.get():
            if type:
                valid_types.add(type)
            else:
                files_in_error.append(errmsg)
        ### If a file(s) is not valid, exit with error message.
        if files_in_error:
            print(*files_in_error, sep='\n')
            sys.exit(ending(args))
        ### If a mix of valid file type are found, exit
        if len(valid_types) != 1:
            print("Multiples valid type found ({}).".format(*valid_types))
        files_type = next(iter(valid_types))

    ### 4. If fastq files, determine paired (if '--paired' argument is specified)
    if files_type == 'fastq':
        sample_list = set_sample_list(files, args, files_type)
        if not sample_list:
            print("\n Error: no samples {} found\n".format('single' if args.single else 'paired'))
            sys.exit(ending(args, files_type))

    ### 5. If input files are fastq, run countTags (Multiprocessed)
    if files_type == 'fastq':
        ### create directory for temporary files and countTags output
        if args.keep_counts:
            ## If the user wants to keep the countTag counts
            args.counts_dir = os.path.join(args.output, 'countTags')
            os.makedirs(args.counts_dir, exist_ok=True)
        else:
            ## Else counts will be removed at the ending() function
            args.counts_dir = args.tmp_dir
        ### Find tags file
        tags_file = get_tags_file(args)
        ### Compute countTags with multi processing (use --core to specify cores counts)
        sys.stderr.write("\n ✨✨ Starting countTags, please wait.\n\n")
        with multiprocessing.Pool(processes=nprocs) as pool:
            results = pool.starmap_async(do_countTags, [(sample, tags_file, kmer_size, args) for sample in sample_list])
            results.wait()
        samples_path = [f for f in glob.glob("{}/*.tsv".format(args.counts_dir))]
    else:
        samples_path = args.files

    ### 6. merge countTags tables
    sys.stderr.write("\n ✨✨ Starting merge of counts.\n")
    samples_path.sort()
    counts = Counts(samples_path, args)

    ### 7. Build results as html pages and tsv table
    sys.stderr.write("\n ✨✨ Build output html page.\n")
    table = TSV(counts, args)             # create TSV file
    charts = HTML(counts, args, info)      # create résults in html format

    ### 8. show results
    show_res(args,counts, table.tsvfile, charts.htmlfile, files_type)

    ### 9. ending program
    ending(args, files_type)


def usage():
    """
    Help function with argument parser.
    """

    ### Text at the end (command examples)
    epilog  = "Examples:\n"
    epilog += "\n # Mandatory: -p for paired-end or -s for single:\n"
    epilog += " %(prog)s -p path/to/*.fastq.gz\n"
    epilog += "\n # -c for multithreading, -k to keep counts (input must be fastq):\n"
    epilog += " %(prog)s -p -c 16 -k path/to/*.fastq.gz\n"
    epilog += "\n # You can skip the counting step thanks to countTags output (see -k option):\n"
    epilog += " %(prog)s -p path/to/countTags/files/*.tsv\n"
    epilog += "\n # -o to choose your directory output (directory will be created),"
    epilog += "\n # --title to show title in results:\n"
    epilog += " %(prog)s -p -o output_dir --title 'Title in html page dir/*.fastq.gz'\n"
    epilog += "\n # Advanced: use your own tag file and config.yaml file:\n"
    epilog += " %(prog)s -p --tags my_tags.tsv --config my_config.yaml dir/*.fast.gz\n"
    ### Argparse
    parser = argparse.ArgumentParser(epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # formatter_class=argparse.RawTextHelpFormatter,
    )
    method = parser.add_mutually_exclusive_group(required=True) # method = paired or single
    special_group = parser.add_argument_group(title='Extra features')
    parser.add_argument('files',
                        help='fastq or fastq.gz or tsv countTag files',
                        nargs='+',
                        default=sys.stdin,
                        metavar=('files'),
    )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='debug',
    )
    parser.add_argument('-t', '--tags',
                        help='tag file.',
    )
    ### Hidden at this time
    parser.add_argument('-S', '--specie',
                        help=argparse.SUPPRESS,
                        default='human',
                        choices=[s for s in SPECIES],
    )
    method.add_argument('-s', '--single',
                        action='store_true',
                        help='when samples are single.',
    )
    method.add_argument('-p', '--paired',
                        action='store_true',
                        help='when samples are paired.',
    )
    parser.add_argument('-o', '--output',
                        default='./{}-results'.format(info.APPNAME.lower()),
                        help='output directory (default: "./{}-results").'.format(info.APPNAME.lower()),
                        metavar='output_dir',
    )
    parser.add_argument('-k', '--keep-counts',
                        action='store_true',
                        help='keep countTags outputs.',
    )
    parser.add_argument('--tmp-dir',
                        default='/tmp',
                        help='temporary files directory.',
                        metavar='tmp_dir',
    )
    ### Deprecated since countTags has the billiard option
    parser.add_argument('--scale',
                        default=1,
                        type=int,
                        help='scale factor, to avoid too small values of counts. (default: 1).',
                        metavar=('scale'),
    )
    parser.add_argument('--config',
                        default='config.yaml',
                        help='alternate config yaml file of each category (default: built-in "config.yaml").',
                        metavar='config.yaml',
    )
    special_group.add_argument('--dump-config',
                        action=DumpAction,
                        arg='file',
                        nargs='?',
                        metavar='config.yaml',
                        help='dump builtin config file as specified name to current directory and exit (default name: config.yaml).',
    )
    special_group.add_argument('--show-tags',
                        action=ShowTagsAction,
                        help='print builtin categories and predictors and exit.',
                        nargs=0,
    )
    parser.add_argument('--title',
                        default='',
                        help='Title to be displayed in the html page.',
    )
    parser.add_argument('-y', '--yes', '--assume-yes',
                        action='store_true',
                        help='assume yes to all prompt answers.',
    )
    parser.add_argument('-c', '--cores',
                        default=1,
                        type=int,
                        help='specifies the number of files which can be processed simultaneously' +
                        ' by countTags. (default: 1). Valid when inputs are fastq file.',
                        metavar=('cores'),
    )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s version: {}.'.format(info.VERSION)
    )
    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1 and sys.stdin.isatty():
        parser.print_help()
        sys.exit()
    return parser.parse_args()


def is_valid(file, args):
    """ Function doc """
    f = cf.File(file)
    if args.debug and f.is_valid:
        print("{} is valid {} file.".format(file, f.type))
    return f.type, f.errmsg


def set_sample_list(files, args, files_type):
    """ Function doc """
    if files_type == 'fastq':
        return samples.find(files, args)


def get_kmers_size(args):
    """ Function doc """
    tags_file = get_tags_file(args)
    ### tags file is gzipped
    if tags_file[-3:] == '.gz':
        with gzip.open(tags_file) as tagsf:
            return len(tagsf.readline().split()[0])
    ### tags file is plain text
    else:
        with open(tags_file) as tagsf:
            return len(tagsf.readline().split()[0])


def do_countTags(sample, tags_file, kmer_size, args):
    """ Compute countTags """
    countTag_cmd = '{0}/countTags --stranded --normalize --tag-names --merge-counts \
                    -b --merge-counts-colname {4} -k {1} \
                    --summary {5}/{4}.summary \
                    -i {2} {3} > {5}/{4}.tsv'.format(APPPATH, kmer_size, tags_file, sample[0],
                                                    ''.join(sample[1:]), args.counts_dir)
    if args.debug: print("{}: Start countTag processing.\n{}".format(sample[1], countTag_cmd))
    os.system(countTag_cmd)
    print("  {}: countTag processed.".format(''.join(sample[1:])))


def show_res(args, tags, tsvfile, htmlfile, files_type):
    """ output """
    print("\n ✨✨ Work is done, show:\n\n {}\n {}".format(os.path.abspath(tsvfile),
                                                           os.path.abspath(htmlfile)))
    if args.keep_counts and files_type == 'fastq' : print(" {}/".format(os.path.abspath(args.counts_dir)))
    print("\n")
    ### Launch results in a browser if possible
    try:
        subprocess.Popen(['x-www-browser', htmlfile])
    except:
        pass



if __name__ == "__main__":
    main()
