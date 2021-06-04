#!/usr/bin/python
# coding: utf-8

'''
路線修正作業用ファイル作成
    対象外駅リスト
        outside_ng_stations(vehicles.pickle) から、
        stationlinedirec_n.txt にない駅をリスト
    路線修正用リスト
        tt_scraping4.py でできた路線をリスト
        lineID, linename, 停車駅リスト(*)
    * 駅名はcveの駅名に変換
'''
import argparse
import os
import pickle
import sys
import re
from vehicle import Vehicle
from lines import Lines, Line_local, Line_rapid, ptn_no, sepID
from station_conv_rev import StationConvRev

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='tohoku/v1')
    psr.add_argument(
        'cvedirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v2')
    psr.add_argument('-s', '--shinkansen', choices=['y', 'n'], default='n', \
        help='新幹線は運行表のジョルダン駅名が検索時と違い県名のカッコ書きがないので\
              station_conv.txt を調整する')
    args = psr.parse_args()
    dirn = args.dirn
    cvedirn = args.cvedirn
    shinkansen = True if args.shinkansen=='y' else False

    # 駅名変換用
    stalinedirecfn = os.path.join(dirn, 'stationlinedirec_n.txt')
    st_conv_rev = StationConvRev(stalinedirecfn, cvedirn, shinkansen=shinkansen)

    vehicle_pickle_fn = os.path.join(dirn, 'pickle/vehicles.pickle')
    lines_pickle_fn = os.path.join(dirn, 'pickle/lines.pickle')
    
    outdirn = os.path.join(dirn, 'cv-e_mod/')
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)
    outf1n = os.path.join(outdirn, 'ng_stations.txt')
    outf2n = os.path.join(outdirn, 'lines_stopstations.txt')

    # 対象外駅リスト
    vehicles = pickle.load(open(vehicle_pickle_fn, 'rb'))
    out1_data = []
    for line, v in vehicles.items():
        print(line)
        for direc, v2 in v.items():
            print('  ', direc)
            for i, vehi in v2.items():
                if vehi.outside_ng_stations:
                    out1_data += [x for x in vehi.outside_ng_stations if not x in st_conv_rev.ista2csta]
    out1 = [(x, str(out1_data.count(x))) for x in set(out1_data)]
    with open(outf1n, 'w', encoding='utf-8') as f1:
        f1.write('\t'.join(['駅名', '件数']) + '\n')
        f1.write(''.join(['\t'.join(l) + '\n' for l in out1]))

    # 路線修正用リスト
    lines = pickle.load(open(lines_pickle_fn, 'rb'))

    sorted_lines = sorted(lines.lines.values(), key=lambda x: (ptn_no(x.ID)))
    sorted_lines = sorted(sorted_lines, key=lambda x: x.parentID if x.__class__==Line_rapid else x.ID)

    out2_data = []
    for l in sorted_lines:
        outline = [l.ID, l.name]
        if l.__class__ == Line_local:
            outline += [st_conv_rev.convert(x, l.ID)[2] for x in l.stations]
        elif l.__class__ == Line_rapid:
            ID_p, _ = sepID(l.ID)
            outline += [st_conv_rev.convert(x, ID_p)[2] for x in l.stop_stations]
        out2_data.append(outline)

    with open(outf2n, 'w', encoding='utf-8') as f2:
        f2.write('\t'.join(['路線ID', '路線名', '->駅名']) + '\n')
        f2.write(''.join(['\t'.join([x or '' for x in l]) + '\n' for l in out2_data]))
