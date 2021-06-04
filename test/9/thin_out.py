# coding: utf-8
'''
緯度経度データの間引き、補完
・前後点を結んだ直線との距離が一定値未満の点を消す
・点間距離が一定値以上だったら、距離が一定値以下になるように等分する <- 未実装
'''

import sys
import argparse
import numpy as np
import csv
sys.path.append('../common')
from common_math import dist_p_to_line2p


def approx_coord(p):
    '''
    北緯・東経 -> 距離換算の近似座標に変換
    p      : [緯度, 経度]
    return : [x, y] (単位 m, 原点は仮) 
    '''    
    R = 6.378e6  # 地球の半径
    ap_lat = np.pi * 35 / 180  # ここらへんはだいたい緯度35度
    
    long = np.pi * p[1] / 180
    lat = np.pi * p[0] / 180
    
    x = long * R * np.cos(ap_lat) 
    y = lat * R

    return np.array([x, y])


def calc_d(plist, i):
    '''
    入力: 緯度経度リスト, 対象点pのインデックス
    出力: pと前後点を結ぶ直線の距離
          （pが最初/最後の場合は 16777215）
    '''
    if i <= 0 or i >= len(plist)-1:
        return 16777215
    
    p = approx_coord(plist[i])  # check点
    p1 = approx_coord(plist[i-1])  # 前点
    p2 = approx_coord(plist[i+1])  # 後点

    return dist_p_to_line2p(p, p1 ,p2)

    
def thin_out(s2s_data, dist):
    ''' 駅間データ（駅-駅）の間引き '''

    # 前後点を結んだ直線との距離、のリスト
    d = [calc_d([x[:2] for x in s2s_data], i) for i in range(len(s2s_data))]

    # 中間点があって、dの最小値がdist未満の間、削減処理
    while len(d) > 2 and min(d) < dist:

        # d が最小の点を消す
        i_del = d.index(min(d))
        d.remove(min(d))
        s2s_data.pop(i_del)

        # 消した点の前後の d を計算しなおす
        if i_del > 1:
            d[i_del-1] = calc_d([x[:2] for x in s2s_data], i_del-1)
        if i_del < len(d)-1:
            d[i_del] = calc_d([x[:2] for x in s2s_data], i_del)

    return s2s_data


def thin_out_1route(rdata, dist):
    '''
    1路線の間引き
    return: 間引き後の路線データ、間引いた数
    '''

    # 駅間リスト作成
    stations = [(x[2], i) for i, x in enumerate(rdata) if x[2]!='-']  # 中間点除いて(駅名, index)のリスト    
    sta2sta_list = [(stations[n], stations[n+1]) for n in range(len(stations) - 1)]

    # 各"駅間"ごとに
    rdata_out = []
    cnt_del = 0
    for i, s2s in enumerate(sta2sta_list):

        # 間引き
        s2s_data = rdata[s2s[0][1]: s2s[1][1]+1]  # 駅間データ
        n_b = len(s2s_data)
        s2s_data = thin_out(s2s_data, dist)  # 間引き
        if len(s2s_data)!=n_b:
            cnt_del += n_b - len(s2s_data)
            print(s2s[0][0], '-', s2s[1][0], ': mabiki:', len(s2s_data)-n_b)  # 間引き件数print

        # 間引き後データをつなげる
        if i == len(sta2sta_list)-1:
            rdata_out.extend(s2s_data)  # 最後の駅間は全部
        else:
            rdata_out.extend(s2s_data[:-1])  # 駅は重なるので、最後の駅間以外は、後の駅を除く

    return rdata_out, cnt_del


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()

    parser.add_argument('infname', help='input "curve_data.txt" file.')
    parser.add_argument('outfname', help='output "curve_data.txt" file.')
    parser.add_argument('-t', type=float, help='dist (m) threshold for thin out.')
    #parser.add_argument('-d', type=float, help='dist (km) threshold for equaly division.')

    args = parser.parse_args()
    
    infname = args.infname
    outfname = args.outfname
    thre_t = args.t
    #thre_d = args.d
    
    # データ読み込み
    with open(infname, 'r', encoding='utf-8') as inf:
        data = [x.strip().split('\t') for x in inf]

    data = [[float(x[0]), float(x[1])] + x[2:] for x in data]
    
    # 路線リスト
    routes = sorted(set([x[3] for x in data]), key=lambda x: [x[3] for x in data].index(x))
    
    # 路線ごとに処理
    outdata = []
    cnt_del = 0
    for r in routes:
        print('[route]', r)
        rdata = [x for x in data if x[3]==r]
        rdata, cd_1r = thin_out_1route(rdata, thre_t)
        outdata.extend(rdata) 
        cnt_del += cd_1r

    # 出力
    with open(outfname, 'w', encoding='utf-8') as outf:
        writer = csv.writer(outf, delimiter='\t', lineterminator='\n')
        for r in outdata:
            writer.writerow(r)

    print('[** total mabiki **]', cnt_del)
