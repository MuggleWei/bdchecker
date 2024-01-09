import sys

from bdchecker.__version__ import __version__
from bdchecker.command.check import CommandCheck
from bdchecker.command.clean import CommandClean
from bdchecker.command.gen import CommandGen
from bdchecker.utils.const_var import APP_NAME


def run_gen():
    """
    run command: gen
    """
    cmd = CommandGen()
    cmd.run(sys.argv[2:])


def run_clean():
    """
    run command: clean
    """
    cmd = CommandClean()
    cmd.run(sys.argv[2:])


def run_check():
    """
    run command: check
    """
    cmd = CommandCheck()
    cmd.run(sys.argv[2:])


def main():
    usage_str = "Usage: {} COMMAND [OPTIONS]\n" \
        "\n" \
        "Commands:\n" \
        "  gen    generate meta file for target path\n" \
        "  clean  remove meta info of missing file\n" \
        "  check  check meta for target path\n" \
        "".format(sys.argv[0])

    if len(sys.argv) < 2:
        print(usage_str)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help"):
        print(usage_str)
        sys.exit(0)

    if sys.argv[1] in ("-v", "--version"):
        print("{} {}".format(APP_NAME, __version__))
        sys.exit(0)

    # commands
    command_dict = {
        "gen": run_gen,
        "clean": run_clean,
        "check": run_check,
    }

    command = sys.argv[1]
    func = command_dict.get(command, None)
    if func is None:
        print(usage_str)
        sys.exit(1)

    try:
        func()
    except Exception as e:
        print("{}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
