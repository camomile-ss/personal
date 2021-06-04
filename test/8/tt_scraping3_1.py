#!/usr/bin/python
# coding: utf-8

'''
(3) 駅・路線・方面リストの、不要フラグないものの、運行表をすべて書き出し
'''

from tt_scraping_func import staLineDirec2timetable, timetable2runtable
import argparse
import sys
from time import ctime
import os

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='tohoku/v1')
    psr.add_argument('-k', '--kubun', help='入出力ファイル名を変えたい時', default='')
    args = psr.parse_args()
    dirn = args.dirn
    kubun = args.kubun

    if kubun:
        kubun = '_' + kubun
    infn = os.path.join(dirn, 'stationlinedirec_n{}.txt'.format(kubun))
    outfn = os.path.join(dirn, 'runtables_all{}.txt'.format(kubun))
    msgfn = os.path.join(dirn, 'runtables_all_messages{}.txt'.format(kubun))

    # 運行表を収集する 駅・路線・方面 リスト
    sta_line_direc_list = []
    with open(infn, 'r', encoding='utf-8') as inf:
        header = [x.strip() for x in next(inf).split('\t')]
        data = [[x.strip() for x in r.split('\t')] for r in inf]
    s_l_d_list = [(s, l, d) for _, _, _, s, l, d, _, n in data if n!='n']

    with open(outfn, 'w', encoding='utf-8') as outf, \
         open(msgfn, 'w', encoding='utf-8') as msgf:

        outf.write('\t'.join(['入力駅', '入力路線', '入力方面', 'tt時刻', 'tt文字列1', 'tt文字列2', \
                            'rt_on駅', 'rt路線', 'rt行き先', 'rt方面', \
                            '列車no', '->runtable']) + '\n')
        # 運行表データを取得
        for i, (s, l, d) in enumerate(s_l_d_list):
            
            print('{0}/{1} {2} {3} {4} {5}'.format(i+1, len(s_l_d_list), s, l, d, ctime()))
            
            timetable, message1, message2 = staLineDirec2timetable(s, l, d)
            if message1:
                msgf.write('{0} {1} {2}\n'.format(s, l, message1))
            if message2:
                msgf.write('{0} {1} {2} {3}\n'.format(s, l, d, message1))
            
            runtableByVehicle, messages = timetable2runtable(timetable)

            if messages:
                msgf.write(''.join([', '.join([s, l, d, x]) + '\n' for x in messages]))

            for r in runtableByVehicle:
                *labels, runtable = r
                outdata = [s, l, d] + labels + [x for r in runtable for x in r]
                outf.write('\t'.join([x or '' for x in outdata]) + '\n')
