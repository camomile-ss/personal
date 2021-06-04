# coding: utf-8
'''
緯度経度データ.csv から各路線をマップに描画
データ0 路線名整備前用
（小泉線の支線が分かれるように工夫したが、丸ノ内線等も支線があるため路線名を変えることになったので、暫定版。）
'''

import folium
import sys
import numpy as np
sys.path.append('../common')
from common_character import enc_detect

def make_map(data, zoom_start=14):
    ''' マップを定義 '''
    
    # 緯度・経度の中心
    ll_data = np.array([[r[0], r[1]] for r in data])
    ll_max = ll_data.max(axis=0)
    ll_min = ll_data.min(axis=0)
    ll_center = (ll_max + ll_min) / 2

    osm = folium.Map(location=list(ll_center), zoom_start=zoom_start)
    return osm

def draw_route(osm, data, color='#03f', weight=3, marker=1):
    ''' ルート、マーカー描画 '''

    route_ll = [(r[0], r[1]) for r in data]
    folium.PolyLine(locations=route_ll, tooltip=data[0][3], color=color, weight=weight).add_to(osm)  # tooltip:路線名
    
    if marker:
        for r in data:
            ic = 'red' if r[2]=='-' else 'blue'
            folium.Marker([r[0], r[1]], popup=str(r[0]) + ',' + str(r[1]), tooltip=r[2], icon = folium.Icon(color = ic)).add_to(osm)
    
    return osm

if __name__ == '__main__':
    
    infname = sys.argv[1]
    outfname = sys.argv[2]
    zoom = int(sys.argv[3])  # ゆりかもめ 14, データ0 11
    mk = int(sys.argv[4])  # マーカー描画するかどうか 0: off, 1: on
    
    #colors = ['#008000', '#0000FF', '#FF0000', '#FF00FF', '#00FF00', '#000080', '#00FFFF', '#800080']
    colors = ['green', 'blue', 'red', 'fuchsia', 'lime', 'navy', 'aqua', 'purple']
    #with open(infname, 'r', encoding='utf-8') as inf:
    with open(infname, 'r', encoding=enc_detect(infname)) as inf:
        inlines = [l.strip().split(',') for l in inf.readlines()]
    inlines = [[float(l[0]), float(l[1]), l[2], l[3]] for l in inlines] 

    osm = make_map(inlines, zoom_start=zoom)

    data = []
    prev_rn = ''
    first = 1
    i = 0  # 色分け用カウンタ
    for l in inlines:
        # 最初の行
        if first == 1:
            prev_rn = l[3]
            data = [l]
            first = 0
        # 路線名変わり目で描画
        elif l[3] != prev_rn:
            if len(data) and prev_rn[-2:]=='_0':  # _0路線だけ
                osm = draw_route(osm, data, colors[i % 8], marker=mk)
                i += 1
            # データリセット
            prev_rn = l[3]
            data = [l]
        else:
            data.append(l)

    # 最後の路線描画
    if len(data) and prev_rn[-2:]=='_0':  # _0路線だけ
        osm = draw_route(osm, data, colors[i % 8], marker=mk)
        
        
    '''
    # 同じ路線名で枝線が別のところにある（小泉線）のでこれだとだめ
    route_names = [l[3] for l in inlines]  # columns[3]: 路線名
    route_names = sorted(set(route_names), key=route_names.index)  # 重複削除。順番は維持。

    osm = make_map(inlines, zoom_start=15)
    i = 0
    for rn in route_names:
        if rn[-2:] == '_0':
            data = [l for l in inlines if l[3]==rn]
            osm = draw_route(osm, data, colors[i % 8])
            i += 1
    '''

    osm.save(outfname)
    