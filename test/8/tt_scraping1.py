#!/usr/bin/python
# coding: utf-8

'''
(1) scraping用に駅名を整る準備
'''

from tt_scraping_func import sta2line
import argparse

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('infn', help='tohoku/v1/station1.txt')
    psr.add_argument('outfn', help='tohoku/v1/station_chk1.txt')
    args = psr.parse_args()
    infn = args.infn
    outfn = args.outfn

    with open(infn, 'r', encoding='utf-8') as inf:
        header = [x.strip() for x in next(inf).split('\t')]
        input_data = [[x.strip() for x in l.split('\t')] for l in inf]
        #stations = [x.strip() for x in inf.readlines()]
    
    count = 0
    with open(outfn, 'w', encoding='utf-8') as outf:
        outf.write('\t'.join(header + ['station_rep', 'message', 'lines count']) + '\n')
        for row in input_data:
            station = row[3]
            lines, station_rep, message = sta2line(station)

            if station_rep or message or not lines:
                count += 1

            if not station_rep:
                if not message:
                    station_rep = station
                    message = ''
                else:
                    station_rep = ''

            outf.write('\t'.join(row + [station_rep, message, str(len(lines))]) + '\n')

    if count:
        print('{} station name need to change.'.format(count))
    else:
        print('all station name OK.')
