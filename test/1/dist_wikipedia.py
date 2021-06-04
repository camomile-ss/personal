#!usr/bin/python
# coding: utf-8

import argparse
import re
import logging
import sys
from datetime import date

def read_data(fn):

    with open(fn, 'r', encoding='cp932') as f:
        _ = next(f)
        indata = [[x.strip() for x in l.split('\t')] for l in f]

    lines = [x[0] for x in indata]
    lines = sorted(set(lines), key=lambda x: lines.index(x))

    eigyo_kilos = [0 if x[2]=='-' else float(x[2]) for x in indata]

    #indata = [x[:2] + [y] for x, y in zip(indata, eigyo_kilos)]
    
    linestations = {x: {'stations': [y[1] for y in indata if y[0]==x], 'eigyo_kilos': [z for y, z in zip(indata, eigyo_kilos) if y[0]==x]} for x in lines}

    return lines, linestations

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('-i', '--infn', help='testデータのとき指定。', default='dist_wikipedia_input.txt')
    psr.add_argument('-o', '--outfn', default='dist_wikipedia_output.txt')
    psr.add_argument('-d', '--debug', default='n', choices=['y', 'n'])
    args = psr.parse_args()
    infn = args.infn
    outfn = args.outfn
    debug = args.debug

    logger = logging.getLogger()
    if debug == 'y':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    lines, linestations = read_data(infn)

    with open(outfn, 'w', encoding='utf-8') as f:

        for line in lines:
            stations = linestations[line]['stations']
            eigyo_kilos = linestations[line]['eigyo_kilos']

            for i in range(len(stations) - 1):
                for j in range(i + 1, len(stations)):

                    eigyo_kilo = round(sum(eigyo_kilos[i + 1: j + 1]), 1)

                    f.write('\t'.join([line, stations[i], stations[j], str(eigyo_kilo)]) + '\n')
