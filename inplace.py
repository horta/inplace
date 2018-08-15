# from __future__ import unicode_literals
import sys
from subprocess import check_output, call


def inplace(root_dir, sed_expr):
    files = check_output(["find", root_dir, "-type", "f", "-print0"])
    print(files)

    # files = files.split(b"\0")[:-1]
    # for f in files:

    #     f = f.decode()
    #     print(["sed", "-i", "''", "-e", sed_expr, f])
    #     call(["sed", "-i", "''", "-e", sed_expr, f])


def main():
    inplace(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
