#!/usr/bin/python
# coding: utf-8

'''
20210414 のデータ用（入力3カラム）
'''

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../common'))
from common_date import char2sectime

def time2sec(datetimechar, stopper='00000000000000'):
    if datetimechar == stopper:
        return 16777215
    else:
        timechar = datetimechar[11:]
        sec = char2sectime(timechar)
        return int(sec)

def get_route_id(stations, railstations):

    for rid, stas in railstations.items():
        if all(x in stas for x in stations):
            idx = [stas.index(x) for x in stations]
            if all([idx[i] < idx[i+1] for i in range(len(idx) - 1)]):
                return rid
    return None

if __name__ == '__main__':

    infn = 'seikei_mae.txt'
    mfn = 'master.txt'
    outfn = '整形後.txt'
    msgfn = '整形メモ.txt'
    msg2fn = '元データメモ.txt'
    msg2_linestart = 2

    stopper = '00000000000000'

    # マスタ
    with open(mfn, 'r', encoding='cp932') as f:
        _ = next(f)
        mst = [[x.strip() for x in l.split('\t')] for l in f.readlines()]

    #route_id = mst[0][0]
    station_name2id = {x[7]: x[6] for x in mst}
    rails = set([x[0] for x in mst])
    railstations = {x: [y[7] for y in mst if y[0]==x] for x in rails}  # {路線ID: [駅名, 駅名, ...], ...}

    # 変換前データ
    with open(infn, 'r', encoding='cp932') as f:
        org_header = next(f)
        data = [[x.strip() for x in l.split('\t')] for l in f.readlines()]
    data = [[i] + l for i, l in enumerate(data)]  # 行番号つける
    i_no, i_st, i_at, i_dt = range(4)

    # 列車ごとに区切る（到着がstopperになってる行が始発駅。終着駅はあてにならないが始発駅は大丈夫そう。）
    start_idx = [i for i, x in enumerate(data) if x[i_at]==stopper]
    end_idx = start_idx[1: ] + [len(data)]

    data = [data[i: j] for i, j in zip(start_idx, end_idx)]

    train_no, outdata, msgdata, org_msgdata = 0, [], [], []
    for train_data in data:

        train_no += 1
        train_id = 'train{:04}'.format(train_no)

        route_id = get_route_id([x[i_st] for x in train_data], railstations)
        if not route_id:
            print('{} route_id nasi'.format(train_id))

        # 1行目が両時刻ともstopperだったら削除
        no, fstation, fddatetime, fadatetime = train_data[0]
        if all(x==stopper for x in (fddatetime, fadatetime)):
            msg = '到着・発車時刻とも{}のため削除'.format(stopper)
            msgdata.append([train_id, '-', fstation, msg])
            train_data[0].append(msg)
            train_data[0].append('del')  # 削除フラグ
            #train_data.pop(0)

        # 開始行なし
        # 開始行インデックス
        first_idx = [i for i, x in enumerate([x for x in train_data]) if x[-1]!='del'][0]
        no, fstation, fddatetime, fadatetime = train_data[first_idx]
        if fddatetime != stopper:
            msg = '到着時刻を無視し始発駅扱い'
            fst_id = station_name2id[fstation]
            msgdata.append([train_id, fst_id, fstation, msg])
            train_data[first_idx].append(msg)
            train_data[first_idx][i_at] = stopper

        # 最終行なし
        # 最終行インデックス
        last_idx = [i for i, x in enumerate([x for x in train_data]) if x[-1]!='del'][-1]
        no, lstation, lddatetime, ladatetime = train_data[last_idx]
        if ladatetime != stopper:
            msg = '発車時刻を無視し終着駅扱い'
            lst_id = station_name2id[lstation]
            msgdata.append([train_id, lst_id, lstation, msg])
            train_data[last_idx].append(msg)
            train_data[last_idx][i_dt] = stopper

        # 変換
        i = 0
        for l in train_data:
            if l[-1] == 'del':  # 削除行はとばす
                continue
            no, station_name, adatetime, ddatetime, *_ = l
            if station_name in station_name2id:
                station_id = station_name2id[station_name]
            else:
                print(station_name, 'なし')
                station_id = '-'

            # 鶴見マスタにないのでメモに出す
            if station_name == '鶴見':
                msg = 'マスタにない。以前のデータから駅IDを取得。'
                msgdata.append([train_id, station_id, station_name, msg])

            asec, dsec = time2sec(adatetime, stopper), time2sec(ddatetime, stopper)
            # 発着逆転
            if asec != 16777215 and dsec != asec and asec > dsec:
                msg = '発着時刻逆転'
                msgdata.append([train_id, station_id, station_name, msg])
                l.append(msg)
            outline = [str(route_id), train_id, train_id, str(i), str(station_id), \
                       '0', str(asec), str(dsec), '0', '3000', '0', '0', '0']
            outdata.append(outline)

            i += 1

        org_msgdata += train_data

    with open(outfn, 'w', encoding='utf-8') as f:
        header = ['路線ID', '列車番号1', '列車番号2', '順序', '駅ID', '-', \
                  '到着[累積秒]', '出発[累積秒]', '-', '定員', '-', '-', '-']
        f.write('\t'.join(header) + '\n')
        f.write(''.join(['\t'.join(l) + '\n' for l in outdata]))

    with open(msgfn, 'w', encoding='utf-8') as f:
        header = ['列車番号', '駅ID', '駅名', '処理内容']
        f.write('\t'.join(header) + '\n')
        f.write(''.join(['\t'.join(l) + '\n' for l in msgdata]))

    with open(msg2fn, 'w', encoding='utf-8') as f:
        header = ['行番号'] + [x.strip() for x in org_header.split('\t')] + ['処理内容']
        f.write('\t'.join(header) + '\n')
        for l in org_msgdata:
            l[0] += msg2_linestart
            f.write('\t'.join([str(l[0])] + l[1:]) + '\n')
