import sys
import os
import argparse
from shutil import copyfile
import gzip


import info
from common import *

APPPATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TAGSET = "human-quality"


def handle_args(args):
    ### check some args
    check_args(args)
    ### check special options
    if args.dump_config: _dump_config(args)
    if args.show_tags: _show_tags(args)
    if args.list_tagsets: _list_tagsets(args)


def check_args(args):
    special_option = any([args.show_tags, args.dump_config, args.list_tagsets])
    ### --paired OR --single
    if not special_option:
        if len([True for i in (args.paired, args.single) if i]) != 1:
            sys.exit("Syntax error: one of the arguments -s/--single -p/--paired is required")
        ### At least one fastq must be define
        if not args.files:
            sys.exit("Syntax error: the following arguments are required: <files1>")
    ### output directory must be writable
    if not os.access(os.path.dirname(os.path.abspath(args.output)), os.W_OK):
        sys.exit(f"Permission denied: {os.path.dirname(os.path.abspath(args.output))}")
    ### Define user tagset tsv/fasta, config yaml, desc md and put them in args
    user_args_len = len([_ for _ in (args.config, args.tags) if _])
    if user_args_len == 2:
        ### check file presences
        if not os.path.isfile(args.tags):
            sys.exit(f"File error: {args.tags!r} not found")
        ### Is user has define a markdown description file ?
        user_desc_file = f"{os.path.splitext(args.tags.split('gz')[0])[0]}.md"
        if not os.path.isfile(user_desc_file):
            user_desc_file = None
        ### Re-define set of tag files
        args.setfiles = {'tags':args.tags, 'config': args.config, 'desc': user_desc_file}
        return
    elif user_args_len == 1 and not special_option:
        sys.exit("SyntaxError: '-C/--config' and '-T/--tags' work together")
    args.setfiles = _get_tagsets(args)


def _get_tagsets(args=None):
    basedir, subdirs, files = next(os.walk(os.path.join(APPPATH, 'tagsets')))
    tagsets = {}
    for file in files:
        if file.endswith(('tsv.gz', 'fa.gz', 'fasta.gz')):
            tagset = ('.'.join(file.split('.')[:-2]))
            ext = '.'.join(file.split('.')[-2:])
            tagsets[tagset] = ext
        elif file.endswith(('tsv', 'fa', 'fasta')):
            tagset = ('.'.join(file.split('.')[:-1]))
            ext = '.'.join(file.split('.')[-1:])
            tagsets[tagset] = ext

    ### return list of kmer sets
    if not args:
        return list(tagsets.keys())

    ### Exit if kmer set files not found
    exit = lambda tagset, tagsets : sys.exit("kmer set '{}' not found, kmer sets available:\n - {}\n"
             "Default is 'human-quality'. You can also use your own kmer set with '--tags' option."
             .format(tagset, '\n - '.join(tagsets)))

    ### find and return kmer set, yaml config and description file
    tagset = args.builtin_tags
    ext = tagsets[tagset]
    def get_setfiles(tagset, ext):
            tag_file = os.path.join(basedir, f"{tagset}.{ext}")
            config_file = os.path.join(basedir, f"{tagset}.yaml")
            desc_file = os.path.join(basedir, f"{tagset}.md")
            if not os.path.isfile(tag_file) or not os.path.isfile(config_file):
                exit(tagset, tagsets)
            if not os.path.isfile(desc_file):
                desc_file = None
            setfiles = {'tags':tag_file, 'config': config_file, 'desc': desc_file, 'ext': ext, 'tags_format': ext.rstrip('.gz')}
            return setfiles

    ### get chosen tagset
    setfiles = get_setfiles(tagset, ext)
    return setfiles



def _dump_config(args):
    """
    Copy builtin config yaml file in current directory
    """
    try:
        copyfile(args.setfiles['config'], args.dump_config)
    except:
        sys.exit(f"FileNotFoundError: file {args.dump_config!r} not found")
    sys.exit(f"Configuration dumped in file {args.dump_config!r} succesfully.")


