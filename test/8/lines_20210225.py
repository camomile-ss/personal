#!/usr/bin/python
# codeing: utf-8

import re
import sys

id_ptn = re.compile(r'^(Line(\d+))(_(\d+))?$')

def revID(ID):
    ''' reverse_lineID を求める関数 '''
    mob = id_ptn.search(ID)
    #mob = re.search(r'^Line(\d+)(_\d+)?$', ID)
    if not mob:
        return None
    no = int(mob.group(2))
    if no % 2 == 0:
        rev_no = no - 1
    else:
        rev_no = no + 1
    if mob.group(3):
        return 'Line{0:3}{1}'.format(rev_no, mob.group(4))
    else:
        return 'Line{:03}'.format(rev_no)

def sepID(ID):
    ''' lineID を親IDと枝番に分ける関数 '''
    mob = id_ptn.search(ID)
    if not mob:
        return None, None
    if mob.group(3):
        return mob.group(1), int(mob.group(4))
    return mob.group(1), None

class Lines:

    def __init__(self):
        self.lines = {}

    def add_line(self, ID, name, stop_stations):
        if ID in self.lines:
            return -1
        ID_p, ID_s = sepID(ID)
        if ID_p is None:
            return -2 
        # 各駅路線（基本）
        if not ID_s:
            self.lines[ID] = Line(ID, name, stop_stations)
            flg = 0
        # 優等列車（通貨駅あり）
        else:
            parentline = self.lines[ID_p]
            self.lines[ID] = Line_higher(ID, name, parentline.stations, \
                                            ID_p, int(ID_s), stop_stations)
            flg = int(ID_s)
        # 逆路線あるか
        reverseID = revID(ID)
        if ID in ['Line007', 'Line008']:
            print(ID, reverseID)
        if reverseID in self.lines:
            # 逆路線IDをセット
            self.lines[ID].reverseID = reverseID
            self.lines[reverseID].reverseID = ID

        return flg

    def add_new_higher(self, parentID, stop_stations, pass_stations):
        parentline = self.lines[parentID]
        parent_revID = parentline.reverseID
        parent_rev_line = self.lines[parent_revID]      
        if any(not st in parentline.stations for st in stop_stations + pass_stations):
            # エラー 親路線にない駅がある
            return 99
        # 同じ通過駅パターンが既存か探す
        for id, l in self.lines.items():
            # 通過駅に停車しない、停車駅を通過しない、共通の停車駅がふたつ以上ある
            if l.__class__ == Line_higher and l.parentID == parentID \
                and all(not s in l.pass_stations for s in stop_stations) \
                and all(not p in l.stop_stations for p in pass_stations) \
                and len([s for s in stop_stations if s in l.stop_stations]) >= 2:
                # 駅追加
                l.stop_stations = sorted(set(l.stop_stations + stop_stations), \
                                         key=lambda x: l.stations.index(x))
                l.pass_stations = sorted(set(l.pass_stations + pass_stations), \
                                         key=lambda x: l.stations.index(x))
                # 既存に逆路線あれば駅追加
                if l.reverseID:
                    rev_line = self.lines[l.reverseID]
                    rev_line.stop_stations = sorted(set(rev_line.stop_stations + l.stop_stations), \
                                                    key=lambda x: rev_line.stations.index(x))
                    rev_line.pass_stations = sorted(set(rev_line.pass_stations + l.pass_stations), \
                                                    key=lambda x: rev_line.stations.index(x))
                return id

        # 逆路線が既存か探す
        rev_hi_lines = [l for l in self.lines.values() if l.__class__ == Line_higher and \
                                         l.parentID == parent_revID]
        for rl in rev_hi_lines:
            # 逆路線既存
            if all(not s in rl.pass_stations for s in stop_stations) \
                and all(not p in rl.stop_stations for p in pass_stations) \
                and len([s for s in stop_stations if s in rl.stop_stations]) >= 2:

                # 逆路線に駅追加
                rl.stop_stations = sorted(set(rl.stop_stations + stop_stations), \
                                         key=lambda x: rl.stations.index(x))
                rl.pass_stations = sorted(set(rl.pass_stations + pass_stations), \
                                         key=lambda x: rl.stations.index(x))

                # 新しい路線作成
                newID = '{0}_{1}'.format(parentID, rl.ptn_no)
                new_line = Line_higher(newID, None, parentline.stations, parentID, \
                                       rl.ptn_no, stop_stations)
                self.lines[newID] = new_line

                # reverseID 設定
                new_line.reverseID = rl.ID
                rl.reverseID = newID

                return newID

        # 新しい通過駅パターン
        parentline.ptn_cnt += 1
        parent_rev_line.ptn_cnt = parentline.ptn_cnt
        newID = '{0}_{1}'.format(parentID, parentline.ptn_cnt)
        new_line = Line_higher(newID, None, parentline.stations, parentID, \
                               parentline.ptn_cnt, stop_stations)
        self.lines[newID] = new_line
        return newID

    def line_list(self):
        
        data = []
        data.append(['lineID', 'linename', 'vehicle_cnt', 'reverseID', '->stations'])
        sorted_lines = sorted(self.lines.values(), key=lambda x: x.ptn_no)
        sorted_lines = sorted(sorted_lines, key=lambda x: x.parentID if x.__class__ == Line_higher else x.ID)
        #for id, v in sorted(self.lines.items(), key=lambda x: x[0]):
        for l in sorted_lines:
            if l.__class__ == Line:
                linedata = [l.ID, l.name, l.vehicle_cnt, l.reverseID] + l.stations
            elif l.__class__ == Line_higher:
                linedata = [l.ID, l.name or '', l.vehicle_cnt, l.reverseID or '']
                for st in l.stations:
                    if st in l.stop_stations:
                        linedata.append(st)
                    elif st in l.pass_stations:
                        linedata.append('-(pass)-')
                    else:
                        linedata.append('--')
            data.append(linedata)
        return data

    def set_name(self, ID, name):
        '''
        路線名をセット
        [return]
            [flg] 0: OK, -1: err
            [message]
        '''
        # 路線IDがない
        if not ID in self.lines:
            return -1, 'lineID: {} なし'.format(ID)
        
        # 別の路線と路線名重複
        for l in self.lines.values():
            if l.ID != ID and l.name == name:
                return -1, 'lineID {} と路線名重複'.format(l.ID)

        oldname = self.lines[ID].name
        self.lines[ID].name = name
        return 0, 'lineID {0}: 路線名変更 {1} -> {2}'.format(ID, oldname, name)

    def change_ID(self, ID, newID):
        '''
        IDを変更

        '''
        def sep_chk(old_id, new_id):
            old_id_p, old_id_s = sepID(old_id)
            if not old_id_p:
                return -1, 'lineID: {} format err'.format(old_id)
            new_id_p, new_id_s = sepID(new_id)
            if not new_id_p:
                return -1, 'lineID: {} format err'.format(new_id)
            if any(old_id_s and not new_id_s, not old_id_s and new_id_s):
                return -1, '基本路線 <=> 優等路線: {0} {1}'.format(old_id, new_id)
            return 0, (old_id_p, old_id_s, new_id_p, new_id_s)
        
        # 基本路線同士、優等路線同士 以外は不可
        flg, value = sep_chk(ID, newID)
        if flg < 0:
            return flg, value
        ID_p, ID_s, newID_p, newID_s = value

        # 路線IDがない
        if not ID in self.lines:
            return -1, 'lineID: {} なし'.format(ID)

        # 逆路線ID
        reverseID = revID(ID)
        new_reverseID = revID(reverseID) 

        # 新ID or 新IDの逆路線が既存
        if newID in self.lines or new_reverseID in self.lines:
            return -1, 'ID {0} or {1} 既存'.format(newID, new_reverseID)

        # 新IDの親路線がない
        if not newID_p in self.lines:
            return -1, 'parentID {} なし'.format(newID_p)

        # 逆路線がある場合で、逆路線の親路線がない
        if reverseID in self.lines:
            flg, value = sep_chk(reverseID, new_reverseID)
            if flg < 0:
                return flg, value
            reverseID_p, reverseID_s, new_reverseID_p, new_reverseID_s = value
            if not new_reverseID_p in self.lines:
                return -1, '逆路線の parentID {} なし'.format(new_reverseID_p)

        # 変更
        self.lines[newID] = self.lines.pop(ID)
        self.lines[newID].ID = newID
        self.lines[newID].parentID = newID_p
        # 優等路線
        if newID_s:
            self.lines[newID].ptn_no = int(newID_s)
            # 親路線の ptn_cnt 変更
            if self.lines[newID_p].ptn_cnt == ID_s:
                self.lines[newID_p].ptn_cnt -= 1                
            if self.lines[newID_p].ptn_cnt < newID_s:
                self.lines[newID_p].ptn_cnt = newID_s

        # 逆路線あれば変更
        if reverseID in self.lines:
            self.lines[new_reverseID] = self.lines.pop(reverseID)
            self.lines[new_reverseID].ID = new_reverseID
            self.lines[new_reverseID].parentID = new_reverseID_p
            if new_reverseID_s:
                self.lines[new_reverseID].ptn_no = int(new_reverseID_s)
                # 親路線の ptn_cnt 変更
                self.lines[new_reverseID_p].ptn_cnt = self.lines[newID_p].ptn_cnt

        # !!!!!!!!!!! ここから

class Line:
    def __init__(self, ID, name, stations):
        self.ID = ID
        self.name = name
        self.stations = [x for x in stations]
        self.vehicle_cnt = 0
        self.ptn_no = 0
        self.ptn_cnt = 0
        self.reverseID = None

class Line_higher(Line):
    def __init__(self, ID, name, stations, parentID, ptn_no, stop_stations):
        super(Line_higher, self).__init__(ID, name, stations)
        self.parentID = parentID
        self.ptn_no = ptn_no
        self.stop_stations = [x for x in stop_stations]
        self.pass_stations = [x for i, x in enumerate(stations) \
                              if not x in stop_stations \
                                  and i >= stations.index(stop_stations[0]) \
                                  and i <= stations.index(stop_stations[-1])]
