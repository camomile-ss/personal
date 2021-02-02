#!/usr/bin/python
# codeing: utf-8

import re
import sys

class Vehicle:

    def __init__(self, stations):
        if not stations:
            self.stations = []
            self.flg = 99
        else:
            self.flg = None
            # station に、隣接する重複があれば削除
            self.stations = [stations[0]] + [stations[i] for i in range(1, len(stations)) \
                        if stations[i] != stations[i-1]]
        self.lineIDs = []
        self.match_stations = None
        self.middle_start, self.middle_end = None, None
        self.pass_stations, self.outside_ng_stations, self.mid_ng_stations = None, None, None
        self.stations_split = None

    def chk(self, line_stations):
        '''
        路線とマッチするか試す
        [return]
        flg: 0: OK
             7: 路線にない駅が外側にある（直通かも）
             8: 通過駅あり
             96: err 路線にない駅が途中にある
             97: err 路線と駅順が違う
             98: err 全ての駅が路線にない
             99: err 列車のstations が空
            # (数字の大きいほうのエラーflg返る)
        '''
        if self.flg == 99:
            return 99

        flg = 0

        remain_stations = [x for x in self.stations]

        # ng駅あるかどうかチェック
        if any(not x in line_stations for x in remain_stations):
            
            # 先頭ng駅を削除 --------------------------------------##
            pop_stations = []
            while remain_stations and not remain_stations[0] in line_stations:
                pop_stations.append(remain_stations.pop(0))

            # 駅が残っていなければエラー -> 終了
            if not remain_stations:
                self.mid_ng_stations = [x for x in pop_stations]
                return 98

            # 末尾ng駅を削除 --------------------------------------##
            while remain_stations and not remain_stations[-1] in line_stations:
                pop_stations.append(remain_stations.pop(-1))

            # 外側ng駅
            self.outside_ng_stations = [x for x in sorted(pop_stations, \
                                            key=lambda x: self.stations.index(x))]
            # 途中ng駅 --------------------------------------------## 
            self.mid_ng_stations = [x for x in remain_stations if not x in line_stations]
            # あったらエラー
            if self.mid_ng_stations:
                flg = 96
                remain_stations = [x for x in remain_stations if x in line_stations]
            else:
                # エラーでない -> 外側のみng駅あり
                flg = 7

        # 路線とマッチする部分
        self.match_stations = [x for x in remain_stations]

        # 路線の途中始発・終着
        if self.match_stations[0] != line_stations[0]:
            self.middle_start = self.match_stations[0]
        if self.match_stations[-1] != line_stations[-1]:
            self.middle_end = self.match_stations[-1]

        # 順番チェック
        orders = [line_stations.index(x) for x in self.match_stations]
        # 駅順が違う
        if any(orders[i] >= orders[i+1] for i in range(len(orders) - 1)):
            flg = 97

        # エラーは終了(flg = 96, 97)
        if flg >= 90:
            return flg

        # 通過駅あるかチェック ---------------------------------------##

        # 路線の、列車始発〜終着の部分
        start_idx = line_stations.index(self.match_stations[0])
        end_idx = line_stations.index(self.match_stations[-1])
        line_stations_part = line_stations[start_idx: end_idx+1]

        # 通過駅リストアップ
        self.pass_stations = [x for x in line_stations_part if not x in self.match_stations]

        """
        # 路線の停車・通過
        for s in line_stations:
            # 停車
            if s in self.match_stations:
                self.rail_stations_stop.append(rs)
            # 通過
            elif rs in self.pass_stations:
                self.rail_stations_stop.append('(-{}-)'.format(rs))
            else:
                self.rail_stations_stop.append('-')
        """

        if self.pass_stations:
            flg = 8

        return flg

