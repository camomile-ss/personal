#!/usr/bin/python
# coding: utf-8
"""
"""
import sys
import cchardet
import re

if __name__ == '__main__':
    infn = sys.argv[1]
    mob = re.search(r'^(.+)\.(txt|tsv)$', infn)
    if not mob:
        print('[err]', infn)
        sys.exit()
    outfn = '{}_out.txt'.format(mob.group(1))
    with open(infn, 'rb') as inf:
        cd = cchardet.detect(inf.read())

    with open(infn, 'r', encoding=cd['encoding']) as inf, \
         open(outfn, 'w', encoding='utf-8') as outf:
        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            if len(l) == 2:
                l.append('network')
            outf.write('\t'.join(l) + '\n')
