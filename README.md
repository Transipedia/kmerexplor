# KmerExploR


- [Description](#description)
- [Installation](#installation)
	+ [Option 1: install with pip](#option-1-install-kmerexplor-with-pip)
	+ [Option 2: install with git](#option-2-install-kmerexplor-with-git-by-cloning-repository)
- [Input](#input)
- [Output](#output)
- [Examples](#examples)
- [Usage](#usage)
- [Options](#options)
	- [-k --keep-counts](#-k---keep-counts)
	- [--tags tags_file](#--tags-tags_file)
	- [--config config.yaml](#config-config.yaml)


## Description


From a bunch of fastq or countTags output files, KmerExploR provides information on RNA-sequencing datasets :

- wether the analysis is based on poly-A selection protocol or ribo-depletion,
- whether the analysis is based on oriented or non-oriented sequencing, 
- gender, 
- whether there is a read coverage bias from 5' to 3' 	long transcripts
- wether the data are contamined by HeLa, mycoplasma is present or not, or other viruses such as hepatitis B virus
- specie

`KmerExploR` uses a set of reference specific kmers designed with Kmerator (https://github.com/Transipedia/kmerator).

For general usage, we will use the provided set of kmers. Howerver, it is also possible to create your own kmers reference file to have specific informations on you samples such as request on a particular specie.

This code is under **GPL3** licence.

### Testing with dataset

You can use the following dataset to test the software and to illustrate the different categories, which contains 5 paired-end human RNA-seq samples:

|            |PolyA/RiboD|HeLa  | Mycoplasma | Stranded | Sex    | fastq1 | fastq2 |
|:-----------|:---------:|:----:|:----------:|:--------:|:------:|:------:| :-----:|
|SRR12010285 | PolyA     | +    |      -     |    yes   | female | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR120/085/SRR12010285/SRR12010285_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR120/085/SRR12010285/SRR12010285_2.fastq.gz) |
|ENCFF322RPT | PolyA     | -    |      +     |    yes   | male   | [link](https://www.encodeproject.org/files/ENCFF322RPT/@@download/ENCFF322RPT.fastq.gz) | [link](https://www.encodeproject.org/files/ENCFF782AHJ/@@download/ENCFF782AHJ.fastq.gz) |
|ENCFF001RMX | RiboD     | -    |      -     |    yes   | female | [link](https://www.encodeproject.org/files/ENCFF001RMX/@@download/ENCFF001RMX.fastq.gz) | [link](https://www.encodeproject.org/files/ENCFF001RMW/@@download/ENCFF001RMW.fastq.gz) |
|SRR1957703  | PolyA     | -    |      -     |    yes   |   NA   | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/003/SRR1957703/SRR1957703_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/003/SRR1957703/SRR1957703_2.fastq.gz) |
|SRR1957706  | PolyA     | -    |      -     |    no    |   NA   | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/006/SRR1957706/SRR1957706_1.fastq.gz) | [link](https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR195/006/SRR1957706/SRR1957706_2.fastq.gz) |



## Installation

`KmerExploR` needs `yaml` python module,
We recommand tu use ``pip` as it install everything you need automatically.

### Option 1: install KmerExploR with pip


```
# as user
python3 -m pip install --user kmerexplor

# in virtualenv or as root
python3 -m pip install kmerexplor
```
**Nota**: using pip as user without virtual environment, make sure your PATH variable include `~/.local/bin`.

### Option 2: install KmerExploR with git by cloning repository

```
# clone the repository
git clone https://github.com/Transipedia/kmerexplor.git

# create link somewhere in your PATH
sudo ln -s $PWD/kmerexplor/kmerexplor/core.py /usr/local/bin/kmerexplor
```



## Input


**required:**

- fastq or outputs from countTags (gzipped or not). 

For paired samples, fastq names must be in illumina format (`_R1_001` and `_R2_001`), or they must end by `_1.fastq[.gz]` and `2.fastq[.gz]`. `countTags` files must end by `tsv[.gz]`. `countTags` files can be aggregated in a single multi-culumn file.

**optional:**

- yaml configuration file.
- tags file.

Both must match (see below).


## Output

By default, outputs are produced in directory `kmerexplor-results`.

- `table.tsv` : tab separated table of results.
- `kmerexplor.html` : graphical results.
- `lib` directory contains css and javascript code associated with `kmerexplor.html`.
- if `--keep-counts` option is specified `countTags` directory contains __countTags__ output. 

```
kmerexplor-results
├── countTags			# with '--keep' option
├── kmerTool.html
├── lib
│   ├── echarts-en.min.js
│   ├── scripts.js
│   └── styles.css
└── table.tsv
```


## Usage

Without options or with `--help`, `KmerExploR` returns Help

```
usage: kmerexplor [-h] (-s | -p) [-k <int>] [-K] [-d] [-o <output_dir>] 
                  [--tmp-dir <tmp_dir>] [--config <file_name>] [-t <tag_file>] 
                  [--dump-config [file_name]] [--show-tags]
                  [--title <string>] [-y] [-c <int>] [-v]
                  <file1> ... [<file1> ... ...]

positional arguments:
  <file1> ...           fastq or fastq.gz or tsv countTags output files.

optional arguments:
  -h, --help            show this help message and exit
  -s, --single          when samples are single.
  -p, --paired          when samples are paired.
  -k <int>, --kmer-size <int>
                        kmer size (default 31).
  -K, --keep-counts     keep countTags outputs.
  -d, --debug           debug.
  -o <output_dir>, --output <output_dir>
                        output directory (default: "./kmerexplor-results").
  --tmp-dir <tmp_dir>   temporary files directory.
  --title <string>      title to be displayed in the html page.
  -y, --yes, --assume-yes
                        assume yes to all prompt answers.
  -c <int>, --cores <int>
                        specify the number of files which can be processed 
                        simultaneously by countTags. (default: 1). Valid when 
                        inputs are fastq files.
  -v, --version         show program's version number and exit

advanced features:
  --config <file_name>  alternate config yaml file.
  -t <tag_file>, --tags <tag_file>
                        alternate tag file.

extra features:
  --dump-config [file_name]
                        dump builtin config file as specified name to current 
                        directory and exit (default name: config.yaml).
  --show-tags           print builtin categories and predictors and exit.

```

## Options

### -k --keep-counts

By default, `KmerExploR` deletes intermediate files, particularly countTags output (when input files are fastq files). You could keep countTags output files by using `--keep-counts`option. The location of the countTags output files will then be displayed on the standard output.

countTags outputs are located in a directory named `countTags`, located in `kmerexplor-results` by default or specified by `-o` option.

If you want to run again KmerExploR with the same input dataset, you can directly use  this directory (`kmerexplor-results/countTags/*.tsv`). CountTags step will be bypassed which is saving a lot of time.

### --tags tags_file

KmerExploR uses an internal default tag file. You can specify another tags file using `--tags` option with an alternate tags file (compressed or not).

#### Tags file format

Tags file format is tabuled in 2 columns.

- column 1 : kmer sequence
- column 2 : description with dashes "-" are separator, The dashes are very important to define the structure.

Example : 


```
AACGCCGCGCGTGACAACAAGAAGACCAGGA Histone-H2AFJ-ENST00000501744.2.fa.kmer58
```

- `AACGCCGCGCGTGACAACAAGAAGACCAGGA` : kmer
- `Histone` : category
- `H2AFJ` : seq_id
- `ENST00000501744.2.fa.kmer58` : seq_def (not used)


__Warning__ : `config.yaml` file must refer to the same categories than tags file, otherwise KmerExploR does not display results (`Histone` in the example).

**Notice** : the description of a set of tags can can be displayed on the main home page by creating a markdown file of the same name, suffixed with ``.md`` (eg: my-tags.tsv -> my-tags.md).


### --config config.yaml

Associated to the tags file, KmerExploR includes a configuration file. It is used to reference kmers by categories (ex: Orientation, Mycoplasma) and display some parameters for graphs. It is strongly linked to the tags file. 
When you set your own tag file, you also have to specify you own matching config file.
 
 Example for one categorie : 
 

```
Basic_features:   # Meta category, show in left sidenav (underscores are replaced by blank)
  Histone:        # Must match with first item (characters before first dash) of the second column
                  # in the tabuled tags file. Also, they will be used for Javascript function names.
                  # They must be unique, and contain uniquely letters, digits and underscores
    sidenav : Poly A / Ribo D
                  # Show in the left sidebar
    title: Poly A and Ribo depletion by Histone detection
                  # Title of the graph, in the main page.
    threshold: 350
                  # Leave blank if threshold is not needed.
                  # More than one threshold possible by adding multiple values separated by coma (ex: 350,450).
    chart_type: bar
                  # Only bar is admitted at this time.
    chart_theme: light
                  # light, dark, or nothing
    desc:         # More details on the graph, located under it
      - Short description of Poly A and Ribodepletion (show as title)
      - A paragraph of explanations.
      - Another paragraph.
```

Using an alternative tag file, you probably have to redefine the `config.yaml` file, `--config` option specifies the location of an alternative yaml configuration file.


__Nota:__ if you add `as_percent:` to a category (empty or not), results will be in percentage (take a look at `Read biases` results).



## Examples:

Mandatory: `-p` for paired-end or `-s` for single:

```
kmerexplor -p path/to/*.fastq.gz
```
 
`-c` for multithreading, `-K` to keep counts (input must be fastq):

``` 
kmerexplor -p -c 16 -K path/to/*.fastq.gz
```

You can skip the counting step thanks to countTags output (see `-K` option):

```
kmerexplor -p path/to/countTags/files/*.tsv
```

`-o` to choose your directory output (directory will be created),  
`--title` to show title in results:

```
kmerexplor -p -o output_dir --title 'Title in html page dir/*.fastq.gz'
```

Advanced: using your own tag file and associated config.yaml file:

```
kmerexplor -p -tags my_tags.tsv --config my_config.yaml dir/*.fast.gz
```

