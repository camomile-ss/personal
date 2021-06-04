#!/usr/bin/python
# coding: utf-8
'''
ほぼ均等になるように中間点を補う
[args] interval: 間隔(m)
'''
import argparse
import os
import sys
sys.path.append('../common')
from common_geography import latlon2distance

def mk_line_outdata(line_data, interval):

    prev_lat, prev_lon = None, None
    line_outdata = []
    for r in line_data:
        lat, lon, _, line = r
        lat, lon = float(lat), float(lon)
        if prev_lat is None:
            pass
        else:
            s, _, _ = latlon2distance(prev_lat, prev_lon, lat, lon)
            mp_num = int(round(s / interval))  # 中間点の数
            if mp_num <= 1:
                pass
            else:
                for n in range(1, mp_num):
                    add_lat = prev_lat + (lat - prev_lat) * n / mp_num
                    add_lon = prev_lon + (lon - prev_lon) * n / mp_num
                    line_outdata.append([str(add_lat), str(add_lon), '-', line])
        line_outdata.append(r)
        prev_lat, prev_lon = lat, lon
    return line_outdata

def set_midpoints_evenly(infn, outfn, interval):
    with open(infn, 'r', encoding='utf-8') as inf:
        indata = [[x.strip() for x in l.split('\t')] for l in inf]

    outdata = []

    lines = [x[3] for x in indata]
    lines = sorted(set(lines), key=lambda x: lines.index(x))
    for line in lines:
        line_data = [x for x in indata if x[3]==line]
        line_outdata = mk_line_outdata(line_data, interval)

        outdata += line_outdata

    with open(outfn, 'w', encoding='utf-8') as outf:
        outf.write(''.join(['\t'.join(x) + '\n' for x in outdata]))

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('infname', help='input "curve_master.txt"')
    psr.add_argument('outfname', help='output "curve_master.txt"')
    psr.add_argument('-i', '--interval', type=int, default=10)
    args = psr.parse_args()
    
    set_midpoints_evenly(args.infname, args.outfname, args.interval)
