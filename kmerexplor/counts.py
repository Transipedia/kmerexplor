#!/usr/bin/env python3
# -*- coding:utf8 -*-

"""
Build an objet with counts.
"""


import os
import sys
import gzip
import math
from statistics import mean, median


def main():
    """ You can use this module stand alone. """

    ### Define some variables, they must be in tsv tags file passed as input
    sample = 'A'
    seq_type = 'Orientation'
    seq_id = 'VPS29'

    ### You may create args
    class args:
        method = 'mean'
        single = False
        scale = 10
    counts_files = sys.argv[1:] # files are countTags output
    counts = Counts(counts_files, args)

    print('SAMPLES (AS SINGLE):', counts.tags['samples']['single'])
    print('SAMPLES (AS PAIRED):', counts.tags['samples']['paired'])
    print('TYPES:', *counts.types)
    print('META:', counts.tags['meta'])
    print("MODE:", counts.mode)
    print(f"----------------\n get_by_sample({sample}, {seq_type}):\n", counts.get_by_sample(sample, seq_type))
    print(f"----------------\n get_counts_by_sample('{seq_type}'):\n", counts.get_counts_by_sample(seq_type))
    print(f"----------------\n get_by_category('{seq_type}'):\n", *counts.get_by_category(seq_type))
    print(f"----------------\n get_by_category in single mode('{seq_type}'):\n", *counts.get_by_category(seq_type, mode='single'))
    print('----------------\n')
    for k, v in counts.tags['counts'][seq_type][seq_id].items():
        print(seq_type, seq_id, k, v)


