#!/usr/bin/python
# coding: utf-8
"""
vehicles から時刻表 timetable_master.txt 生成
"""
import argparse
import os
import sys
import re
import pickle
from station_conv_rev import StationConvRev
from lines import sepID
sys.path.append('../common')
from common_date import char2sectime

def mk_timetable(vehicle, rw_ID2name, station_conv_rev, tno):

    # (定数)
    tsutei = '2'  # 通停区分 2
    ttype = '0'  # 列車種別 0
    capa = 1000  # 定員
    stopper = 16777215  # 時刻stopper
    stoptime = 15  # 仮の駅停車時間

    tt_data_ = []

    for v in vehicles:
        # 対象外
        if not v.target:
            continue
        # 結果なし
        if v.result is None or v.result != 0:
            continue

        # 列車uni_key
 
        # 分割路線ごとに
        for sno, sp in enumerate(v.final_split_runtables):
            lineID = sp.lineID
            linename = rw_ID2name[sp.lineID]

            ## 運行表 -------------------------------------------
            # 時刻を秒に（4時以降当日）
            runtable = [[staj, char2sectime(timec, day_split_hour=4), timetype] \
                        for staj, timec, timetype in sp.runtable]
            # 着発を1行に
            stations = [staj for staj, time, timetype in runtable]
            stations = sorted(set(stations), key=lambda x: stations.index(x))
            time_a = {staj: time for staj, time, timetype in runtable if timetype=='着'}
            time_d = {staj: time for staj, time, timetype in runtable if timetype=='発'}

            runtable = [[staj, \
                         time_a[staj] if staj in time_a else time_d[staj] - stoptime, \
                         time_d[staj] if staj in time_d else time_a[staj] + stoptime, \
                        ] for staj in stations]
            runtable[0][1] = stopper
            runtable[-1][2] = stopper
            # 駅を駅Codeに
            runtable = [[station_conv_rev.convert(sta, lineID)[0], time_a, time_b] \
                         for sta, time_a, time_b in runtable]
            ## ----------------------------------------------------

            # 分割路線仮番号
            sp_uni_key = v.uni_key + (sno,)

            # 直通先
            continue_to = v.uni_key + (sno+1, ) if sno < len(v.final_split_runtables)-1 else None

            tt = [[sp_uni_key, no] + rtl + [lineID, linename, continue_to] for no, rtl in enumerate(runtable)]
            tt_data_ += tt

    # 路線ID順にソート
    lineIDs = sorted(set([x[5] for x in tt_data_]), key=lambda x: sepID(x)[1] or 0)
    lineIDs.sort(key=lambda x: sepID(x)[0])

    tt_data_.sort(key=lambda x: lineIDs.index(x[5]))

    # 順にtrainnoつける。対応データをつくる
    sp_uni_keys = [x[0] for x in tt_data_]
    sp_uni_keys = sorted(set(sp_uni_keys), key=lambda x: sp_uni_keys.index(x))
    train_nos = ['Train{:04}'.format(tno + i) for i in range(len(sp_uni_keys))]
    spk2train_no = {spk: train_no for spk, train_no in zip(sp_uni_keys, train_nos)}

    tt_data, train_no2linename = [], {}
    for l in tt_data_:
        sp_uni_key, no, stacd, time_a, time_d, lineID, linename, continue_to = l
        train_no = spk2train_no[sp_uni_key]
        continue_to = spk2train_no[continue_to] if continue_to else '-' 

        tt_data.append( \
            [train_no] * 2 \
            + [no, stacd, '0', tsutei, time_a, time_d, '3', '0', ttype, '0', linename, \
               capa, continue_to])
        train_no2linename[train_no] = linename

    return tt_data, spk2train_no, train_no2linename

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indir', help='tohoku/v1/runtable_splitline_v2')
    psr.add_argument('cvedirn', help='cv-editor用データのdir.')
    psr.add_argument('out_cvedirn', help='timetable_master.txtを出力するdir')
    psr.add_argument('-n', '--trainNo_start', help='開始列車番号', type=int, default=0)
    psr.add_argument('-s', '--shinkansen', choices=['y', 'n'], default='n', \
        help='新幹線は運行表のジョルダン駅名が検索時と違い県名のカッコ書きがないので\
              station_conv.txt を調整する')
    args = psr.parse_args()
    indir = args.indir
    cvedirn = args.cvedirn
    out_cvedirn = args.out_cvedirn
    if not os.path.isdir(out_cvedirn):
        os.mkdir(out_cvedirn)
    tno = args.trainNo_start
    shinkansen = True if args.shinkansen=='y' else False

    vpklfn = os.path.join(indir, 'pickles/vehicles.pickle')
    sldfn = os.path.join(indir, '../stationlinedirec_n.txt')

    v2trnfn = os.path.join(indir, 'vehicle2trainno.txt')

    rwfn = 'railway_master.txt'
    ttfn = 'timetable_master.txt'

    vehicles = pickle.load(open(vpklfn, 'rb'))

    station_conv_rev = StationConvRev(sldfn, cvedirn, shinkansen=shinkansen)

    with open(os.path.join(cvedirn, rwfn), 'r', encoding='utf-8') as f:
        rw_ID2name =  {x[0]: x[1] for x in [[y.strip() for y in l.split('\t')] for l in f]}

    tt_data, spk2train_no, train_no2linename = mk_timetable(vehicles, rw_ID2name, station_conv_rev, tno)

    with open(os.path.join(out_cvedirn, ttfn), 'w', encoding='utf-8') as f:
        for l in tt_data:
            f.write('\t'.join([str(x) for x in l]) + '\n')

    sorted_keys = sorted(spk2train_no.keys(), key=lambda x: x[3])
    sorted_keys.sort(key=lambda x: x[2])
    sorted_keys.sort(key=lambda x: x[1])
    sorted_keys.sort(key=lambda x: x[0])
    with open(v2trnfn, 'w', encoding='utf-8') as f:
        f.write('\t'.join(['tt_line', 'tt_direc', 'fileline', 'split no', 'train no']) + '\n')
        for k in sorted_keys:
            train_no = spk2train_no[k]
            linename = train_no2linename[train_no]
            f.write('\t'.join([str(x) for x in k] + [train_no, linename]) + '\n')
