#!/usr/bin/python
# coding: utf-8
'''
取得した運行表から路線を整理、優等列車路線のリストを作成
def mk_line_conv(fn):
    [return]   {(ジョルダン路線名, ジョルダン方面名): [(cve路線ID, cve路線名), ...], ...}
def mk_station_conv(fn):
    [return]   {cve駅名: ジョルダン駅名, ...}
def mk_railstation_data(fn, station_conv):
    [return]   {(lineID, linename): [ジョルダン駅名, ...], ... }
'''
import argparse
import os
import re
import sys
import pickle
from runtable_matchline_func import mk_station_conv, cve2lines, rt2vehicles, vehicles_match_line

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='tohoku/v2')
    psr.add_argument('cvedirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v5')
    psr.add_argument('outdirn', help='tohoku/v2/runtables_splitline_v1')
    args = psr.parse_args()
    indirn = args.indirn
    cvedirn = args.cvedirn
    outdirn = args.outdirn

    rt_dirn = os.path.join(indirn, 'runtables')
    lineconv_fn = os.path.join(indirn, 'line_conv.txt')
    stalinedirec_fn = os.path.join(indirn, 'stationlinedirec_n.txt')
    railstation_fn = os.path.join(cvedirn, 'railstation_master.txt')

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)
    listdirn = os.path.join(outdirn, 'lists')
    if not os.path.isdir(listdirn):
        os.mkdir(listdirn)

    llfn = os.path.join(listdirn, 'lines_list.txt')
    okfn = os.path.join(listdirn, 'ok.txt')
    posfn = os.path.join(listdirn, 'possible_splitline.txt')
    errfn = os.path.join(listdirn, 'err.txt')

    # ジョルダン -> 所定 路線対応リスト取得 1:多
    # {(ジョルダン路線名, ジョルダン方面名): [(cve路線ID, cve路線名), ...], ...}
    #line_conv = mk_line_conv(lineconv_fn)

    # cve -> ジョルダン 駅名対応リスト取得 多:1
    # {cve駅名: ジョルダン駅名}
    station_conv = mk_station_conv(stalinedirec_fn)

    # Lines instance
    lines = cve2lines(cvedirn, station_conv, llfn)

    # vehicles instance
    vehicles = rt2vehicles(rt_dirn)
    
    # 各vehicleを路線マッチング・分割
    vehicles = vehicles_match_line(vehicles, lines, station_conv.values(), okfn, posfn, errfn)




    