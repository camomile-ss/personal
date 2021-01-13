#!/usr/bin/python
# coding: utf-8
"""
timetable_master.txt -> trainlog.txt
"""
import argparse
import os

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirname', help='all_master')
    psr.add_argument('outfname', help='trainlog.txt')
    args = psr.parse_args()

    dirn = args.dirname
    outfn = args.outfname

    infn = os.path.join(dirn, 'timetable_master.txt')
    rwfn = os.path.join(dirn, 'railway_master.txt')
    stfn = os.path.join(dirn, 'station_master.txt')

    # 路線名 -> 路線ID
    with open(rwfn, 'r', encoding='utf-8') as rwf:
        line_id = {x[1]: x[0] for x in [[c.strip() for c in l.split('\t')] for l in rwf]}

    # 駅ID -> 駅コード
    with open(stfn, 'r', encoding='utf-8') as stf:
        sta_cd = {x[1]: x[0] for x in [[c.strip() for c in l.split('\t')] for l in stf]}

    # convert
    with open(infn, 'r', encoding='utf-8') as inf, open(outfn, 'w', encoding='utf-8') as outf:

        for l in inf:
            trno1, trno2, seq, sta_id, _, _, time_a, time_d, _, _, ttype, _, line_nm, capa, _ \
                = [x.strip() for x in l.split('\t')]

            # 列車種別 0 だと列車アイコン表示されない
            if ttype == '0':
                ttype = '1'

            outl = [line_id[line_nm], trno1, trno2, seq, sta_cd[sta_id], '0', time_a, time_d, ttype, capa, '0', '0']
            outf.write('\t'.join(outl) + '\n')
