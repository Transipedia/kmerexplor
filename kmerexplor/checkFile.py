#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
Check if input files are valid fastq or output countTags files.
- fastq, fastq.gz
- tsv, tsv.gz
"""


import os
import sys
import gzip


def main():
    """ You can use this module stand alone. """
    file = File(sys.argv[1])
    if file.is_valid:
        print("{} is valid {} file".format(sys.argv[1], file.type))
    else:
        print(file.errmsg)


class File:
    """ Class doc """

    def __init__(self, file):
        """ Class initialiser """
        self.file = file
        self.errmsg = ""
        self.is_valid, self.type = self._is_valid()


    def _is_valid(self):
        """ Function doc """
        ### Test if file is here
        if not os.path.isfile(self.file):
            if os.path.isdir(self.file):
                self.errmsg = "Error: Is a directory: {0}".format(self.file)
            else:
                self.errmsg = "Error: No such file: {0}".format(self.file)
            return False, None

        ### Test file type and consistency
        ftl = []  # First Three Lines
        ### open fastq or fastq.gz or countTags file
        try:
            with gzip.open(self.file, 'rt') as stream:
                for _ in range(3):
                    ftl.append(stream.readline())
        except OSError:
            with open(self.file) as stream:
                for _ in range(3):
                    ftl.append(stream.readline())
        ### check content of file
        if not self.errmsg:
            try:
                ### Check if fastq file
                if ftl[0][0] == "@" and ftl[1][0] in 'ATCGNatcgn' and ftl[2][0] == "+":
                    return True, 'fastq'
                ### Check if countTags file
                if ftl[0].split()[0] == 'tag' and ftl[1][0] in 'ATCGatcg' and ftl[2][0] in 'ATCGatcg':
                    if ftl[0].split()[1] == 'tag_names':
                        return True, 'countTags'
                    else:
                        self.errmsg = "\n Error, '{}' is valid countTags file, but without 'tag_names' field\n" \
                                      " run countTags with '--tag-names' option\n".format(self.file)
            except IndexError:
                self.errmsg = "Error: too small file: {}".format(self.file)
            else:
                self.errmsg = self.errmsg or "Error: {} does not seem a valid fastq or countTags file.".format(self.file)
        return False, None

if __name__ == "__main__":
    main()
