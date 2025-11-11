import sys
from .options import *
from .fileutils import *
from .templates import *

#-------------------------------------------------------------------------------#
# Main
#-------------------------------------------------------------------------------#

def main():
    args, dargs = parse_args()

    write(args.root / 'CMakeLists.txt', TOPLEVEL_CMAKELISTS.format(**dargs))
    write(args.root / 'spec' / 'CMakeLists.txt', SPEC_CMAKELISTS.format(**dargs))
    write(args.root / 'app' / 'CMakeLists.txt', APP_CMAKELISTS.format(**dargs))

    write(args.root / 'spec' / 'control.hh', CONTROL.format(**dargs))

    write(args.root / 'app' / (args.name + '.cc'), DRIVER.format(**dargs))
    write(args.root / 'app' / 'advance.hh', ADVANCE.format(**dargs))
    write(args.root / 'app' / 'analyze.hh', ANALYZE.format(**dargs))
    write(args.root / 'app' / 'finalize.hh', FINALIZE.format(**dargs))
    write(args.root / 'app' / 'initialize.hh', INITIALIZE.format(**dargs))
    write(args.root / 'app' / 'types.hh', TYPES.format(**dargs))

    copy_resource('README.md', args.root)
    copy_resource('support/env.yaml', args.root)
