#!/usr/bin/python
# coding: utf-8
'''
(3)-2 運行表を重複削除して路線方面ごとに書き出し
'''
import argparse
import sys
from time import ctime
import os

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='tohoku/v1')
    psr.add_argument('-d', '--deleteshinkansen', choices=('y', 'n'), default='n')
    args = psr.parse_args()
    dirn = args.dirn
    del_sh = args.deleteshinkansen

    infn = os.path.join(dirn, 'runtables_all.txt')
    outdirn = os.path.join(dirn, 'runtables')
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    i_insta, i_ttline, i_ttdirec, i_onsta, i_rtdest, i_vno, i_rtdata = 0, 1, 2, 6, 8, 10, 11

    print('merge start.', ctime())

    unique_data = []
    with open(infn, 'r', encoding='utf-8') as inf:
        header = [x.strip() for x in next(inf).split('\t')]
        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            input_station, tt_line, tt_direc, tt_time, tt_char1, tt_char2, \
                rt_on_station, rt_line, rt_dest, rt_direc, vehicle_no, *rt_data = l

            # 新幹線を削除する場合
            if del_sh == 'y' and any('新幹線' in x for x in [tt_char2, rt_line]):
                continue

            # 新幹線などの場合(列車noがある)
            if vehicle_no:
                # 同じ列車noで運行表が長いほうを生かす
                vehicle_no_list = [x[i_vno] for x in unique_data]
                if vehicle_no in vehicle_no_list:
                    idx = vehicle_no_list.index(vehicle_no)
                    if len(l) > len(unique_data[idx]):
                        unique_data.pop(idx)
                        unique_data.append(l)
                # 新しい列車noは追加
                else:
                    unique_data.append(l)

            # 在来線などの場合(列車noがない)
            else:
                # rt_dest, runtable で同一列車を判断
                zairai_comp = [[x[i_rtdest]] + x[i_rtdata: ] for x in unique_data]
                # 同一列車は rt_on駅が早い方を生かす(遅い方には快速などの情報が無い場合がある)
                if [rt_dest] + rt_data in zairai_comp:
                    idx = zairai_comp.index([rt_dest] + rt_data)
                    rt_on_station_old = unique_data[idx][i_onsta]
                    rt_stations = [rt_data[i] for i in range(0, len(rt_data), 3)]
                    if rt_stations.index(rt_on_station) < rt_stations.index(rt_on_station_old):
                        #unique_data[idx] = [x for x in l]  # 元の位置に上書き
                        unique_data.pop(idx)  # 削除して後ろに追加
                        unique_data.append(l)
                # 新しい列車
                else:
                    unique_data.append(l)
    print('merge end.', ctime())

    # 他の運行票の途中から最後までと一致している運行表はチェックリストに出力して削除する。
    # (たぶん直通のみ？ 後の路線の駅の運行表には前の路線の駅が入らない様子)
    # データを長い順に
    unique_data.sort(key=lambda x: len(x), reverse=True)
    # ひとつずつチェック
    unique_data_remain = []  # チェックで残った運行表
    chkfn = os.path.join(outdirn, 'delete_chk.txt')
    del_cnt = 0
    with open(chkfn, 'w', encoding='utf-8') as chkf:
        # 運行表1行ずつ
        for rt in unique_data:
            rt_head = rt[:11]  # 入力駅~列車番号
            rt_data = rt[11:]  # 運行データ(駅, 時刻, 発or着 の繰り返し)
            # 残った運行表のなかに、後ろが今見てる運行表と一致するものがあるか
            remain = True
            for r_rt in unique_data_remain:
                if rt_data == r_rt[len(r_rt)-len(rt_data):]:
                    del_cnt += 1
                    del_print = ['*delete'] + rt_head + ['']*(len(r_rt)-len(rt)) + rt_data
                    dup_print = ['*duplicate'] + r_rt            
                    chkf.write('[{}]'.format(del_cnt) + '\n')
                    chkf.write('\t'.join(del_print) + '\n')
                    chkf.write('\t'.join(dup_print) + '\n')
                    remain = False
                    break
            if remain:
                unique_data_remain.append(rt)
    # 並び順を元に
    unique_data_remain.sort(key=lambda x: unique_data.index(x))                    
    print('dup check end. out start.', ctime())

    # 出力は、路線方面で分ける
    line_direc_list = set((x[i_ttline], x[i_ttdirec]) for x in unique_data_remain)
    header = [header[i_insta]] + header[i_ttdirec+1: ]
    for l, d in line_direc_list:
        outdata = [x for x in unique_data_remain if x[i_ttline]==l and x[i_ttdirec]==d]
        outdata = [[x[i_insta]] + x[i_ttdirec+1: ] for x in outdata]  # 路線方面はファイル名にあるので抜く
        outfn = os.path.join(outdirn, '{}_{}_runtables.txt'.format(l, d))
        with open(outfn, 'w', encoding='utf-8') as outf:
            outf.write('\t'.join(header) + '\n')
            outf.write(''.join(['\t'.join(l) + '\n' for l in outdata]))

    print('end.', ctime())