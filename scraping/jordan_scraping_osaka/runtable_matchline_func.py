#!/usr/bin/python
# coding: utf-8
'''
'''
import argparse
import os
import re
import sys
import pickle
from time import ctime
from vehicle_final import Vehicle
from lines import Lines, sepID

def mk_station_conv(fn):
    '''
    [return]
        {cve駅名: ジョルダン駅名}
    '''
    with open(fn, 'r', encoding='utf-8') as f:
        _ = next(f)
        data = [[x.strip() for x in l.split('\t')] for l in f]
    return {x[2]: x[3] for x in data}

def mk_railstation_data(fn, station_conv):
    '''
    railstation から1路線1行のデータを作り親路線すべてを先に並べる
    '''
    with open(fn, 'r', encoding='utf-8') as f:
        indata = [[x.strip() for x in l.split('\t')] for l in f]
    data = {}
    for l in indata:
        lineID, linename, _, _, _, _, _, stationname, *_ = l
        # 駅名はジョルダン駅名に変換
        stationname = station_conv[stationname]
        if lineID in data:
            data[lineID].append(stationname)
        else:
            data[lineID] = [linename, stationname]

    # 並べ替え
    def p0c1(lineID):
        lineID_p, lineID_s = sepID(lineID)
        if lineID_s:
            lineID_s = int(lineID_s)
            s = 1
        else:
            lineID_s = 0
            s = 0
        return s, lineID_p, lineID_s
    sorted_ID = sorted(data.keys(), key=lambda x: p0c1(x)[2])
    sorted_ID.sort(key=lambda x: p0c1(x)[1])
    sorted_ID.sort(key=lambda x: p0c1(x)[0])
    data = [[ID] + data[ID] for ID in sorted_ID]

    return data    

def cve2lines(cvedirn, station_conv, llfn):

    railstation_fn = os.path.join(cvedirn, 'railstation_master.txt')

    # railstation -> 路線 - 駅名リスト
    # {(cve路線ID, cve路線名): ジョルダン駅名, ...}
    railstation_data = mk_railstation_data(railstation_fn, station_conv)

    # Lines instance
    lines = Lines()
    for lineID, linename, *stations_j in railstation_data:
        chk = lines.add_line(lineID, linename, stations_j)
        if type(chk) is int and chk < 0:
            print('railstation err: {0}: {1} {2}'.format(chk, lineID, linename))
            sys.exit()

    # 路線リスト
    lines_list = lines.line_list()
    with open(llfn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(l) + '\n' for l in lines_list]))

    return lines

def rt2vehicles(rt_dirn):

    rt_ptn = re.compile(r'^(.+)_(.+)_runtables.txt$')
    rt_mobs = [rt_ptn.search(x) for x in os.listdir(rt_dirn)]
    rt_fns = [x.group(0) for x in rt_mobs if x]
    rt_ttlines = [x.group(1) for x in rt_mobs if x]
    rt_ttdirecs = [x.group(2) for x in rt_mobs if x]

    vehicles = []   
    # 運行表ファイルひとつずつ読む
    for fn, tt_line, tt_direc in zip(rt_fns, rt_ttlines, rt_ttdirecs):
        with open(os.path.join(rt_dirn, fn), 'r', encoding='utf-8') as f:
            _ = next(f)
            for i, l in enumerate(f):
                uni_key = (tt_line, tt_direc, i)  # ファイル路線名, ファイル方面名, ファイル行
                l = [x.strip() for x in l.split('\t')]
                vehicles.append(Vehicle(uni_key, i, tt_line, tt_direc, l))

    print('vehicle count: {}'.format(len(vehicles)))

    return vehicles

def vehicles_match_line(vehicles, lines, reg_stations, okfn, posfn, errfn):

    with open(okfn, 'w', encoding='utf-8') as okf, \
         open(posfn, 'w', encoding='utf-8') as posf, \
         open(errfn, 'w', encoding='utf-8') as errf:

        header = ['路線', '方面', 'file行', '入力駅', '時刻', '行き先', 'tt_char2']
        okf.write('\t'.join(header + ['split no', '路線ID', '路線名', '->runtable']) + '\n')
        errf.write('\t'.join(header + ['chk', '->駅']) + '\n')

        for v in vehicles:
            outhead = [str(x) for x in v.uni_key] + [v.input_station, v.tt_time, v.tt_char1, v.tt_char2]
            result = v.chk_stations(reg_stations)
            if result < 0:
                outline = outhead + [str(result), 'mid na->'] + [v.stations[i] for i in v.mid_na_idx] 
                if v.outside_na_idx:
                    outline += ['outside na->'] + [v.stations[i] for i in v.outside_na_idx]
                errf.write('\t'.join(outline) + '\n')                 
            if result == 0:
                result = v.match(lines)
                if result == 0:
                    #for i, split in enumerate(v.final_split):
                    #    outline = outhead + [str(i), split.lineID, split.linename] \
                    #            + [y for x in split.runtable for y in x]
                    #    okf.write('\t'.join(outline) + '\n')
                    if v.outside_na_idx:
                        outline = outhead + ['-1', 'outside_na'] \
                                + [x for i in v.outside_na_idx for x in [str(i), v.stations[i]]]
                    else:
                        outline = outhead
                    okf.write('\t'.join(outline) + '\n')
    
    return vehicles

