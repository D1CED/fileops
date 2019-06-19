#!/usr/bin/python

"""
Module fileops is a cli tool for set operations on files.
"""

import argparse
import operator
import os
import os.path as path
import sys
from contextlib import suppress
from itertools import chain, takewhile
from shutil import copyfile


S_OPEN = "("
S_CLOSE = ")"

_alldirs = {}
_indirs = []

help_text = """
Directory names may not contain '$', '(', ')', ' ' or start with a number.
All filenames are passed as strings. Relative filenames are allowed.
An S-expression is build by "(" + <operation> + <...arguments> + ")",
where arguments can be S-exp themselves.
Use $n to refer to the in files strictly in order or enter them in-place.
The following set operations are defined and their shorhands:
    union                - (u <set> <set>) -> <set>
    intersection         - (n <set> <set>) -> <set>
    difference           - (\\ <set> <set>) -> <set>
    symmetric_difference - (s <set> <set>) -> <set>

    cardinality          - (# <set>) -> <num>

    if conditional       - (if (<bool>) (<exp>) (<exp>)) -> <exp>

    contains             - (in <set> <set>) -> <bool>
    disjoint             - (d <set> <set>)  -> <bool>
    equals               - (eq <num> <num>) -> <bool>
    less                 - (lt <num> <num>) -> <bool>
    greater              - (gt <num> <num>) -> <bool>
"""

execdir = {
    # adding new operations is trivial
    # n-length argument support?
    "u":  (frozenset.union, 2),
    "n":  (frozenset.intersection, 2),
    "\\": (frozenset.difference, 2),
    "s":  (frozenset.symmetric_difference, 2),
    "in": (frozenset.issubset, 2),
    "d":  (frozenset.isdisjoint, 2),
    "#":  (len, 1),
    "eq": (operator.eq, 2),
    "lt": (operator.lt, 2),
    "gt": (operator.gt, 2),
    "if": (lambda a, b, c: b if a else c, 3),
}

accept_number = ["lt", "eq", "gt"]


def tokenize(s):
    """generator tokenize is an iterator over tokens of an s-expression"""
    for val in s.split():
        last = 0
        while val[0] == S_OPEN:
            val = val[1:]
            yield S_OPEN
        for char in reversed(val):
            if char == S_CLOSE:
                val = val[:-1]
                last += 1
        if val != "":
            yield val
        for _ in range(last):
            yield S_CLOSE


def next_paren_it():
    depth = 0

    def inner(token):
        nonlocal depth

        if token == S_OPEN:
            depth += 1
        elif token == S_CLOSE:
            depth -= 1

        return depth != 0

    return inner


def dir_to_set(dir_) -> frozenset:
    """returns a set of all filenames of a directory"""
    if path.isfile(path.realpath(dir_)):
        return frozenset(dir_)
    dir_ = path.realpath(dir_)
    if dir_[-1] != "/":
        dir_ += "/"
    _alldirs.update((x, dir_+x)
                    for x in os.listdir(dir_)
                    if path.isfile(dir_ + x))
    return frozenset(x for x in os.listdir(dir_) if path.isfile(dir_ + x))


class ParseError(ValueError):
    pass


def parse(l):
    """returns the result of a given S-expression"""

    tokens = tokenize(l) if isinstance(l, str) else l

    try:
        token = next(tokens)
        if token != S_OPEN:
            raise ParseError(f"expected '{S_OPEN}', got '{token}'")

        token = next(tokens)
        if token == S_CLOSE:
            return None
        elif token not in execdir:
            raise ParseError(f"expected operation, got '{token}'")
        op = token

        args = []
        token = next(tokens)
        while token != S_CLOSE:  # number of args

            if token == S_OPEN:
                tmp = chain(takewhile(next_paren_it(), chain([S_OPEN], tokens)),
                            [S_CLOSE])
                args.append(parse(tmp))
            elif token[0] == "$":
                try:
                    args.append(dir_to_set(_indirs[int(token[1:])-1]))
                except IndexError:
                    raise ParseError(f"file '{int(token[1:])}' not specified")
                except ValueError:
                    raise ParseError(f"error converting '{token}' to int")
            elif token.isdigit():
                i = int(token)
                if op in accept_number:
                    args.append(i)
                else:
                    raise ParseError(f"num literal outside context '{op}'")
            elif token == S_CLOSE:
                raise ParseError("expected value got ')', to few arguments")
            else:
                args.append(dir_to_set(token))

            token = next(tokens)

    except StopIteration:
        raise ParseError(
            f"possibly missing closing parentheses - last value was '{token}'")

    if len(args) != execdir[op][1]:
        raise ParseError(
            f"too many or few arguments for operation '{op}' - expected {execdir[op][1]} got {len(args)}")
    try:
        next(tokens)
        raise ParseError("too many closing parentheses")
    except StopIteration:
        pass

    # print(op, args, execdir[op][0](*args))
    return execdir[op][0](*args)


def main():
    """parses flags and prints result of the provided S-expression"""
    argp = argparse.ArgumentParser(epilog=help_text, allow_abbrev=False,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)

    argp.add_argument("S-exp", type=str,
                      help="Lisp-like S-expression for set operations.")
    argp.add_argument("-f", default=False, dest="force", action='store_true',
                      help="Don't ask for override.")
    argp.add_argument("-o", type=str, dest="outdir",
                      help="If the expression result is a set copy files to <o> directory. (default print to std.out)")
    argp.add_argument('indirs', nargs='*',
                      help="files refernced form sexp with $<n>")

    args = vars(argp.parse_args())

    global _indirs
    _indirs = args["indirs"]
    outdir = args["outdir"]
    force = args["force"]

    try:
        res = parse(args["S-exp"])
    except ParseError as pe:
        print("error while parsing S-expression:", pe)
        sys.exit(1)

    if outdir and isinstance(res, frozenset):
        if force:
            with suppress(FileExistsError):
                os.mkdir(outdir)
        else:
            try:
                os.mkdir(outdir)
            except FileExistsError:
                inp = input("directory already present still proceed? [y/N]: ")
                if inp != "y":
                    sys.exit(2)
        for x in res:
            copyfile(_alldirs[x], outdir+x)
    else:
        print(res)


if __name__ == "__main__":
    main()
