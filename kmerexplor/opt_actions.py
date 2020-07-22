import argparse
import os, sys
from shutil import copyfile
import gzip

from common import *


class DumpAction(argparse.Action):
    """ Copy builtin config.yaml in current directory
    see :
    https://stackoverflow.com/questions/8632354/python-argparse-custom-actions-with-additional-arguments-passed
    https://stackoverflow.com/questions/11001678/argparse-custom-action-with-no-argument
    """

    def __init__(self, option_strings, arg, *args, **kwargs):
        """ Function doc """
        super(DumpAction, self).__init__(option_strings=option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_strings):
        file = values or 'config.yaml'
        """ Copy kmerexplor configuration file to current directory """
        try:
            copyfile(f"{APPPATH}/config.yaml", f"./{file}")
        except:
            sys.exit(f"FileNotFoundError: file 'config.yaml' not found in '{APPPATH}'.")
        sys.exit(f"Configuration dumped in file '{file}' succesfully.")


class ShowTagsAction(argparse.Action):
    """ Copy builtin config.yaml in current directory
    see :
    https://stackoverflow.com/questions/8632354/python-argparse-custom-actions-with-additional-arguments-passed
    https://stackoverflow.com/questions/11001678/argparse-custom-action-with-no-argument
    """

    def __init__(self, option_strings, *args, **kwargs):
        """ Function doc """
        super(ShowTagsAction, self).__init__(option_strings=option_strings, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_strings):
        """ Display categories and tags """

        ### Manage specie case (--tags and --specie, --tags as priority)
        class Args:
            debug=False
            tmp_dir=None
            specie = namespace.specie
            for i,arg in enumerate(sys.argv):
                if arg in ('-S', '--specie'):
                    try:
                        specie = sys.argv[i+1]
                    except IndexError:
                        sys.exit(f"OptionError: argument {arg} expected one argument (choose from {', '.join([s for s in SPECIES])})")
                    if specie not in SPECIES:
                        sys.exit(f"OptionError: argument {arg}: invalid choice: '{specie}' (choose from {', '.join([s for s in SPECIES])}).")
            tags = namespace.tags
            for i,arg in enumerate(sys.argv):
                if arg in ('-t', '--tags'):
                    try:
                        tags = sys.argv[i+1]
                    except IndexError:
                        sys.exit(f"OptionError: argument {arg} expected one argument")
        tags_file = get_tags_file(Args)

        categories = {}
        ### open tag file
        if os.path.splitext(tags_file)[1] == '.gz':
            fh = gzip.open(tags_file, 'rt')
        else:
            fh = open(tags_file)
        ### Extract categories and predictors
        for line in fh:
            try:
                category, predictor = line.split('\t')[1].split('-')[:2]
            except IndexError:
                sys.exit(f"Error: file '{tags_file}' malformated (show format of tag file).")
            if not category in categories:
                categories[category] = {predictor}
            else:
                categories[category].add(predictor)

        ### Display categories and predictors
        for categ,predictors in categories.items():
            print(categ)
            for predictor in predictors:
                print(f"  {predictor}")

        ### exit !!!
        sys.exit()
