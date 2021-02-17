#!/usr/bin/python
# codeing: utf-8

import re
import sys
from lines import Line_rapid, sepID

class Split:
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

        self.final_split = None
        self.possible_splits = []
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
        elif len([x in reg_stations for x in self.stations])==1:
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

    def match1line(self, stations, lines):
        
        match_list = []
    
        lineID_p2c = {}
        for lineID in sorted(lines.lines.keys()):
            lineID_p, lineID_s = sepID(lineID)
            if lineID_s is None:
                if lineID in lineID_p2c:
                    print('err ID {0} dup.'.format(lineID))
                    sys.exit()
                lineID_p2c[lineID] = []
            else:
                if not lineID_p in lineID_p2c:
                    print('err ID {0} parent {1} nasi.'.format(lineID, lineID_p))
                    sys.exit()
                lineID_p2c[lineID_p].append(lineID)

        # まず親IDのみからさがす
        for lineID_p in lineID_p2c:
            line_p = lines.lines[lineID_p]
            if not stations[0] in line_p.stations:
                continue
            match_cnt = 0
            for s in stations:
                if s in line_p.stations:
                    match_cnt += 1
                else:
                    break
            # 親ID に二つ以上ある
            if match_cnt > 1:
                # 子ID+親ID で一番長くマッチするものを選択
                found = []
                for lineID_c in [lineID_p] + lineID_p2c[lineID_p]:
                    line_c = lines.lines[lineID_c]
                    line_stations = line_c.stop_stations if line_c.__class__ == Line_rapid \
                        else line_c.stations
                    if not stations[0] in line_stations:
                        continue
                    match_cnt_c = 0
                    line_stations = line_stations[line_stations.index(stations[0]): ]
                    for s, ls in zip(stations, line_stations):
                        if s == ls:
                            match_cnt_c += 1
                        else:
                            break
                    if match_cnt_c <= 1:
                        continue
                    found.append((lineID_c, line_c.name, match_cnt_c))
                if not found:
                    continue
                match_list.append(sorted(found, key=lambda x: x[2], reverse=True)[0])

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
        """
        return match_list

    def match(self, lines):

        v_stations = [x for i, x in enumerate(self.stations) \
            if not i in self.outside_na_idx and not i in self.mid_na_idx]

        def recursive(depth, result=[], first=False):
            depth += 1
            if first:
                mls = self.match1line(v_stations, lines)
                if not mls:
                    return []
                result = [[ml] for ml in mls]
                result = recursive(depth=depth, result=result)

            if result == []:                       
                return []

            new_result = []
            for r in result:
                i = sum([x[2]-1 for x in r])
                if i >= len(v_stations) - 1:
                    new_result.append(r)
                    continue
                mls = self.match1line(v_stations[i: ], lines)
                if not mls:
                    #new_result.append(r)
                    continue
                new_result += [r + [ml] for ml in mls]
            if new_result == []:
                return []
            if new_result == result:
                return result
            result = recursive(depth=depth, result=new_result)
            return result

        match_result = recursive(depth=0, first=True)

        self.possible_splits = []
        for mr in match_result:
            total_cnt = 0
            add_split = []
            for l in mr:
                lineID, linename, cnt = l
                split_stations = self.stations[total_cnt: total_cnt + cnt]
                rt_data = [x for x in self.runtable if x[0] in split_stations]
                total_cnt += cnt - 1
                add_split.append(Split(lineID, linename, rt_data))
            self.possible_splits.append(add_split)
        if len(self.possible_splits) == 1:
            self.final_split = [x for x in self.possible_splits[0]]
            self.result = 0
        else:
            self.result = 1
        #return self.result

    def select_min_split(self):
        pos_length = [len(x) for x in self.possible_splits]
        min_length = min(pos_length)
        self.possible_splits = [x for i, x in enumerate(self.possible_splits) if pos_length[i]==min_length]
        if len(self.possible_splits) == 1:
            self.final_split = self.possible_splits[0]
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
    print(len(vehicle.possible_splits))
    print(len(vehicle.possible_splits))
    for pos in vehicle.possible_splits[0]:
        print(pos.lineID)
        print(pos.linename)
        print(pos.runtable)
    #print(vehicle.possible_splits[0][0].lineID)
    
    #print(vehicle.possible_splits[0][0].linename)
    #print(vehicle.possible_splits[0][0].runtable)
    #for s in vehicle.final_split:
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



