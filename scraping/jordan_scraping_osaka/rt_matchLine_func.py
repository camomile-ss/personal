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
        outside_ng_stations: 路線が列車より短いため削除した列車の駅リスト
            # 列車に路線の端駅が無い場合はerrとする。削除はする。    
        mid_ng_stations: err の場合の、路線にない列車駅のリスト（outside_ng_stations を除く）

    ## 路線のループ（同じ駅を2度通る路線）には対応していない
    '''

    def __init__(self, rail_stations):

        self.v_stations = None
        self.rail_stations = [x for x in rail_stations]
        self.rail_stations_stop = []
        self.match_stations = None
        self.middle_start, self.middle_end = None, None
        self.pass_stations, self.outside_ng_stations, self.mid_ng_stations = None, None, None

    def chk(self, v_stations):
        '''
        [return]
        flg: 0: OK
             7: 路線にない駅が外側にある（直通かも）
             8: 通過駅あり
             96: err 路線にない駅が途中にある
             97: err 路線と駅順が違う
             98: err 全ての駅が路線にない
             99: err v_stations が空
            # (数字の大きいほうのエラーflg返る)
        '''
        # v_stations 空なら終了
        if not v_stations:
            return 99

        # v_station に、隣接する重複があれば削除
        v_stations = [v_stations[0]] + [v_stations[i] for i in range(1, len(v_stations)) \
                           if v_stations[i] != v_stations[i-1]]

        self.v_stations = [x for x in v_stations]

        flg = 0

        remain_stations = [x for x in self.v_stations]

        # ng駅あるかどうかチェック
        if any(not x in self.rail_stations for x in remain_stations):
            
            # 先頭ng駅を削除 --------------------------------------##
            pop_stations = []
            while remain_stations and not remain_stations[0] in self.rail_stations:
                pop_stations.append(remain_stations.pop(0))

            # 駅が残っていなければエラー -> 終了
            if not remain_stations:
                self.mid_ng_stations = [x for x in pop_stations]
                return 98

            # 削除後の先頭駅が路線始発駅でなければエラー
            #if remain_stations[0] != self.rail_stations[0]:
            #    flg = 9

            # 末尾ng駅を削除 --------------------------------------##
            while remain_stations and not remain_stations[-1] in self.rail_stations:
                pop_stations.append(remain_stations.pop(-1))

            # 削除後の末尾駅が路線終着駅でなければエラー
            #if remain_stations[-1] != self.rail_stations[-1]:
            #    flg = 9

            # 外側ng駅
            self.outside_ng_stations = [x for x in sorted(pop_stations, \
                                            key=lambda x: self.v_stations.index(x))]
            # 途中ng駅 --------------------------------------------## 
            self.mid_ng_stations = [x for x in remain_stations if not x in self.rail_stations]
            # あったらエラー
            if self.mid_ng_stations:
                flg = 96
                remain_stations = [x for x in remain_stations if x in self.rail_stations]
            else:
                # エラーでない -> 外側のみng駅あり
                flg = 7

        # 路線とマッチする部分
        self.match_stations = [x for x in remain_stations]

        # 路線の途中始発・終着
        if self.match_stations[0] != self.rail_stations[0]:
            self.middle_start = self.match_stations[0]
        if self.match_stations[-1] != self.rail_stations[-1]:
            self.middle_end = self.match_stations[-1]

        # 順番チェック
        orders = [self.rail_stations.index(x) for x in self.match_stations]
        # 駅順が違う
        if any(orders[i] >= orders[i+1] for i in range(len(orders) - 1)):
            flg = 97

        # エラーは終了(flg = 96, 97)
        if flg >= 90:
            return flg

        # 通過駅あるかチェック ---------------------------------------##

        # 路線の、列車始発〜終着の部分
        start_idx = self.rail_stations.index(self.match_stations[0])
        end_idx = self.rail_stations.index(self.match_stations[-1])
        rail_stations_part = self.rail_stations[start_idx: end_idx+1]

        # 通過駅リストアップ
        self.pass_stations = [x for x in rail_stations_part if not x in self.match_stations]

        # 路線の停車・通過
        for rs in self.rail_stations:
            # 停車
            if rs in self.match_stations:
                self.rail_stations_stop.append(rs)
            # 通過
            elif rs in self.pass_stations:
                self.rail_stations_stop.append('(-{}-)'.format(rs))
            else:
                self.rail_stations_stop.append('-')

        if self.pass_stations:
            flg = 8

        return flg

class SplitLine:
    '''
    複数路線直通の列車経路を路線に分割
    [var]
        v_stations_split : [(路線名, [駅名, ...]), ... ]
    '''

    def __init__(self):
        self.lines = []
        self.v_stations = None
        self.v_stations_split = []
        self.err_stations = None  # 見つからない駅

    def add_line(self, linename, line_stations):
        self.lines.append({'name': linename, 'stations': line_stations})

    def split(self, v_stations):

        # v_stations 空なら終了
        if not v_stations:
            return 99

        # v_station に、隣接する重複があれば削除
        v_stations = [v_stations[0]] + [v_stations[i] \
                      for i in range(1, len(v_stations)) \
                      if v_stations[i] != v_stations[i-1]]

        self.v_stations = [x for x in v_stations]
        self.v_stations_split = []

        remain_stations = [x for x in self.v_stations]
        pre_line = None

        flg = 0
        while True:
            candidate = {}
            # 列車の先頭駅から、マッチする路線を探す
            for l in self.lines:
                l_name, l_stations = l['name'], l['stations']
                if l_name != pre_line and remain_stations[0] in l_stations:
                    # マッチ部分
                    match = [r for r, l \
                             in zip(remain_stations, \
                                    l_stations[l_stations.index(remain_stations[0]): ]) \
                             if r == l]
                    # 2駅以上マッチ
                    if len(match) >= 2:
                        # マッチ部分が長い方を候補に
                        if not candidate or (len(candidate['stations']) < len(match)):
                            candidate = {'name': l_name, 'stations': match}

            # 候補あり
            if candidate:
                # 列車分割リストに追加
                self.v_stations_split.append((candidate['name'], candidate['stations']))
                # 残り駅から末尾駅除いて削除
                remain_stations = remain_stations[len(candidate['stations']) - 1: ]
                # 残り1駅しかなければ終了
                if len(remain_stations) <= 1:
                    flg = 0
                    break
            # 候補がみつからない -> エラーとして終了
            else:
                self.err_stations = remain_stations[:2]  # 見つからなかった2駅の組み合わせをセット
                self.v_stations_split = []
                flg = 9
                break

        return flg

if __name__ == '__main__':

    sl = SplitLine()
    sl.add_line('路線1', ['品川', '東京', '上野', '北千住'])
    sl.add_line('路線2', ['上野', '大宮'])
    sl.add_line('路線3', ['土呂', '大宮', '高崎', '上越', 'スキー場前'])
    sl.add_line('路線4', ['宇都宮', '上越', '新潟', '越後'])
    sl.add_line('路線5', ['大宮', '指扇', '東大宮', '上越'])
    sl.add_line('路線6', ['どこか', '土呂', '大宮', '指扇', 'どこか2'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越', '上越', '新潟'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越', '上越', '新潟', 'スキー場前'])
    #code = sl.split(['東京', '上野', '大宮', '高崎', '上越'])
    code = sl.split(['土呂', '大宮', '指扇', '東大宮', '上越', 'スキー場前'])
    #code = sl.split(['名古屋', '土呂', '大宮', '指扇', '東大宮', '上越', 'スキー場前'])
    #code = sl.split([])
    print(code)
    print(sl.v_stations)
    print(sl.v_stations_split)
    print(sl.err_stations)
    """
    #v_stations = ['東京', '上野', '上野', '上野', '大宮', '大宮', '高崎']
    #v_stations = ['小田原', '熱海', '熱海', '品川', '品川', '東京', '東京', '上野', '上野', '上野', '大宮', '大宮', '高崎']
    #v_stations = ['小田原', '熱海', '熱海', '品川', '品川', '東京', '東京', '高崎', '上越', '上越', '新潟']
    v_stations = ['小田原', '熱海', '熱海', '品川', '品川', '東京', '東京', '大宮', '上野', '高崎', '上越', '上越', '新潟']
    rail_stations = ['東京', '上野', '大宮', '高崎']
    #v_stations = []
    #rail_stations = ['東京', '上野', '大宮', '高崎']

    ml = MatchLine(rail_stations)
    flg = ml.chk(v_stations)
    print(flg)
    print('[match]', ml.match_stations)
    print('[outside ng]', ml.outside_ng_stations)
    print('[mid ng]', ml.mid_ng_stations)
    print('[pass]', ml.pass_stations)
    """