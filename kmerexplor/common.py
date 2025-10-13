### Const

import os
import sys
import shutil


def exit_gracefully(args, files_type=None):
    """ Function doc """
    ### In debug mode, do not remove temporary files.
    if args.debug:
        print("\n In debug mode, you should remove manually {} temp directory".format(args.tmp_dir))
    elif args.tmp_dir:
            shutil.rmtree(args.tmp_dir)
    ### With EOF, the program exit succesfully.
    if  args.debug: print("EOF")
