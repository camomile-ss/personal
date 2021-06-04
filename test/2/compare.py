#!/usr/bin/python
# coding: utf-8
'''
20200419データ比較用
'''
import sys
import os
from datetime import datetime

def read_data(fn):

    i_tid = 5

    data = {}
    with open(fn, 'r', encoding='utf-8') as f:
        _ = next(f)
        for l in f:
            l = [x.strip() for x in l.split('\t')]
            trainno = l[i_tid]
            if trainno in data:
                data[trainno].append(l)            
            else:
                data[trainno] = [l]

    return data

def compare(trainno, data1t, data2t, routes):

    stoppers = ['00000000000000', 'FFFFFFFFFFFFFF', 'FFFFFFFFFFFFFE']

    i_no, i_st, i_at, i_dt, _, i_rid, i_stid, i_msg = range(1, 9)
    routeid = data1t[0][i_rid]

    # 駅を合わせる
    stations1 = [x[i_st] for x in data1t]
    stations2 = [x[i_st] for x in data2t]
    if stations1 == stations2:
        stations = [x for x in stations1]
    else:
        if all([x in stations1 for x in stations2]):
            stations = [x for x in stations1]
        elif all([x in stations2 for x in stations1]):
            stations = [x for x in stations2]
        else:
            stations = set(stations1 + stations2)
            if routeid in routes:
                if all([x in routes[routeid] for x in stations]):
                    stations = sorted(stations, key=lambda x: routes[routeid].index(x))
                else:
                    print('ソートできない:', trainno)

    # 1と2をまとめる
    def c2datetime(char):
        if char in stoppers:
            return char
        return datetime.strptime(char, '%Y-%m-%d %H:%M:%S.000')
    out_tdata = []
    out_idx_1 = [4, 5, 6, 12]
    out_idx_2 = [7, 8, 9, 13]
    oi_d1, oi_d2 = 10, 11
    for station in stations:

        outline = [trainno, routeid, '', station] + [''] * 10

        def func(data, stas, out_idx):
            oi_no, oi_at, oi_dt, oi_msg = out_idx
            if station in stas:
                dt_line = data[stas.index(station)]
                if dt_line[i_stid]:
                    outline[2] = dt_line[i_stid]
                at = c2datetime(dt_line[i_at])
                dt = c2datetime(dt_line[i_dt])
                outline[oi_no] = dt_line[i_no]
                outline[oi_at] = at
                outline[oi_dt] = dt
                outline[oi_msg] = dt_line[i_msg]
            else:
                outline[oi_msg] = '行欠落'

        func(data1t, stations1, out_idx_1)
        func(data2t, stations2, out_idx_2)

        out_tdata.append(outline)

    # 時刻比較
    for l in out_tdata:
        no1, at1, dt1, no2, at2, dt2 = l[4: 10]

        # 片方しかない
        if not no1 and not no2:
            continue

        # 到着時刻比較
        if not at1 in stoppers + [''] and not at2 in stoppers + ['']:
            l[oi_d1] = (at2 - at1).total_seconds()
        # 発車時刻比較
        if not dt1 in stoppers + [''] and not dt2 in stoppers + ['']:
            l[oi_d2] = (dt2 - dt1).total_seconds()

    return out_tdata

def mk_routes(mstfn='master_for_sort.txt'):
    '''
    {路線ID: [駅名, 駅名, ...], ...}
    '''

    i_rid, i_stn = 0, 7

    routes = {}
    with open(mstfn, 'r', encoding='cp932') as f:
        _ = next(f)
        for l in f:
            l = [x.strip() for x in l.split('\t')]
            if l[i_rid] in routes:
                routes[l[i_rid]].append(l[i_stn])
            else:
                routes[l[i_rid]] = [l[i_stn]]

    return routes

if __name__ == '__main__':

    inf1n = '20210419_1_メモ.txt'
    inf2n = '20210419_2_メモ.txt'
    outfn = '20210419_比較.txt'

    data1 = read_data(inf1n)
    data2 = read_data(inf2n)

    data1_trainnos = sorted(set(data1.keys()), key=int)
    data2_trainnos = sorted(set(data2.keys()), key=int)

    # 共通train no
    trainnos_common = [x for x in data1_trainnos if x in data2_trainnos]

    # 路線の駅順辞書
    routes = mk_routes()

    out_data = []
    for trainno in trainnos_common:

        out_data += compare(trainno, data1[trainno], data2[trainno], routes)

    with open(outfn, 'w', encoding='utf-8') as f:
        header0 = ['(共通)', '', '', '', 'データ1', '', '', 'データ2', '', '', '時刻差異', '', '備考', '']
        header1 = ['列車番号', '路線ID', '駅ID', '駅名', '番号', '到着日時', '発車日時', '番号', '到着日時', '発車日時', '到着日時', '発車日時', 'データ1', 'データ2']
        f.write('\t'.join(header0) + '\n')
        f.write('\t'.join(header1) + '\n')
        f.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in out_data]))
