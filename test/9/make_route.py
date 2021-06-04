# coding: utf-8
'''
railstation.txtをもとに、
・STATION_CODE.txtから駅の緯度経度、
・curve_data.txtから中間点の緯度経度
を取得してOSM描画用の緯度経度データをつくる。
（路線名は、"・"～"_"までの情報を除いた路線名で緯度経度データを作成する。
  短縮した路線名が同じものが複数セットあるときは、駅名が同じかチェックする。）
'''
import csv
import sys
import re

def get_sta_dic():
    ''' 駅のデータ ** STATION_CODE.txt から ** '''
    stafname = '../../data/20181108_緯度経度データの作成と確認/データ/参考/STATION_CODE.txt'
    sta_dic = {}
    with open(stafname, 'r', encoding='cp932') as staf:
        stafreader = csv.reader(staf)
        for r in stafreader:
            # station name でやっても stationID でやってもヒットしないものがあるので、keyはタプルにして両方入れる
            sta_dic[(r[0], r[3])] = (r[5], r[6])  # key: (stationID, station name), value: [latitude, longitude]
    return sta_dic

def get_curve_dic():
    ''' 駅間カーブデータ '''
    curvfname = '../../data/20181108_緯度経度データの作成と確認/データ/参考/curve_data.txt'
    curve_dic = {}
    with open(curvfname, 'r') as curvf:
        curvfreader = csv.reader(curvf)
        for i, r in enumerate(curvfreader):
            ll_list = [(r[j], r[j+1]) for j in range(2, len(r)-1, 2)]  # (緯度, 経度) のリスト
            ll_list = sorted(set(ll_list), key=ll_list.index)  # 同じ値があるので重複削除
            curve_dic[(r[0], r[1])] = ll_list[1:-1]  # 最初と最後が前後と重複しているので削除
    return curve_dic

class short_route_name:
    '''
    路線名短縮・重複削除用クラス
    '''
    def __init__(self):
        self.sr_dic = {}
        self.ptn = re.compile(r'^(.+)・.+(_[01])$')

    def chk(self, routename, stations):
        '''
        路線名を短縮、chk_dicに既存かチェック
        短縮路線名と、既存フラグを返す。
        '''
        mob = self.ptn.match(routename)
        # 路線名短縮対象
        if mob:
            routename_s = mob.group(1) + mob.group(2)  # 短縮（・から_の手前まで除く）
            print(routename + ' -> ' + routename_s)
        # 路線名そのまま
        else:
            routename_s = routename
            print(routename_s)

        # chk_dicに既存
        if routename_s in self.sr_dic:
            
            # 駅名あってるかチェック 
            if stations == self.sr_dic[routename_s]:
                return routename_s, True  # フラグは既存
            else:
                print('[* warn *] ' + routename + ' ekimei ne ' + routename_s, file=sys.stderr)                             
                return routename_s, False  # 駅名あってなかったら、フラグはoffにして出力させる。たぶん手で直すので。
        # chk_dicに追加
        else:
            self.sr_dic[routename_s] = stations
            return routename_s, False

def make_outdata(data, routename, sta_dic, curve_dic, curve=False):
    '''
    1路線の緯度経度データ作成
    curve=Trueなら中間点データも作成
    '''
        
    sta_id = ''
    outdata = []

    for j, r in enumerate(data):
        # curve=Trueで最初の行以外なら、前の行の駅idをストア
        if curve and j != 0:
            prev_sta_id = sta_id

        # 使う項目            
        sta_id = r[5]
        sta_name = r[7]
        
        # curve=Trueで最初の行以外なら、中間点データ出力
        if curve and j != 0:
            # 駅間データが[前の駅->今の駅]
            if (prev_sta_id, sta_id) in curve_dic.keys():
                for ll_data in curve_dic[(prev_sta_id, sta_id)]:
                    outdata.append(list(ll_data) + ['-', routename])                            
            # 駅間データが[今の駅->前の駅]
            elif (sta_id, prev_sta_id) in curve_dic.keys():
                # 緯度経度データ逆に
                rev_curve_data = curve_dic[(sta_id, prev_sta_id)][::-1]
                for ll_data in rev_curve_data:
                    outdata.append(list(ll_data) + ['-', routename])                            
            # 駅間データがない
            else:
                outdata.append(['(駅間なし)', '-', '-', routename])                        

        # 駅のデータ出力
        # stationID で sta_dic からさがす
        if sta_id in [k[0] for k in sta_dic.keys()]:
            sta_dic_ = {k[0]: v for k, v in sta_dic.items()}  # stationID だけがキーの一時辞書
            outdata.append(list(sta_dic_[sta_id]) + [sta_name, routename])
        # stationID がなければ station name でさがす
        elif sta_name in [k[1] for k in sta_dic.keys()]:
            sta_dic_ = {k[1]: v for k, v in sta_dic.items()}  # station name だけがキーの一時辞書
            outdata.append(list(sta_dic_[sta_name]) + [sta_name, routename])
        # 駅のデータなし
        else:
            print(sta_id + ', ' + sta_name + ' not in sta_dic', file=sys.stderr)
            outdata.append(['-'] * 3 + [sta_name, routename])
    
    return outdata


if __name__ == '__main__':

    infname = sys.argv[1]  # railstation.txt
    outdir = sys.argv[2]  # outfname = outdir/緯度経度データ.csv

    other = sys.argv[3:]
    curve = int(other[0]) if len(other) else 0  # 中間点書くかどうか。書くなら1とかTrueになるやつに。
    
    outfname = outdir + '/緯度経度データ.csv'
    
    sta_dic = get_sta_dic()  # 駅のデータ
    curve_dic = get_curve_dic()  # 駅間カーブデータ

    # railstation.txtファイル読み込み
    with open(infname, 'r', encoding='utf-8') as inf:
        inlines = inf.readlines()
        inlines = [l.strip().split('\t') for l in inlines]
    
    # 路線名リスト（路線名だけだと同じものがあるので、路線IDとのタプルにする）
    route_names = [(l[0], l[1]) for l in inlines]  # columns[0]: 路線ID, columns[1]: 路線名
    route_names = sorted(set(route_names), key=route_names.index)  # 重複削除。順番は維持。

    # 各路線ごとにroute作成する
    srn = short_route_name()  # 路線名短縮・重複削除用obj作成

    with open(outfname, 'w', encoding='utf-8') as outf:
        outfwriter = csv.writer(outf, lineterminator='\n')
    
        for rid, rn in route_names:
            data = [l for l in inlines if l[0]==rid and l[1]==rn]  # その路線のデータ
    
            # 路線名短縮、srn.chk_dicに既存かチェック    
            rn_s, flg = srn.chk(rn, [c[7] for c in data])  # column[7] : 駅名
    
            # 既存でなければ
            if not flg:
                # 路線作成
                outdata = make_outdata(data, rn_s, sta_dic, curve_dic, curve)
                
                # 出力
                for l in outdata:
                    outfwriter.writerow(l)
