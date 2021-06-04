#!/usr/bin/python
# coding: utf-8

import argparse
import os
import re

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='tohoku/v1_東武追加用')
    psr.add_argument('kizonfn', help='tohoku/v1/stationlinedirec_n.txt')
    args = psr.parse_args()
    dirn = args.dirn
    kizonfn = args.kizonfn

    rt_dir = os.path.join(dirn, 'runtables')
    outfname = os.path.join(dirn, 'stations_listup.txt')

    # もうある駅のリスト
    with open(kizonfn, 'r', encoding='utf-8') as f:
        header = [x.strip() for x in next(f).split('\t')]
        idx_st = header.index('station_input')

        kizon = [l_[idx_st] for l_ in [[x.strip() for x in l.split('\t')] for l in f]]
        kizon = set(kizon)

    ptn = re.compile(r'^.+_runtables.txt$')
    runtables = [x for x in os.listdir(rt_dir) if ptn.search(x)]

    stations_listup = []
    for rt in runtables:
        with open(os.path.join(rt_dir, rt), 'r', encoding='utf-8') as f:
            print(rt)
            header = [x.strip() for x in next(f).split('\t')]
            idx_rt = header.index('->runtable')

            for l in f:
                rt_data = [x.strip() for x in l.split('\t')][idx_rt:]
                stations = [rt_data[i] for i in range(0, len(rt_data), 3)]
                print(stations)

                for s in stations:
                    if not s in stations_listup:
                        stations_listup.append(s)

    stations_listup = [[x, '既存' if x in kizon else ''] for x in stations_listup]

    with open(outfname, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(l) + '\n' for l in stations_listup]))
