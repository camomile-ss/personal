#!/usr/bin/python
# coding: utf-8

class MatchLine:
    '''
    列車の駅(v_stations)が、路線駅(rail_statilns)にマッチするかチェック
    [args] v_stations, rail_stations : リスト（駅名、駅CD、駅ID いずれも可。ただし両者で揃える。）
    [var]
        match_stations: 路線駅とマッチする列車駅（flg:0 のときv_stationと一致。flg:1 のとき、v_stationより短い） 
        middle_start: 路線の途中が列車の始発駅の場合の始発駅。
        middle_end: 路線の途中が列車の終着駅の場合の終着駅。
        pass_stations: 列車が通過する駅のリスト
        outside_delete_stations: 路線が列車より短いため削除した列車の駅リスト
            # 列車に路線の端駅が無い場合は削除しない。errとする    
        ng_stations: err の場合の、路線にない列車駅のリスト（outside_delete_stations を除く）

    ## 路線のループ（同じ駅を2度通る路線）には対応していない
    '''

    def __init__(self, v_stations, rail_stations):

        self.v_stations, self.rail_stations = None, None
        self.match_stations = None
        self.middle_start, self.middle_end = None, None
        self.pass_stations, self.outside_delete_stations, self.ng_stations = None, None, None

        self.v_stations = [x for x in v_stations]
        self.rail_stations = [x for x in rail_stations]

    def chk(self):
        '''
        [return]
        flg: 0: OK
             1: 路線が列車より短いため路線にない端駅を削除
             8: 通過駅あり
             9: err 路線にない駅が途中にある
             99: err v_stations が空
            # 1 かつ 8 の場合は 8 (-> 8 は準エラーで最終的に解消するはずなので)
        '''
        # v_stations 空なら終了
        if not self.v_stations:
            return 99

        # v_station に、隣接する重複があれば削除
        self.v_stations = [self.v_stations[0]] + [self.v_stations[i] \
                           for i in range(1, len(self.v_stations)) \
                           if self.v_stations[i] != self.v_stations[i-1]]

        flg = None

        v_stas = [x for x in self.v_stations]

        # ng駅あるかどうかチェック
        if any(not x in self.rail_stations for x in v_stas):
            
            # 先頭ng駅を削除
            pop_stations = []
            while not v_stas[0] in self.rail_stations:
                pop_stations.append(v_stas.pop(0))

            # 削除後の先頭駅が路線始発駅でなければエラー
            if v_stas[0] == self.rail_stations[0]:

                # 末尾ng駅を削除
                while not v_stas[-1] in self.rail_stations:
                    pop_stations.append(v_stas.pop(-1))

                # 削除後の末尾駅が路線終着駅でなければエラー
                if v_stas[-1] == self.rail_stations[-1]:

                    # 途中にng駅が残っていたらエラー
                    if any(not x in self.rail_stations for x in v_stas):
                        flg = 9
                else:
                    flg = 9
            else:
                flg = 9

            # エラー
            if flg:
                self.ng_stations = [x for x in self.v_stations if not x in self.rail_stations]
                return flg

            # OK。ng駅両端のみ。削除。
            self.outside_delete_stations = [x for x in sorted(pop_stations, \
                                            key=lambda x: self.v_stations.index(x))]
            flg = 1

        self.match_stations = [x for x in v_stas]

        # 通過駅あるかチェック

        # 路線の、列車始発〜終着の部分
        start_idx = self.rail_stations.index(self.match_stations[0])
        end_idx = self.rail_stations.index(self.match_stations[-1])
        rail_stations_part = self.rail_stations[start_idx: end_idx+1]

        # 通過駅リストアップ
        self.pass_stations = [x for x in rail_stations_part if not x in self.match_stations]

        if self.pass_stations:
            flg = 8

        return flg

class SplitLine:

    def __init__(self):
        self.lines = []
        self.v_stations = None
        self.v_stations_split = []

    def add_line(self, linename, line_stations):
        self.lines.append({'name': linename, 'stations': line_stations})

    def split(self, v_stations):

        # v_stations 空なら終了
        if not v_stations:
            return 99

        # v_station に、隣接する重複があれば削除
        v_stations = [v_stations[0]] + [v_stations[i] for i in range(1, len(v_stations)) \
                           if v_stations[i] != v_stations[i-1]]

        self.v_stations = [x for x in v_stations]
        self.v_stations_split = []

        pre_line = None
        while True:
            flg = False
            for l in self.lines:
                l_name, l_stas = l['name'], l['stations']
                if l_name != pre_line and v_stations[0] in l_stas \
                   and len(l_stas) > l_stas.index(v_stations[0]) + 1 \
                   and l_stas[l_stas.index(v_stations[0]) + 1] == v_stations[1]:
                    flg = True
                    di = l_stas.index(v_stations[0])
                    split_stas = []
                    for i in range(len(v_stations)):
                        if i + di >= len(l_stas) or v_stations[0] != l_stas[i + di]:
                            break
                        split_stas.append(v_stations.pop(0))
                    self.v_stations_split.append((l_name, split_stas))
                    if len(v_stations):
                        v_stations = [split_stas[-1]] + v_stations
                        pre_line = l_name
                    break
            if not flg or len(v_stations) == 0:
                break

        if not flg:
            self.v_stations_split = []
            return 9

        return 0

if __name__ == '__main__':

    sl = SplitLine()
    sl.add_line('路線1', ['品川', '東京', '上野', '北千住'])
    sl.add_line('路線2', ['上野', '大宮'])
    sl.add_line('路線3', ['土呂', '大宮', '高崎', '上越', 'スキー場前'])
    sl.add_line('路線4', ['宇都宮', '上越', '新潟', '越後'])
    sl.add_line('路線5', ['大宮', '指扇', '東大宮', '上越'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越', '上越', '新潟'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越', '上越', '新潟', 'スキー場前'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越'])
    code = sl.split(['土呂', '大宮', '指扇', '東大宮', '上越', 'スキー場前'])
    #code = sl.split([])
    print(code)
    print(sl.v_stations)
    print(sl.v_stations_split)

    """
    #v_stations = ['東京', '上野', '上野', '上野', '大宮', '大宮', '高崎']
    #v_stations = ['小田原', '熱海', '熱海', '品川', '品川', '東京', '東京', '上野', '上野', '上野', '大宮', '大宮', '高崎']
    v_stations = ['小田原', '熱海', '熱海', '品川', '品川', '東京', '東京', '高崎', '上越', '上越', '新潟']
    rail_stations = ['東京', '上野', '大宮', '高崎']
    #v_stations = []
    #rail_stations = ['東京', '上野', '大宮', '高崎']



    ml = MatchLine(v_stations, rail_stations)
    flg = ml.chk()
    print(flg)
    print(ml.match_stations)
    print(ml.outside_delete_stations)
    print(ml.ng_stations)
    print(ml.pass_stations)
    """