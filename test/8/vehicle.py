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
             
             95: err 路線にない駅が途中にある
             96: err 路線にある駅がひとつしかない
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
                flg = 95
                remain_stations = [x for x in remain_stations if x in line_stations]
            else:
                # エラーでない -> 外側のみng駅あり
                flg = 7

        # 残り駅がひとつしかない
        if len(remain_stations) == 1:
            return 96

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

        if self.pass_stations:
            flg = 8

        return flg

    def set_lineID(self, lineID):

        if lineID in self.lineIDs:
            return -1
        self.lineIDs.append(lineID)
        return 0
        