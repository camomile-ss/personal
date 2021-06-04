# coding: utf-8
'''
ファイルの行を逆に
'''

import sys

infname = sys.argv[1]
outfname = sys.argv[2]

with open(infname, 'r') as inf:
    data = inf.readlines()

data_rev = data[::-1]

with open(outfname, 'w') as outf:
    for r in data_rev:
        outf.write(r)