class Counts:
    """
    Create a dictionay of tags
    """

    def __init__(self, counts_files, args):
        """ Class initialiser """
        self.tags = {'samples': {}, 'counts': {}, 'meta': {}}
        self.counts_files = counts_files
        self.args = args
        self.mode = 'single' if args.single else 'paired'
        self.scale = args.scale
        ### Check counts files
        # self._check_count_files()
        ### Add entry for samples
        self._get_samples_names()
        ### merge tags
        self.tags = self._do_merge_counts(args)
        ### compute mean of counts
        self._set_counts_mean()
        ### if paired samples, add dict entry with sum for foward and reverse
        if self.mode == 'paired':
            self._match_paired()
        ### Check if tags dict is consistant
        # self._check_merge()
        ### minimize counts
        self._minimize(args)
        ### some attributes to easier access
        self.samples = [sample for sample in self.tags['samples'][self.mode]]
        self.fastq = [sample for sample in self.tags['samples']['single']]
        self.types = [seq_type for seq_type in self.tags['counts']]
        self.meta = [meta for meta in self.tags['meta']]


    def _do_merge_counts(self, args):
        """ Function doc """
        scale           = self.scale or 1
        tags            = self.tags
        pos             = 0         # position of first sample
        n_sample        = 0         # number of sample
        for index, file in enumerate(self.counts_files):
            if file[-2:].lower() == 'gz':
                fh = gzip.open(file, 'tr')
            else:
                fh = open(file)
            ### Add data
            for row in fh:
                ### Avoid first line in counts and define counts pos
                if row[0:4] == 'tag\t':
                    pos += n_sample
                    n_sample = len(row.split()[2:])
                    continue
                ### split line
                row = row.rstrip().split('\t')
                ### The kmer can be representative of several tag names (seq-type + seq-id + queue)
                tagnames = row[1].split(',')
                for tagname in tagnames:
                    try:
                        seq_type = tagname.split('-')[0]
                        seq_id = tagname.split('-')[1]
                        seq_counts = row[2:]
                    except IndexError:
                        sys.exit(f"\n IndexError: missing at least one field in '{file}' file (2 fields expected, hyphen separated).")
                    ### Add sequence type if not exists (ex: sex, orientation)
                    if not seq_type in tags['counts']:
                        tags['counts'][seq_type] = {}
                    ### Add seq_id (often gene) if not exist (ex: VPS29, HIST1H2BF)
                    if not seq_id in tags['counts'][seq_type]:
                        tags['counts'][seq_type][seq_id] = {'single':[0 for _ in range(len(self.tags['samples']['single']))]}
                        tags['counts'][seq_type][seq_id]['number_counts'] = 0       # number of counts per seq_id
                    ### Add count value
                    for ii, count in enumerate(seq_counts):
                        ### Store count
                        tags['counts'][seq_type][seq_id]['single'][ii+pos] += float(count) * scale
                    ### Store number of counts for this seq_id
                    if pos == 0:
                        tags['counts'][seq_type][seq_id]['number_counts'] += 1
            fh.close()

        ### if first sample, add rows counts in metadata, verify if same count for others samples
        nrows = 0
        for idx,seq_type in enumerate(tags['counts']):
            for seq_id in tags['counts'][seq_type]:
                nrows += len(tags['counts'][seq_type][seq_id])
        if 'nrow' not in tags['meta']:
            tags['meta']['nrow'] = nrows
        else:
            if nrows != tags['meta']['nrow']:
                print("\n InternalError: rows count should be the same for each sample.")
                print(" {} found for {} ({} expected).\n".format(nrows, tags['samples']['single'][idx] , tags['meta']['nrow']))
                sys.exit()
        return tags


    def _set_counts_mean(self):
        """ Compute average for each count """
        for seq_type in self.tags['counts']:
            for seq_id in self.tags['counts'][seq_type]:
                counts = self.tags['counts'][seq_type][seq_id]['single']
                ncounts = self.tags['counts'][seq_type][seq_id]['number_counts']
                for i,count in enumerate(counts):
                    self.tags['counts'][seq_type][seq_id]['single'][i] = count / ncounts


    def _match_paired(self):
        """ Sum sample and his mate and add into dict """
        for seq_type in self.tags['counts']:
            for seq_id in self.tags['counts'][seq_type]:
                #for seq_def in self.tags['counts'][seq_type][seq_id]:
                counts = self.tags['counts'][seq_type][seq_id]['single']
                for i in range(0, len(counts), 2):
                    if not 'paired' in self.tags['counts'][seq_type][seq_id]:
                        self.tags['counts'][seq_type][seq_id]['paired'] = []
                    self.tags['counts'][seq_type][seq_id]['paired'].append(counts[i]+counts[i+1])


    def _minimize(self, args):
        """ Minimize counts """
        precision=4
        for seq_type in self.tags['counts']:
            for seq_id in self.tags['counts'][seq_type]:
                for mode, counts in self.tags['counts'][seq_type][seq_id].items():
                    if mode == 'single' or mode == 'paired':
                        for i,n in enumerate(counts):
                            if n:
                                mod = 0 if n < 1 else 1
                                p = math.pow(10,int(-math.log10(n))+precision-mod)
                                self.tags['counts'][seq_type][seq_id][mode][i] = round(n*p)/p


    def _get_samples_names(self):
        """ get counts for a sample """
        self.tags['samples']['single'] = []
        self.tags['samples']['paired'] = []
        ### Always define sample name 'single' (Required for Orientation category)
        for index, file in enumerate(self.counts_files):
            ### pick column names in the first line ('tag', 'tag_names', 'col1', 'col...', )
            if file[-2:].lower() == 'gz':
                fh = gzip.open(file, 'rt')
            else:
                fh = open(file)
            sample_names = fh.readline().rstrip().split('\t')[2:]
            for sample_name in sample_names:
                self._append_samples_names_to_count_dict(sample_name)
            fh.close
        ### If paired, add merge column names
        if self.mode == 'paired':
            paired_names = [name[:-2] for i, name in enumerate(self.tags['samples']['single']) if i % 2 == 0]
            self.tags['samples']['paired'] = paired_names


    def _append_samples_names_to_count_dict(self, sample_name):
        """ append sample name to counts dict """
        sample_name = os.path.basename(sample_name).rstrip('.fastq.gz').rstrip('.fq.gz').rstrip('.fastq')
        ### Add to samples list
        if not sample_name in self.tags['samples']['single']:
            self.tags['samples']['single'].append(sample_name)


    def _check_count_files(self):
        """ Control if files produced by countTags have same size """
        file_sizes = set()
        for file in self.counts_files:
            file_sizes.add(os.popen('wc -l < ' + file).readline())

        if len(file_sizes) > 1:
            print('\n Error : one or more of countTags output have not the same size.')
            print(" Reload command with '-d' option and check countTags outputs.\n")
            sys.exit()

        if not file_sizes:
            print('\n Internal error: no output countTags file found.\n')
            sys.exit()


    def get_by_category(self, seq_type, mode=None):
        """ get counts by category """
        results = []
        ### By default, use with invoked mode (paired or single)
        mode = mode or self.mode
        ### get counts by category
        if seq_type in self.tags['counts']:
            for seq_id in self.tags['counts'][seq_type]:
                counts = self.tags['counts'][seq_type][seq_id][mode]
                results.append((seq_id, counts))
            return results
        else:
            errmsg = " Category warning: {}, defined in {}, not found in output countTags.\n".format(seq_type, self.args.config)
            print(errmsg)
            return None


    def get_counts_by_sample(self, seq_type, mode=None):
        """ Function doc """
        results = [ {sample: []} for sample in self.samples ]
        ### By default, use with invoked mode (paired or single)
        mode = mode or self.mode
        ### if sequence category is mentioned (ex: 'Gender')
        if not seq_type in self.types:
            sys.exit("\n Error: sequence type '{}' not found among these: {}.\n".format(seq_type, self.types))
        for seq_id in self.tags['counts'][seq_type]:
            counts = self.tags['counts'][seq_type][seq_id][mode]
            for i, count in enumerate(counts):
                if seq_id[-4:] == '_rev':
                    pass
                else:
                    results[i].get(self.samples[i]).append(count)
        return results


    def get_by_sample(self, sample_name, seq_type=None, mode=None):
        """ Function doc """
        results = {}
        ### By default, use with invoked mode (paired or single)
        mode = mode or self.mode
        ### if not samples, return error and quit
        if not sample_name in self.samples:
            sys.exit("\n Error: sample '{}' not found among these: {}.\n".format(sample_name, self.samples))
        ### index of sample
        sample_index = self.samples.index(sample_name)
        ### if sequence type is mentioned (ex: 'sex')
        if seq_type:
            if not seq_type in self.types:
                sys.exit("\n Error: sequence type '{}' not found among these: {}.\n".format(seq_type, self.types))
            for seq_id in self.tags['counts'][seq_type]:
                for seq_id in self.tags['counts'][seq_type]:
                    results[seq_id] = self.tags['counts'][seq_type][seq_id][mode][sample_index]
        ### without sequence type
        else:
            for seq_type in self.tags['counts']:
                if seq_type not in results:
                    results[seq_type] = {}
                for seq_id in self.tags['counts'][seq_type]:
                    if seq_id not in results:
                        results[seq_type][seq_id] = {}
                    for seq_id in self.tags['counts'][seq_type]:
                        results[seq_type][seq_id] = self.tags['counts'][seq_type][seq_id][mode][sample_index]
        return results


    def to_file(self, output_dir='.', output_file='table.tsv', sep='\t'):
        """ write in tabuled file """
        rows = ""
        ### Add columns name at firt row
        rows += sep.join(['type', 'seq_id']) + sep + sep.join(self.samples) + '\n'
        ### Add data in rows
        for seq_type in self.tags['counts']:
            for seq_id in self.tags['counts'][seq_type]:
                counts = self.tags['counts'][seq_type][seq_id][self.mode]
                ### counts list to string
                counts = sep.join([str(count) for count in counts])
                rows += sep.join((seq_type, seq_id, counts)) + "\n"

        filepath = os.path.join(output_dir, output_file)
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        with open(filepath, 'w') as stream:
            stream.write(rows)
        return os.path.join(output_dir, output_file)


if __name__ == "__main__":
    main()
