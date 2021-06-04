#!/usr/bin/python
# codeing: utf-8

import re
import sys
from lines import Line_local, Line_rapid, sepID

class SplitRuntable:
    def __init__(self, lineID, linename, rt_data):
        self.lineID = lineID
        self.linename = linename
        self.runtable = rt_data
        #self.runtable = [tuple(rt_data[i: i*3]) for i in range(len(rt_data))]

def station_adjust(line, direc, station_j):
    ''' ジョルダン運行表に表示される駅名が微妙にちがうことがあるので調整する '''
    if line == '青い森鉄道' and station_j == '青山':
        return '青山（岩手）'
    return station_j

class Vehicle:

    def __init__(self, uni_key, runtableline):
        self.uni_key = uni_key
        # 列車識別項目, 運行表
        self.tt_line, self.tt_direc, self.fileline = uni_key
        self.input_station, self.tt_time, self.tt_char1, self.tt_char2, \
            self.rt_on_sta, self.rt_line, self.rt_dest, self.rt_direc, self.vehicle_no, \
            *self.runtable = runtableline
        self.runtable = [tuple(self.runtable[i: i+3]) for i in range(0, len(self.runtable), 3)]
        self.runtable = [(station_adjust(self.tt_line, self.tt_direc, x[0]), x[1], x[2]) for x in self.runtable]
        # 運行表から駅名リスト取り出し
        #stations = [self.runtable[i] for i in range(0, len(self.runtable), 3)]
        stations = [x[0] for x in self.runtable]
        # stations に、隣接する重複があれば削除
        self.stations = [stations[0]] + [stations[i] for i in range(1, len(stations)) \
                    if stations[i] != stations[i-1]]

        self.final_split_runtables = None
        self.possible_split_runtables = []
        self.outside_na_idx = []
        self.mid_na_idx = []
        self.target = True
        self.result = None

    def chk_stations(self, reg_stations):
        ''' 対象外駅チェック '''

        # 対象駅がひとつもない
        if all([not x in reg_stations for x in self.stations]):
            self.result = -98
            #return -98
        # 対象駅がひとつしかない
        elif [x in reg_stations for x in self.stations].count(True)==1:
            self.result = -96
            #return -96
        else:
            # 対象外駅の位置
            na_idx = [i for i, x in enumerate(self.stations) if not x in reg_stations]
            # 外側
            cnt = 0
            while na_idx and na_idx[0]==cnt:
                self.outside_na_idx.append(na_idx.pop(0))
                cnt += 1
            cnt = len(self.stations) - 1
            while na_idx and na_idx[-1]==cnt:
                self.outside_na_idx.append(na_idx.pop(-1))
                cnt -= 1
            self.outside_na_idx.sort()
            # 内側
            self.mid_na_idx = [i for i in na_idx]
            if self.mid_na_idx:
                self.result = -95
                #return -95
            else:
                self.result = 0
        #return self.result


        #match_list.append(sorted(found, key=lambda x: x[2], reverse=True)[0])

        """
        for lineID, line in lines.lines.items():
            line_stations = line.stop_stations if line.__class__ == Line_rapid else line.stations
            if not stations[0] in line_stations:
                continue
            match_cnt = 0
            for s, ls in zip(stations, line_stations[line_stations.index(stations[0]):] ):
                if s == ls:
                    match_cnt += 1
                else:
                    break
            if match_cnt <= 1:
                continue
            match_list.append((line.ID, line.name, match_cnt))
        return match_list
        """

    def match(self, lines):
        ''' 再帰的にマッチする路線を探して列車データを分割 '''
        v_stations = [x for i, x in enumerate(self.stations) \
            if not i in self.outside_na_idx and not i in self.mid_na_idx]

        def judge_match(stations, lineIDm):

            # 親路線確認 -> 最初の2駅以上がなければng
            line_p = lines.lines[lineIDm]
            # 最初の駅なし
            if not stations[0] in line_p.stations:  
                return []
            cnt = 0
            for s in stations:
                if s in line_p.stations:
                    cnt += 1
                else:
                    break
            # 最初の駅しか一致しない
            if cnt <= 1:  
                return []

            # 親路線と子路線 で一番長くマッチするものを選択
            lines_c = [l for l in lines.lines.values() \
                       if l.__class__==Line_rapid and l.parentID==lineIDm]
            lines_search = [line_p] + lines_c
            found = []
            for l in lines_search:
                l_stations = l.stop_stations if l.__class__ == Line_rapid else l.stations
                if not stations[0] in l_stations:
                    continue
                cnt2 = 0
                # 最初の駅から順に一致する数を調べる
                l_stations = l_stations[l_stations.index(stations[0]): ]
                for s, ls in zip(stations, l_stations):
                    if s == ls:
                        cnt2 += 1
                    else:
                        break
                # 1駅しか一致しないのは飛ばす
                if cnt2 <= 1:
                    continue
                found.append((l, cnt2))
            # マッチする路線なし
            if not found:
                return []
            # マッチ駅数最大の路線を返す（複数）
            max_length = max([x[1] for x in found])
            found = [x for x in found if x[1==max_length]]
            return found  # (line, マッチ長さ) のリスト

        def find_match_lines(org_i=0, org_split=[], found_splits=[], depth=0):
            ''' 再帰的にマッチする路線を探す '''
            depth += 1
            # 主路線IDリスト
            lineIDms = [ID for ID, l in lines.lines.items() if l.__class__==Line_local]
            # 主路線ごとに
            for lineIDm in lineIDms:
                # マッチする路線があるか
                found = judge_match(v_stations[org_i: ], lineIDm)
                for f in found:
                    # 分割路線に追加
                    _, cnt = f
                    split = org_split + [f]
                    i = org_i + cnt - 1
                    # 終着駅まで分割終了
                    if i >= len(v_stations) - 1:
                        found_splits.append(split)
                        continue
                    else:
                        found_splits = find_match_lines(i, split, found_splits, depth)
            return found_splits

        found_splits = find_match_lines()

        self.possible_split_runtables = []
        for sp in found_splits:
            total_cnt = 0
            split_runtables = []
            for ml, cnt in sp:
                lineID, linename = ml.ID, ml.name
                #split_stations = self.stations[total_cnt: total_cnt + cnt]
                split_stations = v_stations[total_cnt: total_cnt + cnt]
                rt_data = [x for x in self.runtable if x[0] in split_stations]
                total_cnt += cnt - 1
                split_runtables.append(SplitRuntable(lineID, linename, rt_data))
            self.possible_split_runtables.append(split_runtables)
        if len(self.possible_split_runtables) == 1:
            self.final_split_runtables = [x for x in self.possible_split_runtables[0]]
            self.result = 0
        else:
            self.result = 1

    def select_min_split(self):
        pos_length = [len(x) for x in self.possible_split_runtables]
        min_length = min(pos_length)
        self.possible_split_runtables = [x for i, x in enumerate(self.possible_split_runtables) if pos_length[i]==min_length]
        if len(self.possible_split_runtables) == 1:
            self.final_split_runtables = self.possible_split_runtables[0]
            self.result = 0

