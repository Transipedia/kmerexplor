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
import multiprocessing
# from functools import partial       # to send multiple arguments with pool.starmap
import tempfile
import gzip
import glob
import subprocess
import yaml

import info
from common import *
import checkFile as cf
import samples
from counts import Counts
from mk_results import TSV, HTML
from options import usage


APPPATH = os.path.dirname(os.path.realpath(__file__))


def main():
    """ Handle keyboard interrupt commands and launch program """
    ### 1. Manage command line arguments
    args = usage()

    ### load config file
    config = config2dict(args)
    if not config:
        sys.exit(f"Config error: {fileset.config!r} seems to be empty")

    ### If "ctrl C" is set, quit after executing exit_gracefully function
    try:
        run(args, config)
    except KeyboardInterrupt:
        print(f"Process interrupted by user", file=sys.stderr)
        exit_gracefully(args)

'''
def get_user_config(args, fileset):
    if args.config:
        fileset.config = args.config
        if args.tags:
            fileset.tags = args.tags
        desc = f"{args.tags[:-len(ext)]}md"
        if os.path.isfile(desc):
            fileset.desc = desc
'''

def config2dict(args):
    """ Load config yaml file as dict """
    config_file = args.setfiles['config']
    try:
        with open(config_file) as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        sys.exit(f"Error: no such file or directory: {config_file!r}")
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
    # ~ tags_file = get_tags_file(args)
    # ~ tags_file_desc = f"{os.path.splitext(tags_file.rstrip('.gz'))[0]}.md"

    ### 5. If input files are fastq, run countTags (Multiprocessed)
    if files_type == 'fastq':
        ### Compute countTags with multi processing (use --core to specify cores counts)
        sys.stdout.write("\n ✨✨ Starting countTags, please wait.\n\n")
        with multiprocessing.Pool(processes=nprocs) as pool:
            results = pool.starmap_async(do_countTags, [(sample, args) for sample in sample_list])
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
    charts = HTML(counts, args, info, config, args.setfiles['desc'])     # create results in html format

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


def do_countTags(sample, args):
    """ Compute countTags """
    tags_file = args.setfiles['tags']
    countTag_cmd = '{0}/countTags --stranded --alltags --normalize --tag-names --merge-counts \
                    -b --merge-counts-colname {4} -k {1} \
                    --summary {5}/{4}.summary \
                    -i {2} {3} > {5}/{4}.tsv'.format(APPPATH, args.kmer_size, tags_file, sample[0],
                                                    ''.join(sample[1:]), args.counts_dir)
    if args.debug: print(f"{sample[1]}: Start countTags processing.\n{countTag_cmd}")
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


if __name__ == "__main__":
    main()
