#!/usr/bin/python
# coding: utf-8

'''
(2) 整えた駅名リストから、路線・方面リストを作成
'''

from tt_scraping_func import sta2lineDirec
import argparse
import sys
from time import ctime

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('infn', help='tohoku/v1/station2.txt')
    psr.add_argument('outfn', help='tohoku/v1/stationlinedirec.txt')
    args = psr.parse_args()
    infn = args.infn
    outfn = args.outfn

    with open(infn, 'r', encoding='utf-8') as inf:
        header = [x.strip() for x in next(inf).split('\t')]
        input_data = [[x.strip() for x in l.split('\t')] for l in inf]
    
    with open(outfn, 'w', encoding='utf-8') as outf:
        outf.write('\t'.join(header + ['line', 'tt_direc', 'message1']) + '\n')
        for i, row in enumerate(input_data):

            station = row[header.index('station_input')]
            print('{0}/{1} {2} {3}'.format(i+1, len(input_data), station, ctime()))

            lines_direcs, station_rep, message1 = sta2lineDirec(station)

            if station_rep or message1:
                print('{0}, station_rep: {1}, message: {2}'.format(station, station_rep, message1))

            outf.write(''.join('\t'.join(row + [l, d, m or '']) + '\n' \
                                         for l, d_s, m in lines_direcs for d in d_s))
