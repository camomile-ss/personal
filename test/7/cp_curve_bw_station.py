#!/usr/bin/python
# coding: utf-8

import argparse
import os
import shutil
import sys
sys.path.append('../common')
from common_os import rmdir_recursively, rmdir_recursively_noconfirm

def backup(edit_dir):

    if edit_dir[-1]=='/':
        edit_dir = edit_dir[:-1]
    old_dir = edit_dir + '_old/'
    if os.path.isdir(old_dir):
        #rmdir_recursively(old_dir)
        rmdir_recursively_noconfirm(old_dir)
    shutil.copytree(src=edit_dir, dst=old_dir)

def mk_linenames(confn):
    ''' 対象路線名リスト '''
    with open(confn, 'r', encoding='utf-8') as f:
        return [x.strip() for x in f.readlines()]

def read_data(fn):
    ''' tsv ファイル読む -> 行のリスト、行はカラムのリスト '''
    with open(fn, 'r', encoding='utf-8') as f:
        return [[x.strip() for x in l.split('\t')] for l in f]

def mk_org_curve(orgfn, linenames, nomid):
    '''
    駅間カーブデータ辞書作成
    {(駅名, 駅名): [[lat, lon], [lat, lon], .... ], ... }
        orgfn: curve_master.txt
        linenames: 対象の路線名
        nomid: 中間点なしの駅間が対象かどうか
    '''
    # curve data 読み込み
    dat = read_data(orgfn)

    # 対象の路線だけに
    dat = [x for x in dat if x[3] in linenames]
    dat_latlon = [x[:2] for x in dat]
    dat_station = [x[2] for x in dat]

    # 中間点以外のindex
    indices = [i for i, x in enumerate(dat_station) if x!='-']
    next_indices = indices[1:]
    pair_indices = [(i, j) for i, j in zip(indices, next_indices)]  # 隣接駅ペア

    # 駅間カーブデータ辞書
    org_curve = {}
    for i, j in pair_indices:
        if nomid and j == i+1:  # 中間点なし対象外の場合とばす
            continue
        org_curve[(dat_station[i], dat_station[j])] = dat_latlon[i: j+1]

    return org_curve

def cp_curve_1line(line, linedata, org_curve_bw_station, rev):
    ''' 1路線のデータのカーブをコピー
            line: 路線名
            linedata: [lat, lon, 駅名 or -] のリスト
            org_curve_bw_station: 駅間カーブデータ辞書
            rev: 逆向きの駅間カーブデータをコピーするかどうか
    '''
    stations = [x[2] for x in linedata if x[2]!='-']  # 駅のみ（中間点以外）
    dup_num = [stations[:n].count(stations[n]) for n in range(len(stations))]  # 重複番号 同一駅あったら最初は0, 以降1,2,...

    for i in range(len(stations) - 1):

        sta1, sta2 = stations[i], stations[i+1]  # 駅名
        dup1, dup2 = dup_num[i], dup_num[i+1]  # 重複番号

        if (sta1, sta2) in org_curve_bw_station:
            curve = org_curve_bw_station[(sta1, sta2)]
        elif rev and (sta2, sta1) in org_curve_bw_station:
            curve = org_curve_bw_station[(sta2, sta1)][::-1]
        else:
            continue

        bw_sta = [sta1] + ['-' for i in range(len(curve) - 2)] + [sta2]
        bw_data = [c + [s] for c, s in zip(curve, bw_sta)]

        sta_column = [x[2] for x in linedata]  # 中間点含む駅カラム
        def get_idx(sta, dup):
            ''' dup番目のstaのインデックス(同じ駅2回通る路線あるため) '''
            sta_idx = sta_column.index(sta)
            for n in range(dup):
                sta_idx = sta_column.index(sta, sta_idx+1)
            return sta_idx
        sta1_idx = get_idx(sta1, dup1)
        sta2_idx = get_idx(sta2, dup2)
        linedata = linedata[:sta1_idx] + bw_data + linedata[sta2_idx + 1: ]
        #linedata = linedata[:sta_column.index(sta1)] + bw_data + linedata[sta_column.index(sta2) + 1: ]

    return [x + [line] for x in linedata]

def cp_curve(indata, org_curve_bw_station, rev):
    ''' カーブをコピー（1ファイル）
            indata: [lat, lon, 駅名 or -, 路線名] のリスト
            org_curve_bw_station: 駅間カーブデータ辞書
            rev: 逆向きの駅間カーブデータをコピーするかどうか
    '''
    lines = [x[3] for x in indata]
    lines = sorted(set(lines), key=lambda x: lines.index(x))

    outdata = []

    for line in lines:

        line_indata = [x[:3] for x in indata if x[3]==line]
        line_outdata = cp_curve_1line(line, line_indata, org_curve_bw_station, rev)

        outdata = outdata + line_outdata

    return outdata

def write_data(fn, outdata):
    ''' curve_master.txt 出力 (リストのリスト -> tsv) '''
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(l) + '\n' for l in outdata]))

def main(edit_dir, org_dir, rev, nomid, confn):
    '''
    [args]
        edit_dir: コピー先データdir (all_master)
        org_dir: コピー元データdir (同上)
        rev: 逆方向も対象にする(1), しない(0)
        nomid: 中間点なしの駅間は対象外(0), 対象(1)
        confn: コピー元のコピー対象路線名の羅列のファイル名
    '''
    orgfn = os.path.join(org_dir, 'curve_master.txt')
    editfn = os.path.join(edit_dir, 'curve_master.txt')

    # 対象の路線リスト
    linenames = mk_linenames(confn)

    # コピー先データを _old にコピー
    backup(edit_dir)

    # コピー元 curve_data 辞書作成
    org_curve_bw_station = mk_org_curve(orgfn, linenames, nomid)

    # コピー先 curve_data 読み込み
    indata = read_data(editfn)

    # コピー先 curve_data へ各駅間 curve をコピー
    outdata = cp_curve(indata, org_curve_bw_station, rev)

    # 出力
    write_data(editfn, outdata)

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('edit_master_dir')
    psr.add_argument('original_master_dir')
    psr.add_argument('-r', '--reverse', type=int, default=1,
                     help='逆方向も対象にする(1), しない(0). default: 1')
    psr.add_argument('-m', '--nomidpoint', type=int, default=0,
                     help='中間点なしの駅間は対象外(0), 対象(1). default: 0')
    psr.add_argument('-c', '--confname', default='./cp_curve_bw_station_linenames.txt')
    args = psr.parse_args()
    edit_dir = args.edit_master_dir
    org_dir = args.original_master_dir
    rev = args.reverse
    nomid = args.nomidpoint
    confn = args.confname

    main(edit_dir, org_dir, rev, nomid, confn)
