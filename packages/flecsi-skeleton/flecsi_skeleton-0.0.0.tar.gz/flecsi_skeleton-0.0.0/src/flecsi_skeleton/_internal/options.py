from pathlib import Path
import argparse

#-------------------------------------------------------------------------------#
# Command line arguments
#-------------------------------------------------------------------------------#

argParser = argparse.ArgumentParser()
argParser.add_argument('name', help="the name of the project")
argParser.add_argument('-p', '--path', action='store', dest='path',
                       help="specify a path to the project"
                       " default: current directory")

def parse_args():
    args = argParser.parse_args()

    root = Path(args.path + '/' + args.name) if args.path else Path(args.name)

    # Use argparse Namespace so that access can be like args.root
    return argparse.Namespace(root = root, name = args.name), \
        {
            "ROOT" : root,
            "UCC_APPNAME" : args.name.title(),
            "LC_APPNAME" : args.name.lower(),
            "UC_APPNAME" : args.name.upper()
        }
