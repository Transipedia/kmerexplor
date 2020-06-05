#!/bin/bash

# Tool for KmerExploR
#
# find categories from set of kmer



[ -z $1 ] && {
	echo -e "\n usage: $0 tags.tsv[.gz]\t: tags.tsv is output countTags file\n";
	exit;
}

if [ "${1##*.}" == gz ]; then
	zcat $1 | cut -f2 | cut -d'-' -f1 | sort | sed '/tag_names/d' | sed '/^\*$/d' |uniq
else
	cat $1 | cut -f2 | cut -d'-' -f1 | sort | sed '/tag_names/d' | sed '/^\*$/d' |uniq
fi
