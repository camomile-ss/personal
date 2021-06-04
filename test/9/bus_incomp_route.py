# coding: utf-8
'''
既取得緯度経度データから、他路線の不完全緯度経度データを作成する。
作業用。
'''
import csv
import sys

def curve_dic_bus(llfn):
    '''
    停留所間データ作成
    {(発停留所名, 着停留所名): [(緯度, 経度), (緯度, 経度), (緯度, 経度), ...], ...}
    '''
    curve_dic = {}
    with open(llfn, 'r') as llf:
        llfreader = csv.reader(llf)
        for i, r in enumerate(llfreader):
            # 1行目
            if i == 0:
                s_sta = r[2]  # 発停留所ストア
                ll_list = [(r[0], r[1])]  # 緯度経度、リストに追加
                continue
            
            # 2行目以降
            # 停留所間
            if r[2]=='-':
                ll_list.append((r[0], r[1]))  # 緯度経度、リストに追加
            # 停留所
            else:
                ll_list.append((r[0], r[1]))  # 緯度経度、リストに追加
                curve_dic[(s_sta, r[2])] = ll_list  # 辞書に追加（重複はとりま上書き）
                # クリア
                s_sta = r[2]  # 発停留所名
                ll_list = [(r[0], r[1])]  # 発停留所の緯度経度

    return curve_dic

def make_route_bus(stations, routename, curve_dic):
    '''
    1路線の(未完)緯度経度データ作成
    辞書にない部分は緯度、経度とも '-'
    '''
    routedata = []
    for i, sta in enumerate(stations):

        # 1行目
        if i == 0:
            s_sta = sta  # 発停留所
            routedata.append(['-', '-', sta, routename])  # -, -, 停留所名, 路線名
            continue
        
        # 2行目以降
        # 「発停留所～いまみてる停留所」が停留所間辞書にある
        if (s_sta, sta) in curve_dic:
            ll_list = curve_dic[(s_sta, sta)]
            # 緯度経度データ編集
            #   最後の1行削除
            routedata = [d for d in routedata[:-1]]
            #   発停留所
            routedata.append(list(ll_list[0]) + [s_sta, routename])
            #   停留所間
            between = [[l[0], l[1], '-', routename] for l in ll_list[1:-1]]
            routedata.extend(between)
            #   着停留所
            routedata.append(list(ll_list[-1]) + [sta, routename])
        # 停留所間辞書にない
        else:
            routedata.append(['-', '-', sta, routename]) 

        s_sta = sta  # 発停留所おきかえ

    return routedata

if __name__ == '__main__':

    llfname = sys.argv[1]  # 緯度経度データ_201812xx.csv
    rsfname = './wk/bus_wk/railstation_wk/railstation.txt'
    outfname = './wk/bus_wk/緯度経度データ_incomp.csv'

    curve_dic = curve_dic_bus(llfname)  # 停留所間データの辞書

    # railstation.txtファイル読み込み
    with open(rsfname, 'r', encoding='utf-8') as inf:
        inlines = inf.readlines()
        inlines = [l.strip().split('\t') for l in inlines]
    
    # 路線名リスト
    route_names = [l[1] for l in inlines]  # columns[1]: 路線名
    route_names = sorted(set(route_names), key=route_names.index)  # 重複削除。順番は維持。

    # 各路線ごとにroute作成する
    outdata = []
    for rn in route_names:
        stations = [l[7] for l in inlines if l[1]==rn]  # その路線の停留所名リスト
        
        # 路線の緯度経度データ作成
        outdata.extend(make_route_bus(stations, rn, curve_dic))
            
    with open(outfname, 'w', encoding='utf-8') as outf:
        outfwriter = csv.writer(outf, lineterminator='\n')

        # 出力
        for l in outdata:
            outfwriter.writerow(l)