class Lines:

    def __init__(self):
        self.lines = {}
        self.ptn = re.compile(r'^(Line\d+)(_(\d+))?$')

    def add_line(self, lineID):
        if lineID in self.lines:
            return -1
        else:
            mob = self.ptn.search(lineID)
            if not mob:
                print('lineID err: {}'.format(lineID)) 
                sys.exit()   
            ID_p, ID_s = mob.group(1), mob.group(3)
            if not ID_s:
                self.lines[lineID] = Line()
                return 0
            else:
                self.lines[lineID] = Line_higher(ID_p, int(ID_s))
                return int(ID_s)

    def set_line_stations(self, lineID, name, stations):
        if self.lines[lineID].__class__ == Line:
            self.lines[lineID].set_line_stations(name, stations)
        elif self.lines[lineID].__class__ == Line_higher:
            parentStations = self.lines[self.lines[lineID].parentlineID].stations
            self.lines[lineID].set_line_stations(name, stations, parentStations)

    def add_higher(self, parentlineID, match_stations, pass_stations):
        parentline = self.lines[parentlineID]
        if any(not st in parentline.stations for st in match_stations + pass_stations):
            # エラー 親路線にない駅がある
            return 99
        # 同じ通過駅パターンが既存か探す
        for id, l in self.lines.items():
            if l.__class__ == Line_higher and l.parentlineID == parentlineID \
                and all(not m in l.pass_stations for m in match_stations) \
                and all(not p in l.stop_stations for p in pass_stations):
                # 既存
                l.vehicle_cnt += 1
                # 駅追加
                l.stop_stations = sorted(set(l.stop_stations + match_stations), \
                                         key=lambda x: l.stations.index(x))
                l.pass_stations = sorted(set(l.pass_stations + pass_stations), \
                                         key=lambda x: l.stations.index(x))
                # 逆路線あれば駅追加
                if l.reverse_lineID:
                    rev_line = self.lines[l.reverse_lineID]
                    rev_line.stop_stations = sorted(set(rev_line.stop_stations + l.stop_stations), \
                                                    key=lambda x: rev_line.stations.index(x))
                    rev_line.pass_stations = sorted(set(rev_line.pass_stations + l.pass_stations), \
                                                    key=lambda x: rev_line.stations.index(x))
                return id
        # 新しい通過駅パターン
        parentline.ptn_cnt += 1
        new_line = Line_higher(parentlineID, parentline.ptn_cnt)
        new_line.stations = [x for x in parentline.stations]
        new_line.stop_stations = [x for x in match_stations]
        new_line.pass_stations = [x for x in pass_stations]
        new_line.vehicle_cnt += 1
        new_lineID = '{0}_{1}'.format(parentlineID, new_line.ptn_no)
        # 逆路線既存か
        parent_rev_lineID = parentline.reverse_lineID
        rev_lineIDs = [id for id, l in self.lines.items() if l.__class__ == Line_higher and \
                                         l.parentlineID == parent_rev_lineID]
        rev_lines = [self.lines[x] for x in rev_lineIDs]
        for id, l in zip(rev_lineIDs, rev_lines):
            if all(not s in l.pass_stations for s in new_line.stop_stations) \
                and all(not p in l.stop_stations for p in new_line.pass_stations):
                # 駅追加
                l.stop_stations = sorted(set(l.stop_stations + new_line.stop_stations), \
                                         key=lambda x: l.stations.index(x))
                l.pass_stations = sorted(set(l.pass_stations + new_line.pass_stations), \
                                         key=lambda x: self.lines[id].stations.index(x))
                new_line.reverse_lineID = id
                l.reverse_lineID = new_lineID
                break
        self.lines[new_lineID] = new_line
        return new_lineID

    def line_list(self):
        
        data = []
        data.append(['lineID', 'linename', 'vehicle_cnt', 'reverseID', '->stations'])
        for id, v in sorted(self.lines.items(), key=lambda x: x[0]):
            if v.__class__ == Line:
                linedata = [id, v.name, v.vehicle_cnt, v.reverse_lineID] + v.stations
            elif v.__class__ == Line_higher:
                linedata = [id, v.name or '', v.vehicle_cnt, v.reverse_lineID or '']
                for st in v.stations:
                    if st in v.stop_stations:
                        linedata.append(st)
                    elif st in v.pass_stations:
                        linedata.append('-(pass)-')
                    else:
                        linedata.append('--')
            data.append(linedata)
        return data

class Line:

    def __init__(self):
        self.name = None
        self.stations = None
        self.vehicle_cnt = 0
        self.ptn_no = 0
        self.ptn_cnt = 0
        self.reverse_lineID = None

    def set_line_stations(self, name, stations):
        self.name = name
        self.stations = [x for x in stations]

#    def vehicle_cnt_up(self):
#        self.vehicle_cnt += 1

class Line_higher(Line):
    def __init__(self, parentlineID, ptn_no):
        super(Line_higher, self).__init__()
        self.parentlineID = parentlineID
        self.ptn_no = ptn_no
        self.stop_stations = None
        self.pass_stations = None

    def set_line_stations(self, name, stations, parentStations):
        self.name = name
        self.stations = [x for x in parentStations]
        self.stop_stations = [x for x in stations]
        self.pass_stations = [x for x in parentStations if not x in stations]
