#!/usr/bin/python
# coding: utf-8

'''
20210419 のデータ用
'''

import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../common'))
from common_date import char2sectime

def time2sec(datetimechar, stoppers=['00000000000000']):
    if datetimechar in stoppers:
        return 16777215
    else:
        timechar = datetimechar[11:]
        sec = char2sectime(timechar)
        return int(sec)

def get_route_id(stations, railstations):

    for rid, stas in railstations.items():
        #if all(x in stas for x in stations):
        # マスタにない駅があっても通す
        idx = [stas.index(x) for x in stations if x in stas]
        if len(idx) > 1 and all([idx[i] < idx[i+1] for i in range(len(idx) - 1)]):
            return rid
    return None

def noid(stationname):
    if stationname == '鶴見':
        return 11
    if stationname == '函南':
        return None
    if stationname == '来宮':
        return None
    return None

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infn')
    psr.add_argument('outfn')
    psr.add_argument('-m', '--mfn', default='master.txt')
    args = psr.parse_args()
    infn = args.infn
    mfn = args.mfn
    outfn = args.outfn
    p, e = os.path.splitext(outfn)
    msgfn = p + '_メモ' + e
    msg2_linestart = 2
    stoppers = ['00000000000000', 'FFFFFFFFFFFFFF', 'FFFFFFFFFFFFFE']
    out_stopper = 16777215

    # マスタ
    with open(mfn, 'r', encoding='cp932') as f:
        _ = next(f)
        mst = [[x.strip() for x in l.split('\t')] for l in f.readlines()]

    station_name2id = {x[7]: x[6] for x in mst}
    rails = set([x[0] for x in mst])
    railstations = {x: [y[7] for y in mst if y[0]==x] for x in rails}  # {路線ID: [駅名, 駅名, ...], ...}

    # 変換前データ
    with open(infn, 'r', encoding='cp932') as f:
        org_header = next(f)
        data = [[x.strip() for x in l.split('\t')] for l in f.readlines()]

    i_no, i_st, i_at, i_dt, i_tno, i_rid, i_stid, i_msg, i_flg = range(9)
    data = [x + [''] * 4 for x in data]  # 

    # 列車ごとに区切る
    nos = sorted(set([x[0] for x in data]), key=int)
    data = [[x for x in data if x[i_no] == no] for no in nos]

    outdata, train_data_all = [], []

    for train_data in data:

        train_no = train_data[0][i_tno]

        route_id = get_route_id([x[i_st] for x in train_data], railstations)

        # 削除することになるチェックを先に ---------------------------------------------
        # 路線ID 不明なら削除
        route_id = get_route_id([x[i_st] for x in train_data], railstations)
        if not route_id:
            for l in train_data:
                l[i_msg] = '路線不明のため削除 '
                l[i_flg] = 'del'
            train_data_all += train_data
            continue

        for i, l in enumerate(train_data):
            l[i_rid] = route_id
            station_name, adatetime, ddatetime = l[i_st], l[i_at], l[i_dt]
            # 到着時刻・発車時刻ともstopper
            if all([x in stoppers for x in (adatetime, ddatetime)]):
                msg = '到着・発車時刻とも{}などのため削除 '.format(adatetime)
                l[i_msg] += msg
                l[i_flg] = 'del'  # 削除フラグ
                continue
            # 駅名を駅IDに
            if station_name in station_name2id:
                station_id = station_name2id[station_name]
            # マスタに駅がない
            else:
                station_id = noid(station_name)
                if station_id:
                    msg = 'マスタにない。以前のデータから駅IDを取得。 '
                    l[i_msg] += msg
                # 不明の場合は削除
                else:
                    msg = '駅ID不明のため削除 '
                    l[i_msg] += msg
                    l[i_flg] = 'del'
                    continue
            l[i_stid] = station_id

        # 始発駅以外で到着時刻がstopper
        idx = [i for i, x in enumerate(train_data) if x[i_flg]!='del'][1: ]
        for i in idx:
            adatetime = train_data[i][i_at]
            if adatetime in stoppers:
                msg = '始発駅以外で到着時刻が{}のため削除 '.format(adatetime)
                train_data[i][i_msg] += msg
                train_data[i][i_flg] = 'del'  # 削除フラグ
        # 終着駅以外で発車時刻がstopper
        idx = [i for i, x in enumerate(train_data) if x[i_flg]!='del'][: -1]
        for i in idx:
            ddatetime = train_data[i][i_dt]
            if ddatetime in stoppers:
                msg = '終着駅以外で発車時刻が{0}のため削除 '.format(ddatetime)
                train_data[i][i_msg] += msg
                train_data[i][i_flg] = 'del'  # 削除フラグ

        # 1行しか残ってない
        remain_idx = [i for i, x in enumerate(train_data) if x[i_flg]!='del']
        if len(remain_idx) <= 1:
            for i in remain_idx:
                msg = '1駅しか残っていないため削除 '
                train_data[i][i_msg] += msg
                train_data[i][i_flg] = 'del'

            # この列車は出力しない
            train_data_all += train_data
            continue

        # 変換 ------------------------------------------------------------------------
        remain_i = [i for i, x in enumerate(train_data) if x[i_flg]!='del']
        first_i, last_i = remain_i[0], remain_i[-1]  # 削除行以外の最初と最後
        order = 0
        for i, l in enumerate(train_data):
            asec, dsec = time2sec(l[i_at], stoppers), time2sec(l[i_dt], stoppers)
            # 最初の行
            if i == first_i and not l[i_at] in stoppers:
                msg = '到着時刻を無視し始発駅扱い '
                l[i_msg] += msg
                asec = out_stopper

            # 最後の行
            if i == last_i and not l[i_dt] in stoppers:
                msg = '発車時刻を無視し終着駅扱い '
                l[i_msg] += msg
                dsec = out_stopper

            # 発着逆転
            if not out_stopper in (asec, dsec) and asec > dsec:
                msg = '時刻逆転 '
                l[i_msg] += msg

            if l[i_flg] != 'del':
                outline = [str(l[i_rid]), l[i_tno], l[i_tno], str(order), str(l[i_stid]), \
                        '0', str(asec), str(dsec), '0', '3000', '0', '0', '0']
                outdata.append(outline)
                order += 1

        train_data_all += train_data

    with open(outfn, 'w', encoding='utf-8') as f:
        header = ['路線ID', '列車番号1', '列車番号2', '順序', '駅ID', '-', \
                  '到着[累積秒]', '出発[累積秒]', '-', '定員', '-', '-', '-']
        f.write('\t'.join(header) + '\n')
        f.write(''.join(['\t'.join(l) + '\n' for l in outdata]))

    with open(msgfn, 'w', encoding='utf-8') as f:
        header = ['行番号'] + [x.strip() for x in org_header.split('\t')] \
                + ['路線ID', '駅ID', '処理内容']
        f.write('\t'.join(header) + '\n')
        for i, l in enumerate(train_data_all):
            lineno = i + msg2_linestart
            f.write('\t'.join([str(lineno)] + l[:-1]) + '\n')

    '''
    with open(msgfn, 'w', encoding='utf-8') as f:
        header = ['列車番号', '駅ID', '駅名', '処理内容']
        f.write('\t'.join(header) + '\n')
        for l in traindata_plus_msg:
            if l[i_msg]:
                outline = [l[i_tno], l[i_stid], l[i_st], l[i_msg]]
                f.write('\t'.join(outline) + '\n')
    '''
