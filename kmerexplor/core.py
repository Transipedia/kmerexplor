#!/usr/bin/env python3


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
import yaml

from common import *
import checkFile as cf
import samples
from counts import Counts
from mk_results import TSV, HTML
import info
from opt_actions import DumpAction, ShowTagsAction


APPPATH = os.path.dirname(os.path.realpath(__file__))


def main():
    """ Handle keyboard interrupt commands and launch program """
    ### 1. Manage command line arguments
    args = usage()
    ### load config file
    config = config2dict(args)
    ### If "ctrl C" is set, quit after executing exit_gracefully function
    try:
        run(args, config)
    except KeyboardInterrupt:
        print(f"Process interrupted by user", file=sys.stderr)
        exit_gracefully(args)


def config2dict(args):
    """ Load config yaml file as dict """
    try:
        with open(args.config) as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        sys.exit(f"Error: no such file or directory: {args.config!r}")
    except yaml.scanner.ScannerError as err:
        sys.exit(f"Error {err}")


def run(args, config):
    """ Function doc """
    nprocs, files = args.cores, args.files
    if args.debug: print("Arguments:", args)
    ### 1. Define some PATH
    # create directory for temporay files
    args.tmp_dir = tempfile.mkdtemp(prefix=info.APPNAME.lower() + "-", dir=args.tmp_dir)
    # define countTags PATH
    if args.keep_counts:
        ## If the user wants to keep the countTag counts
        args.counts_dir = os.path.join(args.output, 'countTags')
        os.makedirs(args.counts_dir, exist_ok=True)
    else:
        ## Else counts will be removed at the exit_gracefully() function
        args.counts_dir = args.tmp_dir

    ### 2. Test validity files (Multiprocessed)
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
            print(*files_in_error, sep='\n', file=sys.stderr)
            sys.exit(exit_gracefully(args))
        ### If a mix of valid file type are found, exit
        if len(valid_types) != 1:
            print("Multiples valid type found ({}).".format(*valid_types), file=sys.stderr)
        files_type = next(iter(valid_types))

    ### 3. If fastq files, determine paired (if '--paired' argument is specified)
    if files_type == 'fastq':
        sample_list = set_sample_list(files, args, files_type)
        if not sample_list:
            print("\n Error: no samples {} found\n".format('single' if args.single else 'paired'), file=sys.stderr)
            sys.exit(exit_gracefully(args, files_type))

    ### 4. Handle tags
    tags_file = get_tags_file(args)
    tags_file_desc = f"{tags_file.split('.')[0]}.md"

    ### 5. If input files are fastq, run countTags (Multiprocessed)
    if files_type == 'fastq':
        ### Compute countTags with multi processing (use --core to specify cores counts)
        sys.stdout.write("\n ✨✨ Starting countTags, please wait.\n\n")
        with multiprocessing.Pool(processes=nprocs) as pool:
            results = pool.starmap_async(do_countTags, [(sample, tags_file, args) for sample in sample_list])
            results.wait()
        samples_path = [f for f in glob.glob("{}/*.tsv".format(args.counts_dir))]
    else:
        samples_path = args.files

    ### 6. merge countTags tables
    sys.stdout.write("\n ✨✨ Starting merge of counts.\n")
    samples_path.sort()
    counts = Counts(samples_path, args)

    ### 7. Build results as html pages and tsv table
    sys.stdout.write("\n ✨✨ Build output html page.\n")
    table = TSV(counts, args)                                   # create TSV file
    charts = HTML(counts, args, info, config, tags_file_desc)   # create résults in html format

    ### 8. show results
    show_res(args,counts, table.tsvfile, charts.htmlfile, files_type)

    ### 9. exit gracefully program
    exit_gracefully(args, files_type)



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


def do_countTags(sample, tags_file, args):
    """ Compute countTags """
    countTag_cmd = '{0}/countTags --stranded --alltags --normalize --tag-names --merge-counts \
                    -b --merge-counts-colname {4} -k {1} \
                    --summary {5}/{4}.summary \
                    -i {2} {3} > {5}/{4}.tsv'.format(APPPATH, args.kmer_size, tags_file, sample[0],
                                                    ''.join(sample[1:]), args.counts_dir)
    # ~ print(countTag_cmd)
    if args.debug: print("{}: Start countTags processing.\n{}".format(sample[1], countTag_cmd))
    os.popen(countTag_cmd).read()
    print("  {}: countTags processed.".format(''.join(sample[1:])))


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


