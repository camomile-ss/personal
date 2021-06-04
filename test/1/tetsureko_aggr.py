#!usr/bin/python
# coding: utf-8

import argparse
import re
import logging
import sys
from datetime import date

def mk_line_order(mstfn):

    with open(mstfn, 'r', encoding='cp932') as f:
        mst = [[x.strip() for x in l.split('\t')] for l in f]

    station_order, line_order = {}, []
    for l in mst:
        linename, suf = l[1].split('_')
        stationname = l[7]
        if suf != '0':
            continue
        if linename in line_order:
            station_order[linename].append(stationname)
        else:
            line_order.append(linename)
            station_order[linename] = [stationname]

    out_order = []
    for linename in line_order:
        stations = station_order[linename]
        for sta1 in stations[: -1]:
            for sta2 in stations[stations.index(sta1) + 1: ]:
                out_order.append((linename, sta1, sta2))

    return line_order, station_order, out_order

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('-i', '--infn', help='testデータのとき指定。', default='tetsureko_output.txt')
    psr.add_argument('-m', '--mstfn', default='rs_master.txt')
    psr.add_argument('-o', '--outfn', default='tetsureko_aggr.txt')
    psr.add_argument('-c', '--chkfn', default='tetsureko_aggr_chk.txt')
    psr.add_argument('-d', '--debug', default='n', choices=['y', 'n'])
    args = psr.parse_args()
    infn = args.infn
    mstfn = args.mstfn
    outfn = args.outfn
    chkfn = args.chkfn
    debug = args.debug

    logger = logging.getLogger()
    if debug == 'y':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    line_order, station_order, out_order = mk_line_order(mstfn)

    ptn_sta = re.compile(r'^(.+)駅')

    aggrdata, chkdata = {}, []

    with open(infn, 'r', encoding='utf-8') as f:
        _ = next(f)
        for l in f:
            l = [x.strip() for x in l.split('\t')]
            linename, sta1, sta2, dist, datec, *_ = l
            def shape(sta):
                mob = ptn_sta.search(sta)
                if mob:
                    return mob.group(1)
                else:
                    logger.warning('駅名マッチしない {}'.format(sta))
                    return sta
            sta1, sta2 = shape(sta1), shape(sta2)
            dist = float(dist)
            dateo = date(int(datec[:4]), int(datec[5:7]), int(datec[8:]))

            # 駅順
            if (linename, sta1, sta2) in out_order:
                out_key = (linename, sta1, sta2)
            elif (linename, sta2, sta1) in out_order:
                out_key = (linename, sta2, sta1)
            else:
                out_key = (linename + '（他路線含む）', sta1, sta2)

            if out_key in aggrdata:
                dist_p, dateo_p = aggrdata[out_key]
                if dist_p != dist:
                    chkdata.append(list(out_key) + [dist_p, dateo_p])
                    chkdata.append(list(out_key) + [dist, dateo])
                #if dateo > dateo_p:
                if dist < dist_p:
                    aggrdata[out_key] = [dist, dateo] 

            else:
                aggrdata[out_key] = [dist, dateo]
    
    allkeys = set(list(aggrdata.keys()) + out_order)
    def order(x):
        if x in out_order:
            return out_order.index(x)
        else:
            return 999999
    allkey_sorted = sorted(allkeys, key=lambda x: order(x))

    with open(outfn, 'w', encoding='utf-8') as f:
        for out_key in allkey_sorted:
            if out_key in aggrdata:
                outline = list(out_key) + [str(x) for x in aggrdata[out_key]]
            else:
                outline = list(out_key) + ['データなし', '']
            f.write('\t'.join(outline) + '\n')

    with open(chkfn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in chkdata]))
