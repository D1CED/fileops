#!/usr/bin/python
"""Module fileops is a cli tool for set operations on files"""
import sys, os, os.path

# add conditionals later with 'if' and 'in'/'ni'
helptxt = """usage: %s <out-dir> <S-exp> ...<in-dirs>

All filenames are passed as strings. Relative filenames are allowed.
An S-expression is build by "(" + <operation> + ...<arguments> + ")", where arguments can be S-exp themselves.
Use $n to refer to the in files strictly in order or enter them in-place.
The following set operations are defined and their shorhands:
    union               - u (two args)
    intersection        - n (two args)
    complement          - \\ (two args)
    symmetricdifference - s (two args)""" % (sys.argv[0])
helpflags = ["-h", "--h", "-help", "--help"]

try:
	if sys.argv[1] in helpflags:
		print(helptxt)
		sys.exit(2)
	else:
		outdir = sys.argv[1]
		sexp   = sys.argv[2]
		indirs = sys.argv[3:]
except IndexError:
	print(helptxt)
	sys.exit(2)

try:
	os.mkdir(outdir)
except FileExistsError:
	pass

indirsets = []
for dir_ in indirs:
	indirsets.append(set([x for x in os.listdir(dir_) if os.path.isfile(x)]))
	# indirsets.append(set(filter(lambda a: os.path.isfile(a), os.listdir(dir_))))

print(indirsets)

execdir = {"u": set.union, "n": set.intersection,
	"\\": set.difference, "s": set.symmetric_difference}

sexp_str = sexp.split(" ")
sexp_ast = []

def dir_to_set(s):
	return set([x for x in os.listdir(dir_) if os.path.isfile(x)])

class ParseError(ValueError):
	pass

def parse(l):
	if l[0] != "(":
		raise ParseError("expected \"(\", got %" % l[0])

	if l[1] not in execdir:
		raise ParseError("expected operation, got %" % l[1])

	if l[2][0] == "(":
		arg1 = parse(l[2])
	if l[2][0] == "$":
		arg1 = indirs[int(l[2][1:])]

	if l[3][0] == "(":
		arg1 = parse(l[3])
	if l[3][0] == "$":
		arg1 = indirs[int(l[3][1:])]
