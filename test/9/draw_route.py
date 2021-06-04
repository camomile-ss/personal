# coding: utf-8
'''
緯度経度データ.csv から各路線をマップに描画
'''
import os
import folium
import sys
import argparse
import numpy as np
import re
sys.path.append('../common')
from common_character import enc_detect

def get_colors():
    #confname = './conf/route.conf'
    confname = os.path.join(os.path.dirname(__file__), 'conf/route.conf')
    with open(confname, 'r', encoding='utf-8') as conff:
        conf_lines = [l.strip().split(',') for l in conff.readlines()]
        route_color = {l[0]: (l[1], l[2]) for l in conf_lines}  # 路線の色の辞書

    #colors = ['#008000', '#0000FF', '#FF0000', '#FF00FF', '#00FF00', '#000080', '#00FFFF', '#800080']
    default_colors = [('green', 'green'), ('lime', 'lightgreen'), ('blue', 'blue'), ('aqua', 'lightblue'), \
                      ('red', 'red'), ('fuchsia', 'pink'), ('navy', 'darkblue'), ('purple', 'purple')]

    return route_color, default_colors

def make_map(ll_data, zoom_start=14):
    ''' マップを定義 '''

    # 緯度・経度の中心
    ll_data = np.array(ll_data)
    ll_max = ll_data.max(axis=0)
    ll_min = ll_data.min(axis=0)
    ll_center = (ll_max + ll_min) / 2

    osm = folium.Map(location=list(ll_center), zoom_start=zoom_start)
    return osm

def draw_route(osm, data, color=('#03f', 'blue'), weight=3, marker=1):
    ''' ルート、マーカー描画 '''

    route_ll = [(r[0], r[1]) for r in data]
    folium.PolyLine(locations=route_ll, tooltip=data[0][3], color=color[0], weight=weight).add_to(osm)  # tooltip:路線名

    # 駅は路線の色、カーブは白
    if marker==1:
        for r in data:
            ic = 'lightgray' if r[2]=='-' else color[1]
            folium.Marker([r[0], r[1]], popup=str(r[0]) + ',' + str(r[1]), tooltip=r[2], \
                          icon = folium.Icon(color = ic)).add_to(osm)
    # 駅だけ
    elif marker==2:
        for r in data:
            if r[2] != '-':
                folium.Marker([r[0], r[1]], popup=str(r[0]) + ',' + str(r[1]), tooltip=r[2], \
                              icon = folium.Icon(color = color[1])).add_to(osm)

    return osm

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infname', help='curve_data.txt')
    parser.add_argument('outfname', help='html file.')
    parser.add_argument('outword', help='路線名grepするワード。全部出すなら all。')
    parser.add_argument('-z', help='default 14', type=int, default=14)
    parser.add_argument('-m', help='marker. 0: off, 1: on, 2(default): only station.',
                        type=int, choices=[0, 1, 2], default=2)
    parser.add_argument('-b', help='draw both direction or not. 0: only _0, 1(default): both.',
                        type=int, choices=[0, 1], default=1)
    parser.add_argument('-s', help='input file type. c(default): csv, t: tsv.',
                        choices=['c', 't'], default='c')

    args = parser.parse_args()
    infname = args.infname
    outfname = args.outfname
    outword = args.outword  # ex) 海01 全部だしたいときは all（緯度経度抜けてる行があるとエラーになる!!!）
    zoom = args.z  # ゆりかもめ 14, データ0 11, バス 15
    mk = args.m  # マーカー描画するかどうか 0: off, 1: on, 2: 駅だけ
    both = args.b  # 0: _0 だけ, 1: _0, _1 両方
    if args.s == 'c':
        sep = ','
    elif args.s == 't':
        sep = '\t'

    route_color, default_colors = get_colors()

    #with open(infname, 'r', encoding='utf-8') as inf:
    with open(infname, 'r', encoding=enc_detect(infname)) as inf:
        inlines = [l.strip().split(sep) for l in inf.readlines()]

    # 編集中によく改行入ってしまうのでチェック
    for i, l in enumerate(inlines):
        if len(l) < 4:
            print('[err] kaigyo ari. line:', i, ', ', l, file=sys.stderr)
            sys.exit()

    # allでなかったらoutword をふくむ路線のデータに絞る
    if outword != 'all':
        ptnword = outword.replace('[', '\[')
        ptnword = ptnword.replace(']', '\]')
        ptn = re.compile(ptnword)
        inlines = [l for l in inlines if ptn.search(l[3])]

    # 緯度・経度はfloatに
    inlines = [[float(l[0]), float(l[1]), l[2], l[3]] for l in inlines]

    ll_data = [[r[0], r[1]] for r in inlines]
    osm = make_map(ll_data, zoom_start=zoom)

    route_names = [l[3] for l in inlines]  # columns[3]: 路線名
    route_names = sorted(set(route_names), key=route_names.index)  # 重複削除。順番は維持。

    i = 0
    for rn in route_names:
        if both or (not both and rn[-2:] == '_0'):
            data = [l for l in inlines if l[3]==rn]

            # 色
            if rn in route_color:
                rc = route_color[rn]  # 路線独自色
            else:
                rc = default_colors[i % 8]  # 独自色指定ない場合はdefault_color順番に
                i += 1

            osm = draw_route(osm, data, rc, marker=mk)

    osm.save(outfname)

'''
The color of the marker. You can use:
[‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’,
darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’,
gray’, ‘black’, ‘lightgray’]
'''
