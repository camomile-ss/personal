#!/usr/bin/python
# coding: utf-8

'''
(3) 駅・路線・方面リストの、不要フラグないものの、運行表を路線方面ごとに書き出し
'''

from tt_scraping_func import staLineDirec_list2runtable
import argparse
import sys
from time import ctime
import os

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='tohoku/v1')
    #psr.add_argument('infn', help='tohoku/v1/stationlinedirec_n.txt')
    #psr.add_argument('outdirn', help='tohoku/v1/runtables')
    args = psr.parse_args()
    dirn = args.dirn
    #infn = args.infn
    #outdirn = args.outdirn

    infn = os.path.join(dirn, 'stationlinedirec_n.txt')
    outdirn = os.path.join(dirn, 'runtables')

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # 運行表を収集する 駅・路線・方面 リスト作成
    sta_line_direc_list = {}
    with open(infn, 'r', encoding='utf-8') as inf:
        header = [x.strip() for x in next(inf).split('\t')]
        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            _, _, _, station, line, tt_direc, _, n = l
            if n == 'n':
                continue
            if station in sta_line_direc_list:
                if line in sta_line_direc_list[station]:
                    sta_line_direc_list[station][line].append(tt_direc)
                else:
                    sta_line_direc_list[station][line] = [tt_direc]
            else:
                sta_line_direc_list[station] = {line: [tt_direc]}
    
    sta_line_direc_list = [(s, [(l, d_list) for l, d_list in v.items()]) for s, v in sta_line_direc_list.items()]

    # 運行表データを取得
    runtableByVehicle_out, messages = staLineDirec_list2runtable(sta_line_direc_list)
    msgfn = os.path.join(outdirn, 'messages.txt')
    with open(msgfn, 'w', encoding='utf-8') as msgf:
        msgf.write(''.join([x + '\n' for x in messages]))

    # 路線・方面で分ける
    runtableByLineDirec = {}
    for v_data in runtableByVehicle_out:
        station, line, tt_direc, *data = v_data
        if (line, tt_direc) in runtableByLineDirec:
            runtableByLineDirec[(line, tt_direc)].append([station] + data)
        else:
            runtableByLineDirec[(line, tt_direc)] = [[station] + data]

    # 出力
    for k, v in runtableByLineDirec.items():
        line, tt_direc = k
        fn = os.path.join(outdirn, '{0}_{1}_runtables.txt'.format(line, tt_direc))
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\t'.join(['入力駅', 'tt時刻', 'tt文字列1', 'tt文字列2', \
                               'rt_on駅', 'rt路線', 'rt行き先', 'rt方面', \
                               '列車no', '->runtable']) + '\n')
            for v_d in v:
                station, *data, runtable = v_d
                outdata = [station] + data 
                for rt_line in runtable:
                    outdata += rt_line
                f.write('\t'.join([x or '' for x in outdata]) + '\n')
