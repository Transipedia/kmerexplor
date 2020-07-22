### Const

import os
import sys
import shutil


APPPATH = os.path.dirname(os.path.realpath(__file__))
SPECIES = {
    'human': os.path.join(APPPATH, 'indexes', 'Human_tags.tsv.gz'),
    #'mouse': os.path.join(APPPATH, 'indexes', 'Mouse_tags.tsv.gz'),
}


def get_tags_file(args):
    """ Function doc """
    ### Find tags file
    ## --tags used to specify tags file
    if args.tags:
        tags_file = args.tags
    ## tags file specified from --specie option (default: human)
    else:
        tags_file = SPECIES[args.specie]
    ### Is tag file here ?
    if not os.path.isfile(tags_file):
        print("\n FileError: tags file '{}' not Found.\n".format(tags_file))
        sys.exit(ending(args))
    return tags_file


def ending(args, files_type=None):
    """ Function doc """
    ### In debug mode, do not remove temporary files.
    if args.debug:
        print("\n In debug mode, you should remove manually {} temp directory".format(args.tmp_dir))
    elif args.tmp_dir:
            shutil.rmtree(args.tmp_dir)
    ### With EOF, the program ending succesfully.
    if  args.debug: print("EOF")
