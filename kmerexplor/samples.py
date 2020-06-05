#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
From a bunch of files, determine the samples weither the files are single or paired.
"""

import os
import sys
import re

TAGS = [
    ('_R1_001', '_R2_001', 'illumina'),
    ('_1.fastq', '_2.fastq', 'bio2m'),
    ('_1.fq', '_2.fq', 'other'),
    ('_1.tsv', '_2.tsv', 'countTags'),
]

def main():
    """ You can use this module stand alone. """
    #sample_list = find_paired(sys.argv[1:])
    class args:
        single = False
        yes = True
    sample_list = find(sys.argv[1:], args)
    print(*sample_list, sep="\n  ")


def find(files, args):
    """ Function doc """
    if args.single:
        return find_single(files)
    return find_paired(files, args)


def find_paired(files, args):
    """ Function doc """
    samples = []
    control = []
    for file in files:
        ### if file seems paired file (see TAGS)
        for tag in TAGS:
            if tag[0] in file:
                ### set mate file
                mate = file.replace(tag[0], tag[1])
                if os.path.isfile(mate):
                    sample = os.path.basename(re.sub('{}.*'.format(tag[0]), '', file))
                    samples.append((file, sample, '_1'))
                    samples.append((mate, sample, '_2'))
                    ### to control missing files
                    control += [file, mate]
    ### Control files
    f_not_found = []
    for file in files:
        if file not in control:
            f_not_found.append(file)
    if not control:
        msg = "\n No paired files found in {}, you may want to use '--single' argument.\n" \
                .format(os.path.dirname(files[0]))
        sys.exit(msg)
    if f_not_found:
        msg = "\n Be carefull, one or more file seems not be paired."
        msg += "\n No mate found for:"
        print(msg, *f_not_found, sep='\n\t')
        if not args.yes:
            valid = input("\n Would you like to continue? (these files will not be processed) [Y,n] ")
            if valid.lower() == 'n':
                sys.exit("\n Program aborted by user")
        else:
            if not args.yes:
                print("\n Program continues")
    return samples


def find_single(files):
    """ Function doc """
    samples = []
    for file in files:
        sample = os.path.basename(file)
        sample, ext = os.path.splitext(sample)
        if ext == '.gz':
            sample, ext = os.path.splitext(sample)
        if sample in samples:
            sys.exit("Maybe two files in the directory, with one compressed ({})".format(file))
        samples.append((file, sample))
    return samples


if __name__ == "__main__":
    main()