def usage():
    """
    Help function with argument parser.
    """

    ### Text at the end (command examples)
    epilog  = ("Examples:\n"
            "\n # Mandatory: -p for paired-end or -s for single:\n"
            " %(prog)s -p path/to/*.fastq.gz\n"
            "\n # -c for multithreading, -k to keep counts (input must be fastq):\n"
            " %(prog)s -p -c 16 -k path/to/*.fastq.gz\n"
            "\n # You can skip the counting step thanks to countTags output (see -k option):\n"
            " %(prog)s -p path/to/countTags/files/*.tsv\n"
            "\n # -o to choose your directory output (directory will be created),"
            "\n # --title to show title in results:\n"
            " %(prog)s -p -o output_dir --title 'Title displayed on the html page' dir/*.fastq.gz'\n"
            "\n # Advanced: use your own tag file and config.yaml file:\n"
            " %(prog)s -p --tags my_tags.tsv --config my_config.yaml dir/*.fast.gz\n"
    )
    ### Argparse
    parser = argparse.ArgumentParser(epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # formatter_class=argparse.RawTextHelpFormatter,
    )
    method = parser.add_mutually_exclusive_group(required=True) # method = paired or single
    advanced_group = parser.add_argument_group(title='advanced features')
    special_group = parser.add_argument_group(title='extra features')
    parser.add_argument('files',
                        help='fastq or fastq.gz or tsv countTags output files.',
                        nargs='+',
                        default=sys.stdin,
                        metavar=('<file1> ...'),
    )
    method.add_argument('-s', '--single',
                        action='store_true',
                        help='when samples are single.',
    )
    method.add_argument('-p', '--paired',
                        action='store_true',
                        help='when samples are paired.',
    )
    parser.add_argument('-k', '--kmer-size',
                        type=int,
                        help='kmer size (default 31).',
                        default=31,
                        metavar="<int>",
    )
    parser.add_argument('-K', '--keep-counts',
                        action='store_true',
                        help='keep countTags outputs.',
    )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='debug.',
    )
    ### Depreciated : hidden for the moment
    parser.add_argument('-b', '--builtin-tags',
                        help=argparse.SUPPRESS,
                        default='human-quality',
                        choices=[s for s in BUILTIN_TAGS],
    )
    parser.add_argument('-o', '--output',
                        default='./{}-results'.format(info.APPNAME.lower()),
                        help='output directory (default: "./{}-results").'.format(info.APPNAME.lower()),
                        metavar='<output_dir>',
    )
    parser.add_argument('--tmp-dir',
                        default='/tmp',
                        help='temporary files directory.',
                        metavar='<tmp_dir>',
    )
    ### Deprecated since countTags has the billiard option
    parser.add_argument('--scale',
                        default=1,
                        type=int,
                        help=argparse.SUPPRESS,
                        # help='scale factor, to avoid too small values of counts. (default: 1).',
                        metavar=('scale'),
    )
    advanced_group.add_argument('--config',
                        default=os.path.join(APPPATH, "config.yaml"),
                        help='alternate config yaml file.',
                        metavar='<file_name>',
    )
    advanced_group.add_argument('-t', '--tags',
                        help='alternate tag file.',
                        metavar='<tag_file>',
    )
    advanced_group.add_argument('-a', '--add-tags',
                        help=argparse.SUPPRESS, # 'additional tag file.',
                        metavar='<tag_file>',
    )
    special_group.add_argument('--dump-config',
                        action=DumpAction,
                        arg='file',
                        nargs='?',
                        metavar='file_name',
                        help='dump builtin config file as specified name to current directory and exit (default name: config.yaml).',
    )
    special_group.add_argument('--show-tags',
                        action=ShowTagsAction,
                        help='print builtin categories and predictors and exit.',
                        nargs=0,
    )
    parser.add_argument('--title',
                        default='',
                        help='title to be displayed in the html page.',
                        metavar="<string>"
    )
    parser.add_argument('-y', '--yes', '--assume-yes',
                        action='store_true',
                        help='assume yes to all prompt answers.',
    )
    parser.add_argument('-c', '--cores',
                        default=1,
                        type=int,
                        help='specify the number of files which can be processed simultaneously' +
                        ' by countTags. (default: 1). Valid when inputs are fastq files.',
                        metavar=('<int>'),
    )
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s version: {}'.format(info.VERSION)
    )
    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1 and sys.stdin.isatty():
        parser.print_help()
        sys.exit()
    return parser.parse_args()


if __name__ == "__main__":
    main()
