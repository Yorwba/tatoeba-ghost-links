#!/usr/bin/env python3

"""
Executes set operations on the input files interpreted as sorted lists of integer tuples.
"""

import operator
import sys


_, op, file1, file2 = sys.argv
op = operator.__dict__['__'+op+'__']


def next_tuple(f):
    line = f.readline()
    if not line:
        return None
    return tuple(map(int, line[:-1].split('\t')))

with open(file1, 'r') as f1:
    with open(file2, 'r') as f2:
        l1 = next_tuple(f1)
        l2 = next_tuple(f2)
        while l1 or l2:
            if l2 is None or l1 is not None and l1 < l2:  # l1 not in f2
                if op(1, 0):
                    print('\t'.join(map(str, l1)))
                l1 = next_tuple(f1)
            elif l1 == l2:  # l1 in f2
                if op(1, 1):
                    print('\t'.join(map(str, l1)))
                l1 = next_tuple(f1)
                l2 = next_tuple(f2)
            elif l1 is None or l2 is not None and l2 < l1:  # l2 not in f1
                if op(0, 1):
                    print('\t'.join(map(str, l2)))
                l2 = next_tuple(f2)
            else:
                raise RuntimeError  # should never happen if comparison is linear
