#!/usr/bin/python
# coding: utf-8
'''
Vehicle, Line 修正
'''
import argparse
import os
import re
import sys
import pickle
import shutil
from runtable_matchline_func import mk_station_conv, cve2lines, rt2vehicles, \
                                    vehicles_match_line, vehicles_chklist

def cve_line_rename(fixdata, indirn, outdirn):
    rsfn = 'railstation_master.txt'
    cvfn = 'curve_master.txt'
    rwfn = 'railway_master.txt'
    ttfn = 'timetable_master.txt'
    otherfns = ['station_mater.txt', 'transporter_master.txt', 'railtransporter_master.txt']

    infns = os.listdir(indirn)

    fixlineIDs = [x[0] for x in fixdata]

    # railway_master
    with open(os.path.join(indirn, rwfn), 'r', encoding='utf-8') as f:
        rw_data = [[x.strip() for x in l.split('\t')] for l in f]        
    name_old2new = {}
    for rw in rw_data:
        ID, oldname = rw
        if ID in fixlineIDs:
            newname = fixdata[fixlineIDs.index(ID)][2]
            # timetable, curve 用に、old -> new の名前辞書作っておく
            name_old2new[oldname] = newname
            # rename
            rw[1] = newname
    with open(os.path.join(outdirn, rwfn), 'w', encoding='utf-8') as f:
        f.write(''.join('\t'.join(l) + '\n' for l in rw_data))

    # railstation_master
    with open(os.path.join(indirn, rsfn), 'r', encoding='utf-8') as f:
        rs_data = [[x.strip() for x in l.split('\t')] for l in f]        
    for rs in rs_data:
        ID = rs[0]
        if ID in fixlineIDs:
            # 路線名修正
            rs[1] = fixdata[fixlineIDs.index(ID)][2]
    with open(os.path.join(outdirn, rsfn), 'w', encoding='utf-8') as f:
        f.write(''.join('\t'.join(l) + '\n' for l in rs_data))

    # curve_master
    if cvfn in infns:
        with open(os.path.join(indirn, cvfn), 'r', encoding='utf-8') as f:
            cv_data = [[x.strip() for x in l.split('\t')] for l in f]        
        for cv in cv_data:
            oldname = cv[3]
            if oldname in name_old2new:
                # 路線名修正
                cv[3] = name_old2new[oldname]
        with open(os.path.join(outdirn, cvfn), 'w', encoding='utf-8') as f:
            f.write(''.join('\t'.join(l) + '\n' for l in cv_data))

    # timetable_master
    if ttfn in infns:
        with open(os.path.join(indirn, ttfn), 'r', encoding='utf-8') as f:
            tt_data = [[x.strip() for x in l.split('\t')] for l in f]        
        for tt in tt_data:
            oldname = tt[12]
            if oldname in name_old2new:
                # 路線名修正
                tt[12] = name_old2new[oldname]
        with open(os.path.join(outdirn, ttfn), 'w', encoding='utf-8') as f:
            f.write(''.join('\t'.join(l) + '\n' for l in tt_data))

    # 他のファイル
    for fn in otherfns:
        if fn in infns:
            shutil.copy2(os.path.join(indirn, fn), outdirn)

def line_rename(lines, fixfn, incvedirn, outcvedirn):
    with open(fixfn, 'r', encoding='utf-8') as f:
        fix_data = [[x.strip() for x in l.split('\t')] for l in f]
    for fd in fix_data:
        lineID, _, newname = fd
        if not lineID in  lines.lines:
            print('lineID: {} nasi'.format(lineID))
            continue
        lines.lines[lineID].name = newname

    cve_line_rename(fix_data, incvedirn, outcvedirn)

    return lines

