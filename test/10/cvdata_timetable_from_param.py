#!/usr/bin/python

import argparse
import os
import json
import sys
sys.path.append('/home/otani/src/common')
from common_date import char2sectime
sys.path.append('/home/otani/src/common_cv-editor')
from get_cveditor_data import RailwayData

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='output/ev-editor_data/01_仮時刻表（固定間隔）/02_在来線_往復')
    psr.add_argument('--trainno', '-t', type=int, default=0, help='start train no, default=0.')
    args = psr.parse_args()

    infn = os.path.join(args.dirn, 'time_table_param_input.json')
    outfn = os.path.join(args.dirn, 'timetable_master.txt')

    railway_data = RailwayData(os.path.join(args.dirn, 'railway_master.txt'))

    train_no = args.trainno

    param = json.load(open(infn))

    with open(outfn, 'w', encoding='utf-8') as f:
        for p in param:

            lineCD = p['code']
            lineName = railway_data.cd_to_name(lineCD)
            routes = p['timetableParam']['routes']
            stationCDs = [x['stationCode'] for x in routes]
            nextTimes = [x['nextTime'] for x in routes]
            timeSpan = p['timetableParam']['timeSpan']
            capacity = p['timetableParam']['other']['capacity']

            for ts in timeSpan:

                start_sec = char2sectime(ts['startTime'])
                end_sec = char2sectime(ts['endTime'])
                span_sec = ts['span'] * 60
                dep, term = ts['dep'], ts['term']  # 始発駅、終着駅
                stationCDs = stationCDs[stationCDs.index(dep): stationCDs.index(term)+1]
                nextTimes = nextTimes[stationCDs.index(dep): stationCDs.index(term)+1]

                each_train_start_sec = range(start_sec, end_sec+1, span_sec)

                for s in each_train_start_sec:
                    trainID = 'Train{0:04}'.format(train_no)

                    out_data = [[trainID, trainID, i, scd, 0, 2, s+sum(nextTimes[:i]), s+sum(nextTimes[:i]), \
                                 3, 0, 1, 0, lineName, capacity, '-'] \
                                for i, scd in enumerate(stationCDs)]
                    out_data[0][6] = 16777215
                    out_data[-1][7] = 16777215

                    f.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in out_data]))

                    train_no += 1