if __name__ == '__main__':
    infn = 'tohoku/test.txt'
    with open(infn, 'r', encoding='utf-8') as inf:
        dat = [x.strip() for x in next(inf).split('\t')]

    #unikey = ('大糸線（東日本）', '松本方面', 21)
    unikey = ('リバティ', '会津田島方面', 1)
    vehicle = Vehicle(unikey, dat)

    from runtable_matchline_func import cve2lines, mk_station_conv
    stalinedirec_fn = 'tohoku/v2/stationlinedirec_n.txt'
    cvedirn='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v8'
    llfn = 'lines_list_test.txt'

    station_conv = mk_station_conv(stalinedirec_fn)
    # Lines instance
    lines = cve2lines(cvedirn, station_conv, llfn)

    vehicle.chk_stations(station_conv.values())
    vehicle.match(lines)
    print(len(vehicle.possible_split_runtables))
    print(len(vehicle.possible_split_runtables))
    for pos in vehicle.possible_split_runtables[0]:
        print(pos.lineID)
        print(pos.linename)
        print(pos.runtable)
    #print(vehicle.possible_split_runtables[0][0].lineID)
    
    #print(vehicle.possible_split_runtables[0][0].linename)
    #print(vehicle.possible_split_runtables[0][0].runtable)
    #for s in vehicle.final_split_runtables:
    #    print(s.lineID)
    #    print(s.linename)
    #    print(s.runtable)

    


    """
        if self.mid_na_idx:
            return -95
        target_stations = [x for i, x in enumerate(self.stations) if not i in self.outside_na_idx]

        # 
        tar_idx = 0
        match_list = self.match1line(target_stations[tar_idx: ], lines)
        for ml in match_list #!!!!!!!!! ここから

    """


    """
        if not stations:
            self.stations = []
        else:
            # station に、隣接する重複があれば削除
            self.stations = [stations[0]] + [stations[i] for i in range(1, len(stations)) \
                        if stations[i] != stations[i-1]]
        self.lineIDs = []
        self.match_stations = None
        self.middle_start, self.middle_end = None, None
        self.pass_stations, self.outside_ng_stations, self.mid_ng_stations = None, None, None
        self.stations_split = None
    """
    #def split(self, lines):



