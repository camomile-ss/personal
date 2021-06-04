#!/usr/bin/python

import argparse
import os
import sys
sys.path.append('/home/otani/src/common_cv-editor')
from get_cveditor_data import StationData
sys.path.append('/home/otani/src/common')
from common_geography import latlon2distance
import json

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infn', help='input/time_table_param_wk.txt')
    psr.add_argument('indirn', help='output/ev-editor_data/01_仮時刻表（固定間隔）/02_在来線_往復')
    psr.add_argument('--outdirn', '-o', help='output/ev-editor_data/01_仮時刻表（固定間隔）/02_在来線_往復', default=None)
    args = psr.parse_args()

    infn = args.infn
    indirn = args.indirn
    if args.outdirn:
        outdirn = args.outdirn
    else:
        outdirn = args.indirn

    rsfn = 'railstation_master.txt'
    ttpfn = 'time_table_param_input.json'

    # 駅緯度経度取得準備
    station_data = StationData(os.path.join(indirn, 'station_master.txt'))

    # 経路railstation読み込み
    with open(os.path.join(indirn, rsfn), 'r', encoding='utf-8') as f:
        rs = [[x.strip() for x in l.split('\t')] for l in f]
    rs = {l: [[int(x[4])]+x[5:8] for x in rs if x[0]==l] for l in list(set([y[0] for y in rs]))}
    # {路線ID: [[0, 駅ID, 駅Code, 駅名], [1, 駅Code, 駅ID, 駅名], ... ], ...}

    # wkファイル1行ずつ
    out_data_all = []
    with open(infn, 'r', encoding='utf-8') as f:
        _ = next(f)
        for l in f:
            lineID, _, _, _, train_per_day, total_minute, *_ = [x.strip() for x in l.split('\t')] 
            if not train_per_day:  # 列車本数ない路線は飛ばす
                continue
            if not lineID in rs:  # railstation にない路線は飛ばす
                continue
            train_per_day = int(train_per_day)
            total_second = int(total_minute) * 60  # 全線の時間
            
            # 列車間隔(分)
            T = 18 * 60  # 5:00 ~ 23:00 の18時間
            span = round(T / train_per_day)

            stations_cds = [x[2] for x in rs[lineID]]
            station_num = len(stations_cds)
            # 次の駅までの距離のリスト作成
            nextDist = []
            for i in range(station_num-1):
                lat0, lon0 = station_data.get_latlon(stations_cds[i])
                lat1, lon1 = station_data.get_latlon(stations_cds[i+1])
                dist, _, _ = latlon2distance(lat0, lon0, lat1, lon1)
                nextDist.append(dist)
            # 全線の距離
            totalDist = sum(nextDist)
            # 全線の時間を各駅間に割り振る
            nextTime = [int(total_second * x / totalDist) for x in nextDist]
            if any([x < 30 for x in nextTime]):
                print('{0}, {1}'.format(lineID, ' '.join([str(x) for x in nextTime])))
            nextTime.append(None)

            # データ編集
            routes = [{'stationCode': scd, 'nextTime': nt} for scd, nt in zip(stations_cds, nextTime)]
            timeSpan = [{'startTime': '05:00',
                         'endTime': '23:00',
                         'span': span,
                         'dep': stations_cds[0],
                         'term': stations_cds[-1]}]
            other = {'capacity': 1000}
            out_data = {'code': lineID,
                        'timetableParam': {'routes': routes,
                                           'timeSpan': timeSpan,
                                           'other': other}}
            out_data_all.append(out_data)
    
    outfn = os.path.join(outdirn, 'time_table_param_input.json')
    json.dump(out_data_all, open(outfn, 'w'), indent=2)









