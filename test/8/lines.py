#!/usr/bin/python
# codeing: utf-8

import re
import sys

def mobID(ID):
    return re.search(r'^(Line(\d+))(_(\d+))?$', ID)

def revID(ID):
    ''' reverse_lineID を求める関数 '''
    mob = mobID(ID)
    if not mob:
        return None
    no = int(mob.group(2))
    if no % 2 == 0:
        rev_no = no - 1
    else:
        rev_no = no + 1
    if mob.group(3):
        return 'Line{0:03}_{1}'.format(rev_no, mob.group(4))
    return 'Line{:03}'.format(rev_no)

def sepID(ID):
    ''' lineID を親IDと枝番に分ける関数 '''
    mob = mobID(ID)
    if not mob:
        return None, None
    if mob.group(3):
        return mob.group(1), int(mob.group(4))
    return mob.group(1), None

def ptn_no(ID):
    ''' ID から 枝番を返す関数 (各駅路線の場合は0) '''
    mob = re.search(r'^Line\d+(_(\d+))?$', ID)
    if not mob:
        return
    if mob.group(1):
        return int(mob.group(2))
    return 0

class Lines:
    def __init__(self):
        self.lines = {}

    def add_line(self, ID, name, stop_stations, parentID=None):
        ''' 路線追加 '''

        def chk_new_rapid(ID, parentID, stop_stations):
            ''' 新しい優等路線のチェック '''
            # 停車駅に重複ないか
            if any(stop_stations.count(x) > 1 for x in stop_stations):
                return -2
            # 停車駅がすべて親路線にあるか
            if not all(x in self.lines[parentID].stations for x in stop_stations):
                return -3
            # 逆路線IDが既存なら、停車駅が同じか
            reverseID = revID(ID)
            if reverseID in self.lines:
                if any(not x in self.lines[reverseID].stop_stations for x in stop_stations) \
                    or any(not y in stop_stations for y in self.lines[reverseID].stop_stations):
                    return -4
            return 0

        def add_new_rapid(ID, parentID, stop_stations):
            ''' 優等路線追加 '''
            # 優等路線チェック
            chk = chk_new_rapid(ID, parentID, stop_stations)
            # チェックOKなら路線追加、ptn_cnt更新
            if chk < 0:
                return chk
            self.lines[ID] = Line_rapid(ID, name, self.lines[parentID].stations, parentID, \
                                        stop_stations)
            self.lines[parentID].ptn_cnt += 1
            self.lines[self.lines[parentID].reverseID].ptn_cnt += 1
            return 0

        # ID なし -> 親路線から優等路線IDを採番して追加する
        if ID is None:
            # 親IDあるか
            if not parentID:
                return -9
            # 親路線があるか
            if not parentID in self.lines: 
                return -1
            # ID を採番する
            ptn_no = self.lines[parentID].ptn_cnt + 1
            ID = '{0}_{1}'.format(parentID, ptn_no)
            # 優等路線追加
            chk = add_new_rapid(ID, parentID, stop_stations)
            if chk < 0:
                return chk

        # ID あり -> ID から路線を追加
        else:
            # ID が新規か
            if ID in self.lines:
                return -1
            ID_p, ID_s = sepID(ID)
            # ID の format OK か
            if ID_p is None:
                return -2 
            # 各駅路線（基本）
            if not ID_s:
                self.lines[ID] = Line_local(ID, name, stop_stations)

            # 優等列車（通過駅あり）
            else:
                # 親路線があるか
                if not ID_p in self.lines: 
                    return -1
                # 優等路線追加
                chk = add_new_rapid(ID, ID_p, stop_stations)
                if chk < 0:
                    return chk

            # 逆路線あるか
            reverseID = revID(ID)
            if reverseID in self.lines:
                # 逆路線IDをセット
                self.lines[ID].reverseID = reverseID
                self.lines[reverseID].reverseID = ID

        return ID

    def search_rapid_or_add(self, parentID, stop_stations, pass_stations):
        '''
        (1)マッチするパターンの優等路線をさがす
        (2)なかったら新しい優等路線を追加する
        [return]
            (1) 見つかった路線ID
            (2) 新しい路線ID
        '''
        parentline = self.lines[parentID]
        parent_revID = parentline.reverseID
        parent_rev_line = self.lines[parent_revID]      
        if any(not st in parentline.stations for st in stop_stations + pass_stations):
            # エラー 親路線にない駅がある
            return 99

        # 同じ通過駅パターンが既存か探す
        for id, l in self.lines.items():
            # 通過駅に停車しない、停車駅を通過しない、共通の停車駅がふたつ以上ある
            if l.__class__ == Line_rapid and l.parentID == parentID \
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
        rev_hi_lines = [l for l in self.lines.values() if l.__class__ == Line_rapid and \
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
                _, ptn_no = sepID(rl.ID)
                newID = '{0}_{1}'.format(parentID, ptn_no)
                new_line = Line_rapid(newID, None, parentline.stations, parentID, \
                                       sorted(rl.stop_stations, key=lambda x: parentline.stations.index(x)))
                #                       stop_stations)
                self.lines[newID] = new_line

                # reverseID 設定
                new_line.reverseID = rl.ID
                rl.reverseID = newID

                return newID

        # 新しい通過駅パターン
        parentline.ptn_cnt += 1
        parent_rev_line.ptn_cnt = parentline.ptn_cnt
        newID = '{0}_{1}'.format(parentID, parentline.ptn_cnt)
        new_line = Line_rapid(newID, None, parentline.stations, parentID, stop_stations)
        self.lines[newID] = new_line
        return newID

    def line_list(self):
        '''
        親路線の全線にわたって、停車駅は駅名、通過駅は-(pass)-、通らない駅は-- としたリストを返す
        '''
        
        data = []
        data.append(['lineID', 'linename', 'vehicle_cnt', 'reverseID', '->stations'])
        sorted_lines = sorted(self.lines.values(), key=lambda x: ptn_no(x.ID))
        sorted_lines = sorted(sorted_lines, key=lambda x: x.parentID if x.__class__ == Line_rapid else x.ID)
        for l in sorted_lines:
            if l.__class__ == Line_local:
                linedata = [l.ID, l.name, str(l.vehicle_cnt), l.reverseID] + l.stations
            elif l.__class__ == Line_rapid:
                linedata = [l.ID, l.name or '', str(l.vehicle_cnt), l.reverseID or '']
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
            0, 変更前路線名  -> OK
            -1, ID           -> 路線IDがない
            -2, 他路線ID     ^> 路線名重複
        * 
        '''
        # 路線IDがない
        if not ID in self.lines:
            return -1, ID
        
        # 別の路線と路線名重複
        for l in self.lines.values():
            if l.ID != ID and l.name == name:
                return -2, l.ID

        oldname = self.lines[ID].name
        self.lines[ID].name = name
        return 0, oldname

    def change_ID(self, ID, newID):
        '''
        IDを変更
        [return]
            flg
            (reverseID, new_reverseID) or message
        '''
        ## check ---------------------------------------------------------##
        # 変更前路線IDのデータがあるか
        if not ID in self.lines:
            return -1, 'lineID: {} なし'.format(ID)
        ID_p, ID_s = sepID(ID)
        newID_p, newID_s = sepID(newID)
        # IDのフォーマットOKか
        if not ID_p or not newID_p:
            return -1, '{0} or {1} format err'.format(ID, newID)
        # 優等路線同士か
        if not ID_s or not newID_s:
            return -1, '{0} or {1} 各駅路線'.format(ID, newID)
        # 親路線が同じか
        if newID_p != ID_p:
            return -1, '{0} -> {1} 親路線が別'.format(ID, newID)

        # 逆路線ID
        reverseID = revID(ID)
        new_reverseID = revID(newID)

        # 新ID or 新IDの逆路線が既存でないか
        if newID in self.lines or new_reverseID in self.lines:
            return -1, 'ID {0} or {1} 既存'.format(newID, new_reverseID)

        # 変更 ------------------------------------------------------------##
        # ID 変更
        self.lines[newID] = self.lines.pop(ID)
        self.lines[newID].ID = newID

        # 親路線の ptn_cnt 変更
        new_parentline = self.lines[self.lines[newID].parentID]
        if new_parentline.ptn_cnt == ID_s:
            new_parentline.ptn_cnt -= 1                
        if new_parentline.ptn_cnt < newID_s:
            new_parentline.ptn_cnt = newID_s
        # 親路線の逆路線の ptn_cnt 変更
        self.lines[new_parentline.reverseID].ptn_cnt = new_parentline.ptn_cnt
        
        # 逆路線あれば
        if reverseID in self.lines:
            # 新路線の、逆路線ID
            self.lines[newID].reverseID = new_reverseID
            # 逆路線の、ID変更
            self.lines[new_reverseID] = self.lines.pop(reverseID)
            self.lines[new_reverseID].ID = new_reverseID
            # 逆路線の、逆路線ID
            self.lines[new_reverseID].reverseID = newID
            return 0, (reverseID, new_reverseID)

        return 0, (None, None)

        # !!!!!!!!!!! ここから

class Line:
    def __init__(self, ID, name, stations):
        self.ID = ID
        self.name = name
        self.stations = [x for x in stations]
        self.vehicle_cnt = 0
        self.reverseID = None

class Line_local(Line):
    def __init__(self, ID, name, stations):
        super(Line_local, self).__init__(ID, name, stations)
        self.ptn_cnt = 0

class Line_rapid(Line):
    def __init__(self, ID, name, stations, parentID, stop_stations):
        super(Line_rapid, self).__init__(ID, name, stations)
        self.ptn_cnt = None
        self.parentID = parentID
        self.stop_stations = [x for x in stop_stations]
        self.pass_stations = [x for i, x in enumerate(stations) \
                              if not x in stop_stations \
                                  and i >= stations.index(stop_stations[0]) \
                                  and i <= stations.index(stop_stations[-1])]
