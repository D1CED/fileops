#!/usr/bin/python
"""Module fileops is a cli tool for set operations on files"""
import sys, os
import os.path as path

# add conditionals later with 'if' and 'in'/'ni'
helptxt = """usage: %s <out-dir> '<S-exp>' <...in-dirs>

All filenames are passed as strings. Relative filenames are allowed.
An S-expression is build by "(" + <operation> + <...arguments> + ")",
where arguments can be S-exp themselves.
Use $n to refer to the in files strictly in order or enter them in-place.
The following set operations are defined and their shorhands:
    union                - u (two args)
    intersection         - n (two args)
    difference           - \\ (two args)
    symmetric_difference - s (two args)""" % (sys.argv[0])
helpflags = ["-h", "--h", "-help", "--help"]

execdir = {
	"u": (frozenset.union, 2),
	"union": (frozenset.union, 2),
	"n": (frozenset.intersection, 2),
	"intersection": (frozenset.intersection, 2),
	"\\": (frozenset.difference, 2),
	"difference": (frozenset.difference, 2),
	"s": (frozenset.symmetric_difference, 2),
	"symmetric_difference": (frozenset.symmetric_difference, 2),
}
s_open = "("
s_close = ")"

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

def tokenize(s):
	"""function tokenize is an iterator over tokens of an s-expression"""
	s = s.split(" ")
	for idx, val in enumerate(s):
		if val[0] == s_open:
			yield s_open
			yield val[1:]
			continue
		if val[-1] == s_close:
			yield val[:-1]
			yield s_close
			continue
		yield val
	return

def next_paren(str_):
	"""function next_paren returns the index of the next top level element of a tokinize range"""
	o, idx = 0, 0
	for idx, s in enumerate(tokenize(str_)):
		if s == s_open:
			o += 1
		if s == s_close:
			o -= 1
		if o == 0:
			break
	return idx

def dir_to_set(dir_):
	if not path.isabs(dir_):
		dir_ = path.realpath(dir_) + '/'
	return frozenset([x for x in os.listdir(dir_) if path.isfile(dir_ + x)])

class ParseError(ValueError):
	pass

def parse(l):
	tt = []
	for t in tokenize(l):
		tt.append(t)
	if tt[0] != s_open:
		raise ParseError("expected \"(\", got %s" % tt[0])

	if tt[1] not in execdir:
		raise ParseError("expected operation, got %s" % tt[1])

	args = []
	for i in range(2, execdir[tt[1]][1]+2):
		t = tt[i]
		if t == s_open:
			args.append(parse(tt[i:next_paren(tt[i:])]))
			tt = tt[next_paren(tt[i:])-2 : next_paren(tt[i:])]
		elif t[0] == "$":
			args.append(dir_to_set(indirs[int(t[1:])-1]))
		else:
			args.append(dir_to_set(t))
	return execdir[tt[1]][0](*args)

res = parse(sexp)
print(res)
