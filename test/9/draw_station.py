# coding: utf-8
'''
STATION_CODE.txt から各駅をマップに表示
'''
import os
import folium
import sys
import argparse
#import numpy as np
from draw_route import make_map
sys.path.append('../common')
from common_character import enc_detect

def draw_stations(osm, data, color='red', radius=5):
    ''' 駅描画（circle marker） '''
    for l in data:
        scd, sid, snm, lat, lon = l

        #folium.Marker([lat, lon], popup=str(lat) + ',' + str(lon), tooltip='{0}({1},{2})'.format(snm, scd, sid), \
        #              icon = folium.Icon(color = 'red')).add_to(osm)

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            popup='{0},{1}\t({2},{3})'.format(scd, sid, str(lat), str(lon)),  #str(lat) + ',' + str(lon),
            tooltip=snm,  #'{0}({1},{2})'.format(snm, scd, sid),
            color=color,  #'#3186cc',
            fill=True,
            fill_color=color  #'#3186cc'
        ).add_to(osm)

    return osm

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infname', help='STATION_CODE.txt')
    parser.add_argument('outfname', help='html file.')
    parser.add_argument('-z', help='default 14', type=int, default=10)

    args = parser.parse_args()
    infname = args.infname
    outfname = args.outfname
    zoom = args.z  # ゆりかもめ 14, データ0 11, バス 15

    #colors = ['#008000', '#0000FF', '#FF0000', '#FF00FF', '#00FF00', '#000080', '#00FFFF', '#800080']
    #default_colors = [('green', 'green'), ('lime', 'lightgreen'), ('blue', 'blue'), ('aqua', 'lightblue'), \
    #                  ('red', 'red'), ('fuchsia', 'pink'), ('navy', 'darkblue'), ('purple', 'purple')]

    with open(infname, 'r', encoding=enc_detect(infname)) as inf:
        inlines = [l.strip().split('\t') for l in inf.readlines()]

    # カラム位置
    c_scd, c_sid, c_snm, c_lat, c_lon = 0, 1, 4, 6, 7

    # 緯度・経度はfloatに
    data = [[l[c_scd], l[c_sid], l[c_snm], float(l[c_lat]), float(l[c_lon])] for l in inlines[1:]]

    ll_data = [[r[3], r[4]] for r in data]
    osm = make_map(ll_data, zoom_start=zoom)

    osm = draw_stations(osm, data)

    osm.save(outfname)

'''
The color of the marker. You can use:
[‘red’, ‘blue’, ‘green’, ‘purple’, ‘orange’, ‘darkred’,
’lightred’, ‘beige’, ‘darkblue’, ‘darkgreen’, ‘cadetblue’,
darkpurple’, ‘white’, ‘pink’, ‘lightblue’, ‘lightgreen’,
gray’, ‘black’, ‘lightgray’]
'''