def select_splitline(vehicles, fixfn):
    with open(fixfn, 'r', encoding='utf-8') as f:
        _ = next(f)
        fix_data = [[x.strip() for x in l.split('\t')] for l in f]

    fix_data = [x for x in fix_data if x[7]]  # 候補noが無い行は除く
    # {(路線, 方面, ファイル行): 候補no}
    fix_data = {(x[0], x[1], int(x[2])): int(x[7]) for x in fix_data}

    for v in vehicles:
        if v.uni_key in fix_data:
            v.final_split_runtables = v.possible_split_runtables[fix_data[v.uni_key]]
            v.result = 0

    return vehicles

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='tohoku/v2/runtables_splitline_v1')
    psr.add_argument('outdirn', help='tohoku/v2/runtables_splitline_v2')
    psr.add_argument('-c', '--cvedirn', default=None, \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v8')
    psr.add_argument('-o', '--out_cvedirn', default=None, \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v9')
    psr.add_argument('-s', '--shinkansen', choices=['y', 'n'], default='n', \
        help='新幹線は運行表のジョルダン駅名が検索時と違い県名のカッコ書きがないので\
              station_conv.txt を調整する')
    args = psr.parse_args()
    indirn = args.indirn
    outdirn = args.outdirn
    cvedirn = args.cvedirn
    out_cvedirn = args.out_cvedirn
    shinkansen = True if args.shinkansen=='y' else False

    fixdir = os.path.join(indirn, 'fix')
    fix_fns = os.listdir(fixdir)
    sel_sp_fn = 'select_splitline.txt'
    l_rn_fn = 'line_rename.txt'

    stalinedirec_fn = os.path.join(indirn, '../stationlinedirec_n.txt')
    #railstation_fn = os.path.join(cvedirn, 'railstation_master.txt')

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)
    if out_cvedirn and not os.path.isdir(out_cvedirn):
        os.mkdir(out_cvedirn)
    listdirn = os.path.join(outdirn, 'lists')
    if not os.path.isdir(listdirn):
        os.mkdir(listdirn)
    pickledirn = os.path.join(outdirn, 'pickles')
    if not os.path.isdir(pickledirn):
        os.mkdir(pickledirn)

    lpkfn = 'lines.pickle'
    vpkfn = 'vehicles.pickle'

    in_lpkfn = os.path.join(indirn, 'pickles', lpkfn)
    in_vpkfn = os.path.join(indirn, 'pickles', vpkfn)
    out_lpkfn = os.path.join(pickledirn, lpkfn)
    out_vpkfn = os.path.join(pickledirn, vpkfn)

    llfn = os.path.join(listdirn, 'lines_list.txt')
    okfn = os.path.join(listdirn, 'ok.txt')
    posfn = os.path.join(listdirn, 'possible_splitline.txt')
    errfn = os.path.join(listdirn, 'err.txt')

    # vehicles, lines 読み込み
    lines = pickle.load(open(in_lpkfn, 'rb'))
    vehicles = pickle.load(open(in_vpkfn, 'rb'))

    # cve -> ジョルダン 駅名対応リスト取得 多:1
    # {cve駅名: ジョルダン駅名}
    station_conv = mk_station_conv(stalinedirec_fn, shinkansen=shinkansen)

    # 修正
    if l_rn_fn in fix_fns:
        if not cvedirn or not out_cvedirn:
            print('arg [cvedirn] or [out_cvedirn] nasi.')
            sys.exit()
        # 路線名修正
        lines = line_rename(lines, os.path.join(fixdir, l_rn_fn), cvedirn, out_cvedirn)
    # 分割の選択
    if sel_sp_fn in fix_fns:
        vehicles = select_splitline(vehicles, os.path.join(fixdir, sel_sp_fn))

    # 各vehicleを路線マッチング・分割
    vehicles = vehicles_match_line(vehicles, lines, station_conv.values())
    
    # チェックリスト
    vehicles_chklist(vehicles, okfn, posfn, errfn)

    # pickle dump
    pickle.dump(vehicles, open(out_vpkfn, 'wb'))
    pickle.dump(lines, open(out_lpkfn, 'wb'))
