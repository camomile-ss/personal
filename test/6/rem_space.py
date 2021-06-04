# coding: utf-8
'''
Created on Tue Jan 29 12:40:53 2019

@author: otani
'''
import sys

infname = sys.argv[1]
outfname = sys.argv[2]

with open(infname, 'r', encoding='utf-8') as inf, \
    open(outfname, 'w', encoding='utf-8') as outf:
    
    for r in inf:
        r = r.strip().split('\t')
        r = [x.strip() for x in r]
        outf.write('\t'.join(r) + '\n')
