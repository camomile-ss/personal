# coding: utf-8
'''
既取得緯度経度データから、他路線の同じ停留所間の緯度経度データを作成する。
'''
import csv
import sys

class bus_stop:
    ''' のりばを区別する用のクラス '''
    
    def __init__(self, stopfname):
        ''' のりば辞書作成 {(停留所名, 路線名): のりば名, .....} '''
        with open(stopfname, 'r', encoding='utf-8') as stf:
            stfreader = csv.reader(stf)
            self.stop_dic = {(l[0], l[1]): l[2] for l in stfreader}

    def get_stop(self, station, route):
        ''' のりば検索 '''
        if (station, route) in self.stop_dic:
            return self.stop_dic[(station, route)]
        else:
            return ''
    
def curve_dic_bus(llfn, bs):
    '''
    ・緯度経度取得済みの停留所辞書作成
    {停留所名: [(のりば名, 緯度, 経度), ...], .....}
    ・停留所間データ作成
    {((発停留所名, 発のりば名), (着停留所名, 着のりば名)): [(緯度, 経度), (緯度, 経度), (緯度, 経度), ...], ...}
    '''
    with open(llfn, 'r') as llf:
        llfreader = csv.reader(llf)
        data = [l for l in llfreader if l[0]!='-' and l[1]!='-']

    #ready_stations = [tuple(l[:-1] + [bs.get_stop(l[2], l[3])]) for l in data if l[2]!='-']
    ready_stations = {}
    curve_dic = {}
    for i, r in enumerate(data):
        lat, lon, station, route, *_ = r
        
        # 1行目
        if i == 0:
            # 停留所間データ -----------------#
            s_ss = (station, bs.get_stop(station, route))  # (発停留所, 発のりば)ストア
            ll_list = [(lat, lon)]  # 緯度経度、リストに追加

            # 取得済み辞書 -----------------#
            ready_stations[station] = [(s_ss[1], lat, lon, route)]
            continue

        # 2行目以降
        # 停留所間
        if station == '-':
            ll_list.append((lat, lon))  # 緯度経度、リストに追加
        # 停留所
        else:
            # 停留所間データ -----------------#
            ll_list.append((lat, lon))  # 緯度経度、リストに追加
            e_ss = (station, bs.get_stop(station, route))  # (着停留所, 着のりば)

            # 辞書に既存なら一致してるかチェック
            if (s_ss, e_ss) in curve_dic:  # 既存は書き換えない
                if ll_list != curve_dic[(s_ss, e_ss)]:
                    print('[warn] route not equal. llf line:', i, ', route:', route, ', s:', s_ss, ', e:', e_ss)
            else:
                curve_dic[(s_ss, e_ss)] = ll_list  # 辞書に追加（重複はとりま上書き）

            # クリア
            s_ss = e_ss  # (発停留所名, 発のりば) 入れ替え
            ll_list = [(lat, lon)]  # 発停留所の緯度経度

            # 取得済み辞書 -----------------#
            if station in ready_stations:
                ready_stations[station].append((e_ss[1], lat, lon, route))
            else:
                ready_stations[station] = [(e_ss[1], lat, lon, route)]

    return ready_stations, curve_dic

def make_route_bus(stations, routename, curve_dic, bs):
    '''
    1路線の(未完)緯度経度データ作成
    辞書にない部分は緯度、経度とも '-'
    [args] stations: (停留所名, のりば名)のリスト
    '''
    routedata = []
    for i, sta in enumerate(stations):

        ss = (sta, bs.get_stop(sta, routename))
        
        # 1行目
        if i == 0:
            s_ss = ss  # (発停留所名, のりば名)
            routedata.append(['-', '-', sta, routename])  # -, -, 停留所名, 路線名
            continue
        
        # 2行目以降
        # 「発停留所～いまみてる停留所」が停留所間辞書にある
        if (s_ss, ss) in curve_dic:
            ll_list = curve_dic[(s_ss, ss)]
            # 緯度経度データ編集
            #   最後の1行削除
            routedata = [d for d in routedata[:-1]]
            #   発停留所
            routedata.append(list(ll_list[0]) + [s_ss[0], routename])
            #   停留所間
            between = [[l[0], l[1], '-', routename] for l in ll_list[1:-1]]
            routedata.extend(between)
            #   着停留所
            routedata.append(list(ll_list[-1]) + [sta, routename])
        # 停留所間辞書にない
        else:
            routedata.append(['-', '-', sta, routename]) 

        s_ss = ss  # 発停留所おきかえ

    return routedata

if __name__ == '__main__':

    llfname = sys.argv[1]  # 緯度経度データ_201812xx.csv
    #rsfname = './wk/bus_wk/railstation_wk/railstation.txt'
    #rsfname = './wk/bus_wk/railstation_wk/railstation_1219追記.txt'
    rsfname = sys.argv[2]
    stopfname = './wk/bus_wk/stop.csv'
    #outfname = sys.argv[2]  #'./wk/bus_wk/緯度経度データ_incomp.csv'
    outfname = './wk/bus_wk/緯度経度データ_halfw.csv'
    curvefname = './wk/bus_wk/bus_curve_data.txt'

    # のりば区別用いんすたんす
    bs = bus_stop(stopfname)
    # 緯度経度取得済みの停留所のリスト、停留所間データの辞書
    ready_stations, curve_dic = curve_dic_bus(llfname, bs)

    # 停留所間データ書き出し
    with open(curvefname, 'w', encoding='utf-8') as cf:
        for k, v in curve_dic.items():
            cf.write('\t'.join(['\t'.join(e) for e in k]) + '\t' + '\t'.join(['\t'.join(e) for e in v]) + '\n')
        
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
        stations = [l[7] for l in inlines if l[1]==rn]  # その路線の停留所リスト        
        # 路線の緯度経度データ作成
        outdata.extend(make_route_bus(stations, rn, curve_dic, bs))

    with open(outfname, 'w', encoding='utf-8') as outf:
        outfwriter = csv.writer(outf, lineterminator='\n')

        # 出力
        for l in outdata:
            outfwriter.writerow(l)
            # outdataの緯度経度ない停留所がready_stationsにあったらprint
            if l[0]=='-' and l[1]=='-' and l[2] in ready_stations:
                print('[*既存*]', l[3], l[2], ', 緯度経度:', ready_stations[l[2]])
                
                
