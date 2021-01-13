#!/usr/bin/python
# coding: utf-8
"""
unkouhyo.txt -> unkouhyo_conv.txt
路線・駅 railstation に合わせる。（カラムを追加）
"""
import argparse
import os
import sys

class Convert:
    def __init__(self, dirn, rsfn):

        cfn = os.path.join(dirn, 'linecd_conv.txt')
        with open(cfn, 'r', encoding='cp932') as cf:
            # ｛(jordan路線, jordan方面): 路線名}
            self.linecd_conv = {(r[0], r[1]): r[2] for r in [[x.strip() for x in l.split('\t')] for l in cf]}
        # 駅順データ {路線名: [駅名, 駅名, ....]}
        self.rsdata = {}
        self.station_nm2id = {}  # 駅名 -> 駅ID
        with open(rsfn, 'r', encoding='utf-8') as rsf:
            for l in rsf:
                l = l.split('\t')
                line, cd, station = l[1], l[5], l[7]
                if line in self.rsdata:
                    self.rsdata[line].append(station)
                else:
                    self.rsdata[line] = [station]
                self.station_nm2id[station] = cd

    def convert_onetrain(self, data):
        '''
        列車いっこ分のデータを変換
        (1)jordan路線・方面からデータ用の路線名に
        (2)jordan駅名のカッコの部分は削除（暫定：大阪メトロはこれで大丈夫そう）
        (3)railstationと駅名の並び順チェック
            ・乗り入れ別路線の駅の行は削除（railstationのその路線にない駅）
            ・駅の抜けないかチェック（通過駅あると動かないめんどい）
        # (1), (2) はうしろのカラムにくっつける(8,9)
        '''
        outdata = []
        for l in data:
            no, line, direc, dest, typ, station, time_, io_ = l
            # (1)
            if (line, direc) in self.linecd_conv:
                l.append(self.linecd_conv[(line, direc)])
            else:
                print('[err] line: {0}, direcion: {1} not in linecd_conv.txt.'.format(line, direc))
                sys.exit()
            # (2)
            l.append(station[:station.index('（')] if '（' in station else station)
            outdata.append(l)

        # (3)
        dt_stations = [l[9] for l in outdata]  # データの駅並び
        rs_stations = self.rsdata[(outdata[0][8])]  # railstation の駅並び
        o_stations = [x for x in dt_stations if x in rs_stations]  # 共通
        # 共通に、データ中の間抜けないか
        dt_idx = [dt_stations.index(x) for x in o_stations]
        if any([dt_idx[i+1]-dt_idx[i]!=1 for i in range(len(dt_idx)-1)]):
            print('[err] 対象駅の間に違う駅あり train no: {}'.format(data[0][0]))
            sys.exit()
        # 通過駅ないか
        rs_idx = [rs_stations.index(x) for x in o_stations]
        if any([rs_idx[i+1]-rs_idx[i]!=1 for i in range(len(rs_idx)-1)]):
            print('[err] 通過駅あり train no: {}'.format(data[0][0]))
            sys.exit()

        # いらん駅さくじょ, 駅IDカラム追加
        return [outdata[i] + [self.station_nm2id[outdata[i][9]]] for i in dt_idx]

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirname')
    psr.add_argument('rsfname', help='railstation.txt or railstation_master.txt')
    args = psr.parse_args()
    dirn = args.dirname
    rsfn = args.rsfname

    infn = os.path.join(dirn, 'unkouhyo.txt')
    outfn = os.path.join(dirn, 'unkouhyo_conv.txt')

    conv = Convert(dirn, rsfn)

    with open(infn, 'r', encoding='utf-8') as inf, open(outfn, 'w', encoding='utf-8') as outf:
        prev_no = None
        one_train_data = []
        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            no, line, direc, dest, typ, station, time_, io_ = l
            if prev_no is None:
                prev_no = no
            # 列車番号かわったとこで処理
            if no != prev_no:
                outf.write(''.join(['\t'.join(l) + '\n' for l in conv.convert_onetrain(one_train_data)]))
                # データリセット、新しい列車の1行目セット
                one_train_data = [l]
                prev_no = no
                continue
            one_train_data.append(l)
        # 最後の列車の処理
        if not prev_no is None:
            outf.write(''.join(['\t'.join(l) + '\n' for l in conv.convert_onetrain(one_train_data)]))
