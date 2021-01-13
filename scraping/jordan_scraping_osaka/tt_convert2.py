#!/usr/bin/python
# coding: utf-8
"""
unkouhyo_conv.txt -> timetable_master.txt
・データ編集(自動化)ツール用時刻表データに変換
# 定員はとりま1000
"""
import argparse
import os
import sys
import re

def conv_1train(data_1train):

    # (定数)
    tsutei = '2'  # 通停区分 2
    ttype = '0'  # 列車種別 0
    capa = 1000  # 定員
    stopper = 16777215  # 時刻stopper

    date_thres = 4  # 4時以降は当日
    stop_time = 30  # 停車時間30秒に設定

    # 列車ID
    trno = 'Train{:04}'.format(int(data_1train[0][0]))

    # convert
    outdata_1train, time_chk = [], []
    for i, l in enumerate(data_1train):
        no, _, _, _, _, _, time_, io, line, station, staid = l

        # 着時刻(秒)、発時刻(秒) <- 時刻, 発着
        mob = re.search(r'^(\d{1,2}):(\d\d)$', time_)
        if not mob:
            print('time char err {0}'.format(time_))
            sys.exit()
        hr, mn = int(mob.group(1)), int(mob.group(2))
        if hr < date_thres:
            hr += 24
        sec = hr * 3600 + mn * 60
        if io == '発':
            time_a, time_d = sec - stop_time, sec
        elif io == '着':
            time_a, time_d = sec, sec + stop_time
        else:
            print('発着?', io)
            sys.exit()

        outdata_1train.append([trno, trno, str(i), staid, '0', tsutei, str(time_a), str(time_d),
                               '3', '0', ttype, '0', line, str(capa), '-'])
        time_chk.extend([time_a, time_d])  # 時間前後チェック用

    # 時間前後チェック
    if any([x <= 0 for x in [time_chk[i+1] - time_chk[i] for i in range(len(time_chk) - 1)]]):
        print('[err] 時間逆順あり no: {}'.format(data_1train[0][0]))

    # stopper
    outdata_1train[0][6] = str(stopper)
    outdata_1train[-1][7] = str(stopper)

    return outdata_1train

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirname')
    args = psr.parse_args()
    dirn = args.dirname

    infn = os.path.join(dirn, 'unkouhyo_conv.txt')
    outfn = os.path.join(dirn, 'timetable_master.txt')

    with open(infn, 'r', encoding='utf-8') as inf, open(outfn, 'w', encoding='utf-8') as outf:

        prev_no = None
        data_1train = []
        for l in inf:

            l = [x.strip() for x in l.split('\t')]
            no = l[0]

            if no == prev_no:
                data_1train.append(l)
            else:
                # 1列車データ出力
                if prev_no:
                    outdata_1train = conv_1train(data_1train)
                    outf.write(''.join(['\t'.join(lo) + '\n' for lo in outdata_1train]))
                # リセット
                data_1train = [l]
                prev_no = no

        # 最後の列車データ出力
        if prev_no:
            outdata_1train = conv_1train(data_1train)
            outf.write(''.join(['\t'.join(lo) + '\n' for lo in outdata_1train]))
