# KmerExploR


- [Description](#description)
- [Installation](#installation)
- [Input](#input)
- [Output](#output)
- [Examples](#examples)
- [Usage](#usage)
- [Options](#options)
	- [-k --keep-counts](#k---keep-counts)
	- [--tags tags_file](#tags-tags_file)
	- [--config config.yaml](#config-config.yaml)


## Description


From a bunch of fastq or countTags output files, KmerExploR provides information on samples analyzed by NGS, such as gender, whether the analysis is based on oriented or non-oriented sequencing, whether mycoplasma is present, and much more.

`KmerExploR` uses a set of reference kmers.

We will generally use the existing kmer set. But it is also possible to create your own kmers reference file, for example for a search on a particular species.

This code is under **GPL3** licence.


## Installation

`KmerExploR` needs `yaml` python module, `pip` automatically install it, not `git`. 

You may install kmerexplor with pip: 

```
# as user
python3 -m pip install --user kmerexplor

# as root or in virtualenv
python3 -m pip install kmerexplor
```
**Nota**: using pip as user without virtual environment, make sure PATH variable include `~/.local/bin`.

or by cloning repository:

```
# clone the repository
git clone https://github.com/Transipedia/kmerexplor.git

# create link somewhere in your PATH
sudo ln -s $PWD/kmerexplor/kmerexpor/core.py /usr/local/bin/kmerexplor
```



## Input


**required:**

- fastq or outputs from countTags (gzipped or not). 

For paired samples, fastq names must be in illumina format (`_R1_001` and `_R2_001`), or they must end by `_1.fastq[.gz]` and `2.fastq[.gz]`. `countTags` files must end by `tsv[.gz]`. `countTags` files can be aggregate in a multiculumn single file.

**optional:**

- yaml configuration file.
- tags file.

Both must match (see below).


## Output

By default, outputs are produced in directory `kmerexplor-results`.

- `table.tsv` : tab separated table of results.
- `kmerexplor.html` : graphical results.
- `lib` directory contains css and javascript code associated with KmerExploR.html
- if `--keep-counts` option is specified `countTags` directory contains __countTags__ output. 


## Examples:

Mandatory: `-p` for paired-end or `-s` for single:

```
kmerexplor -p path/to/*.fastq.gz
```
 
`-c` for multithreading, `-k` to keep counts (input must be fastq):

``` 
kmerexplor -p -c 16 -k path/to/*.fastq.gz
```

You can skip the count step thanks to countTags output (see `-k` option):

```
kmerexplor -p path/to/countTags/files/*.tsv
```

`-o` to choose a directory output, `--title` to show title in results:

```
kmerexplor -p -o output_dir --title 'Title in html page dir/*.fastq.gz'
```

Advanced: use your own tag file and associated config.yaml file:

```
kmerexplor -p -tags my_tags.tsv --config my_config.yaml dir/*.fast.gz
```

## Usage

 
Without options or with `--help`, `KmerExploR` returns Help

 
 ```
usage: kmerexplor [-h] [-d] [-t TAGS] (-s | -p) [-o output_dir] [-k]
                [--tmp-dir tmp_dir] [--scale scale] [--config config.yaml]
                [--title TITLE] [-y] [-c cores] [-v]
                files [files ...]

positional arguments:
  files                 fastq or fastq.gz or tsv countTag files

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           debug
  -t TAGS, --tags TAGS  tag file
  -s, --single          when samples are single
  -p, --paired          when samples are paired
  -o output_dir, --output output_dir
                        output directory (default: "./KmerExploR-results")
  -k, --keep-counts     keep countTags outputs
  --tmp-dir tmp_dir     Temporary files directory
  --scale scale         Scale factor, to avoid too small values of counts.
                        (default: 1)
  --config config.yaml  Configuration yaml file of each category (default:
                        "lib/config.yaml")
  --title TITLE         Title to be displayed in the html page
  -y, --yes, --assume-yes
                        Assume yes to all prompt answers
  -c cores, --cores cores
                        Number of CPUs cores (default: 1). Valid especially
                        when starting from fastq file.
  -v, --version         show program's version number and exit

 ```
 
## Options

### -k --keep-counts

By default, `KmerExploR` deletes intermediate files, particularly countTags output (when input files are fastq files). You could keep countTags output files by using `--keep-counts`option. The location of the countTags output files will then be displayed on the standard output.

countTags outputs are located in a directory named `countTags`, located in `kmerexplor-results` by default or specified by `-o` option.

Then when you run KmerExploR with this directory as argument (`kmerexplor-results/countTags/*.tsv` by default), `countTags` step is bypassed, saving a lot of time.

### --tags tags_file

KmerExploR uses an internal default tag file. You can specify another tags file with `--tags` option with as alternate tags file (compressed or not).

#### Tags file format

Tags file format is tabuled in 2 columns.

- column 1 : kmer
- column 2 : description, dashes "-" are important, because they define a structure. 

Example : 


```
AACGCCGCGCGTGACAACAAGAAGACCAGGA Histone-H2AFJ-ENST00000501744.2.fa.kmer58
```

- `AACGCCGCGCGTGACAACAAGAAGACCAGGA` : kmer
- `Histone` : category
- `H2AFJ` : seq_id
- `ENST00000501744.2.fa.kmer58` : seq_def (not used)

__Warning__ : `config.yaml` file must refer to the same categories than tags file, otherwise KmerExploR does not display results (`Histone` in the example).

### --config config.yaml

Associated to the tags file, KmerExploR include a configuration file. It is used to reference kmers by categories (ex: Orientation, Mycoplasma) and display some parameters for graphs. It is strongly linked to the tags file. 
When you set your own tag file, probably you will must specify you own config file.
 
 Example for a categorie : 
 

```
Basic_features:   # Meta category, show in left sidenav (underscores are replaced by blank)
  Histone:        # Must match with first item (characters before first dash) of the second column
                  # in the tabuled tags file. Also, they will be used for Javascript function names.
                  # They must be uniq, and contain uniquely letters, digits and underscores
    sidenav : Poly A / Ribo D
                  # Show in the left sidebar
    title: Poly A and Ribo depletion by Histone detection
                  # Title of the graph, in the main page.
    threshold: 350
                  # nothing if threshold is not needed.
                  # More than one threshold possible by adding multiple values separated by coma (ex: 350,450).
    chart_type: bar
                  # Only bar at this time.
    chart_theme: light
                  # light, dark, or nothing
    desc:         # More details on the graph, located under it
      - Short description of Poly A and Ribodepletionq
      - A paragraph of explanations.
      - Another paragraph.
```

Using an alternative tag file, you probably have to redefine the `config.yaml` file, `--config` option specifies the location of an alternative yaml configuration file.


__Nota:__ if you add `as_percent:` to a category, results will be in percentage (take a look at `Read biases` results).


