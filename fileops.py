#!/usr/bin/python
"""Module fileops is a cli tool for set operations on files"""
import os
import sys
import argparse
from shutil import copyfile
import os.path as path

s_open = "("
s_close = ")"

argp = argparse.ArgumentParser(epilog="""
Directory names may not contain '$', '(', ')' or start with a number.
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
    disjoint             - (d <set> <set>) -> <bool>
    equals               - (eq <num> <num>) -> <bool>
    less                 - (lt <num> <num>) -> <bool>
    greater              - (gt <num> <num>) -> <bool>
""", allow_abbrev=False, formatter_class=argparse.RawDescriptionHelpFormatter)
argp.add_argument("sexp", type=str, help="Lisp-like S-expression for set operations.")
argp.add_argument("-f", default=False, dest="force", action='store_true', help="Don't ask for override.")
argp.add_argument("-o", type=str, dest="outdir", help="If the expression result is a set copy files to <o> directory. (default print to std.out)")
argp.add_argument('indirs', nargs='*', help="files refernced form sexp with $<n>")
flags = argp.parse_args()
print(vars(flags))

execdir = {
    "u": (frozenset.union, 2),
    "n": (frozenset.intersection, 2),
    "\\": (frozenset.difference, 2),
    "s": (frozenset.symmetric_difference, 2),
    "#": ((lambda a: len(a)), 1),
    "in": ((lambda a, b: a.issubset(b)), 2),
    "d": ((lambda a, b: a.isdisjoint(b)), 2),
    "eq": ((lambda a, b: a == b), 2),
    "lt": ((lambda a, b: a < b), 2),
    "gt": ((lambda a, b: a > b), 2),
    "if": ((lambda a, b, c: b if a else c), 3),
}

def tokenize(s):
    """function tokenize is an iterator over tokens of an s-expression"""
    s = s.split()
    for idx, val in enumerate(s):
        if val[0] == s_open:
            yield s_open
            yield val[1:]
            continue
        if val[-1] == s_close:
            yield val.partition(")")[0]
            for _ in range(len(val) - len(val.partition(")")[0])):
                yield s_close
            continue
        yield val
    return

def next_paren(tt) -> int:
    """function next_paren returns the index of the next top level element of a tokinize range"""
    o, idx = 1, 0
    for idx, s in enumerate(tt):
        if s == s_open:
            o += 1
        if s == s_close:
            o -= 1
        if o == 0:
            break
    return idx

def dir_to_set(dir_):
    if path.isfile(path.realpath(dir_)):
        return set(dir_)
    dir_ = path.realpath(dir_)
    if dir_[-1] != "/":
        dir_ += "/"
    return frozenset([x for x in os.listdir(dir_) if path.isfile(dir_ + x)])


class ParseError(ValueError):
    pass

def parse(l):
    if isinstance(l, str):
        tt = [t for t in tokenize(l)]
    else:
        tt = list(l)
    if tt == [s_open, s_close]:
        return

    cur = tt.pop(0)
    if cur != s_open:
        raise ParseError(f"expected \"(\", got {cur}")

    op = tt.pop(0)
    if op not in execdir:
        raise ParseError(f"expected operation, got {op}")

    args = []
    for _ in range(execdir[op][1]): # number of args
        t = tt.pop(0)
        if t == s_open:
            args.append(parse(["("]+tt[:next_paren(tt)+1]))
            for _ in range(next_paren(tt)+1):
                tt.pop(0)
        elif t[0] == "$":
            args.append(dir_to_set(flags.indirs[int(t[1:])-1]))
        elif t[0] in [x for x in range(1, 10)]:
            i = int(t)
            if op in ["lt", "eq", "gt"]:
                args.append(i)
            else:
                raise ValueError(f"num literal outside context {op}")
        else:
            args.append(dir_to_set(t))

    if tt.pop(0) != s_close:
        raise ParseError("no closing parenthese")
    if len(tt) != 0:
        raise ParseError("to many arguments")

    # print(op, args, execdir[op][0](*args))
    return execdir[op][0](*args)

res = parse(flags.sexp)
if flags.outdir and isinstance(res, frozenset):
    try:
        os.mkdir(outdir)
        [copyfile(x, flags.outdir+x) for x in res]
    except FileExistsError:
        if not flags.force:
            in_ = input("directory already present still proceed? [y/N]: ")
            if in_ != "y":
                sys.exit(2)
else:
    print(res)
