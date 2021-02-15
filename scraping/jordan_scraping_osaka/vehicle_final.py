#!/usr/bin/python
# codeing: utf-8

import re
import sys
from lines import Line_rapid

class Split:
    def __init__(self, lineID, linename, rt_data):
        self.lineID = lineID
        self.linename = linename
        self.runtable = [tuple(rt_data[i: i*3]) for i in range(len(rt_data))]

def station_adjust(line, direc, station_j):
    ''' ジョルダン運行表に表示される駅名が微妙にちがうことがあるので調整する '''
    if line == '青い森鉄道' and station_j == '青山':
        return '青山（岩手）'
    return station_j

class Vehicle:

    def __init__(self, uni_key, fileline, tt_line, tt_direc, runtableline):
        self.uni_key = uni_key
        # 列車識別項目, 運行表
        self.tt_line, self.tt_direc, self.fileline = uni_key
        self.input_station, self.tt_time, self.tt_char1, self.tt_char2, \
            self.rt_on_sta, self.rt_line, self.rt_dest, self.rt_direc, self.vehicle_no, \
            *self.runtable = runtableline
        # 運行表から駅名リスト取り出し
        stations = [self.runtable[i] for i in range(0, len(self.runtable), 3)]
        # stations に、隣接する重複があれば削除
        self.stations = [stations[0]] + [stations[i] for i in range(1, len(stations)) \
                    if stations[i] != stations[i-1]]
        self.stations = [station_adjust(tt_line, tt_direc, x) for x in self.stations]

        self.final_split = None
        self.possible_splits = []
        self.outside_na_idx = []
        self.mid_na_idx = []
        self.target = True

    def chk_stations(self, reg_stations):
        ''' 対象外駅チェック '''
        # 対象駅がひとつもない
        if all([not x in reg_stations for x in self.stations]):
            return -98
        # 対象駅がひとつしかない
        if len([x in reg_stations for x in self.stations])==1:
            return -96
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
            return -95
        return 0

    def match1line(self, stations, lines):
        
        match_list = []
        for line in lines:
            line_stations = line.stop_stations if line.__class__ == Line_rapid else line.stations
            if not stations[0] in line_stations:
                continue
            match_cnt = 0
            for s, ls in zip(stations, line_stations[stations[0]:] ):
                if s == ls:
                    match_cnt += 1
            if match_cnt == 1:
                continue
            match_list.append((line.ID, line.name, match_cnt))
        return match_list

    def match(self, lines):

        return 0        
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