def _show_tags(args):
    """
    show details of specified tagset (default: human-quality)
    """
    categories = {}
    ### Define tag file.
    tags_file = args.tags or args.setfiles['tags']

    ### is tag file gzipped ?
    is_gz = _is_gz_file(tags_file)
    ### is file formated as fasta or tsv ?
    tag_format = _get_file_format(tags_file, is_gz)
    ### open tag file
    try:
        if is_gz:
            fh = gzip.open(tags_file, 'rt')
        else:
            fh = open(tags_file)
    except FileNotFoundError as err:
        sys.exit(f"Error: file {tags_file!r} not found")
    ### Extract categories and predictors
    if tag_format == 'tsv':
        for line in fh:
            try:
                category, predictor = line.split('\t')[1].split('-')[:2]
                categories.setdefault(category, set()).add(predictor)
            except IndexError:
                sys.exit(f"Error: file '{tags_file!r}' malformated (show format of tag file).")
    if tag_format == 'fasta':
        for line in fh:
            try:
                if line.startswith('>'):
                    category, predictor = line[1:].rstrip().split('-')[:2]
                    categories.setdefault(category, set()).add(predictor)
            except IndexError:
                sys.exit(f"Error: file '{tags_file!r}' malformated (show format of tag file).")



    ### Display categories and predictors
    for categ,predictors in categories.items():
        print(categ)
        for predictor in predictors:
            print(f"  {predictor}")

    sys.exit()


def _list_tagsets(args):
    """
    List builtin tag sets
    """
    print("Buitin tag set (to use with -b/--builtin-tags):")
    print(" - {}\nDefault: human-quality".format('\n - '.join(_get_tagsets())))
    sys.exit()


def _is_gz_file(file):
    with open(file, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b'


def _get_file_format(file, gz=False):
    ### Is tag file a fasta or a tsv
    if gz:
        with gzip.open(file, 'rt') as fh:
            format = 'fasta' if fh.readline().startswith('>') else 'tsv'
    else:
        with open(file) as fh:
            format = 'fasta' if fh.readline().startswith('>') else 'tsv'
    return format



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
    # ~ method = parser.add_mutually_exclusive_group(required=True) # method = paired or single
    advanced_group = parser.add_argument_group(title='advanced features')
    special_group = parser.add_argument_group(title='extra features')
    parser.add_argument('files',
                        help='fastq or fastq.gz or tsv countTags output files.',
                        nargs='*',
                        metavar=('<file1> ...'),
    )
    parser.add_argument('-s', '--single',
                        action='store_true',
                        help='when samples are single.',
    )
    parser.add_argument('-p', '--paired',
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
    parser.add_argument('-b', '--builtin-tags',
                        help=f"Choose a kmer set between {_get_tagsets()} (default: human-quality)",
                        default='human-quality',
    )
    parser.add_argument('-o', '--output',
                        default=f'./{info.APPNAME.lower()}-results',
                        help=f'output directory (default: "./{info.APPNAME.lower()}-results").',
                        metavar='<output_dir>',
    )
    parser.add_argument('-l', '--list-tagsets',
                        action='store_true',
                        help="List available kmer sets",
    )
    parser.add_argument('--tmp-dir',
                        default='/tmp',
                        help='temporary files directory.',
                        metavar='<tmp_dir>',
    )
    advanced_group.add_argument('-C', '--config',
                        help="alternate config yaml file. Used with '--tags' option",
                        metavar='<file_name>',
    )
    advanced_group.add_argument('-T', '--tags',
                        help=("alternate tag file. Could be fasta or tsv file (gzip or not)."
                              " Needs '--config' option"),
                        metavar='<tag_file>',
    )
    ### Not implemented yet: hidden
    advanced_group.add_argument('-A', '--add-tags',
                        help=argparse.SUPPRESS, # 'additional tag file.',
                        metavar='<tag_file>',
    )
    special_group.add_argument('--dump-config',
                        default=None,
                        metavar='file_name',
                        help=('dump builtin config file as specified name '
                              'as yaml format and exit.'),
    )
    special_group.add_argument('--show-tags',
                        action='store_true',
                        help='print builtin categories and predictors and exit.',
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
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    ### check, add, and modify some parameters
    handle_args(args)

    return args
