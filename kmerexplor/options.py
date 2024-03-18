import sys
import os
import argparse
from shutil import copyfile
import gzip


import info
# from opt_actions import DumpAction, ShowTagsAction, ListTagsetsAction
from common import *

APPPATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TAGSET = "human-quality"


"""
ajouter les def :
 - dump_config()
 - show_tags()
 - list_tagsets
contrôler que
 - qu'il y a '-s' OU '-p'
"""

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
    ### Define user tagset tsv, config yaml, desc md and put them in args
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
    tagsets = []
    for file in files:
        if file.endswith('tsv.gz'):
            tagsets.append('.'.join(file.split('.')[:-2]))
        elif file.endswith('tsv'):
            tagsets.append('.'.join(file.split('.')[:-1]))

    ### return list of kmer sets
    if not args:
        return tagsets

    ### Exit if kmer set files not found
    exit = lambda tagset, tagsets : sys.exit("kmer set '{}' not found, kmer sets available:\n - {}\n"
             "Default is 'human-quality'. You can also use your own kmer set with '--tags' option."
             .format(tagset, '\n - '.join(tagsets)))

    ### find and return kmer set, yaml config and description file
    tagset = args.builtin_tags
    def get_setfiles(tagset, ext):
            tag_file = os.path.join(basedir, f"{tagset}.{ext}")
            config_file = os.path.join(basedir, f"{tagset}.yaml")
            desc_file = os.path.join(basedir, f"{tagset}.md")
            if not os.path.isfile(tag_file) or not os.path.isfile(config_file):
                exit(tagset, tagsets)
            if not os.path.isfile(desc_file):
                desc_file = None
            setfiles = {'tags':tag_file, 'config': config_file, 'desc': desc_file, 'ext': ext}
            return setfiles
            # ~ return type('KmerFiles', (object,), setfiles)

    ext = ('tsv.gz','tsv')[f"{tagset}.tsv" in files]
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
    ### open tag file
    try:
        if os.path.splitext(tags_file)[1] == '.gz':
            fh = gzip.open(tags_file, 'rt')
        else:
            fh = open(tags_file)
    except FileNotFoundError as err:
        sys.exit(f"Error: file {tags_file!r} not found")
    ### Extract categories and predictors
    for line in fh:
        try:
            category, predictor = line.split('\t')[1].split('-')[:2]
        except IndexError:
            sys.exit(f"Error: file '{tags_file!r}' malformated (show format of tag file).")
        if not category in categories:
            categories[category] = {predictor}
        else:
            categories[category].add(predictor)

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
                        help="alternate tag file. Needs '--config' option",
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
