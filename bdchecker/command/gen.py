import getopt
import sys
from bdchecker.checker import Checker

from bdchecker.utils.const_var import APP_NAME


class CommandGen:
    """
    generate meta file
    """

    def __init__(self):
        self._usage_str = "Usage: {} gen [OPTIONS]\n" \
            "Options: \n" \
            "  -d, --dir        [REQUIRED] target directory\n" \
            "  -v, --verbose    [OPTIONAL] set verbose level; [0|1]\n" \
            "    , --hash       [OPTIONAL] hash algo; [md5|sha256|sha512]\n" \
            "".format(APP_NAME)

        self._dir = ""
        self._verbose = 0
        self._hash_algo = "sha256"

    def run(self, args):
        """
        run command gen
        """
        self._parse_args(args)

        if len(self._dir) == 0:
            print("ERROR! gen without 'dir' param\n")
            print(self._usage_str)
            sys.exit(1)

        checker = Checker(verbose=self._verbose, hash_algo=self._hash_algo)
        checker.gen(self._dir)

    def _parse_args(self, args):
        """
        parse input arguments
        """
        opts, _ = getopt.getopt(
            args, "hd:v:", ["help", "dir=", "verbose=", "hash="]
        )

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(self._usage_str)
                sys.exit(0)
            elif opt in ("-d", "--dir"):
                self._dir = arg
            elif opt in ("-v", "--verbose"):
                self._verbose = int(arg)
            elif opt in ("--hash"):
                self._hash_algo = arg
