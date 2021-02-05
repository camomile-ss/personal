#!/usr/bin/python
# coding: utf-8
'''
取得した運行表から路線を整理、優等列車路線のリストを作成
'''
import argparse
import os
import re
import sys
import pickle
from time import ctime
#from rt_class import Vehicle, Lines, Line, Line_higher
from vehicle import Vehicle
from lines import Lines

def mk_line_conv(fn):
    '''
    [return]
        {(ジョルダン路線名, ジョルダン方面名): [(cve路線ID, cve路線名), ...], ...}
    '''
    with open(fn, 'r', encoding='utf-8') as f:
        _ = next(f)
        indata = [[x.strip() for x in l.split('\t')] for l in f]
    data = {}
    for l in indata:
        tt_line, tt_direc, cve_lineID, cve_linename = l
        if (tt_line, tt_direc) in data:
            data[(tt_line, tt_direc)].append((cve_lineID, cve_linename))
        else:
            data[(tt_line, tt_direc)] = [(cve_lineID, cve_linename)]

    return data

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
    with open(fn, 'r', encoding='utf-8') as f:
        indata = [[x.strip() for x in l.split('\t')] for l in f]
    data = {}
    for l in indata:
        lineID, linename, _, _, _, _, _, stationname, *_ = l
        k = (lineID, linename)
        stationname = station_conv[stationname]
        if k in data:
            data[k].append(stationname)
        else:
            data[k] = [stationname]
    return data

def read_data_and_sort(rt_dirn):
    ''' 運行表をすべて読んで、長いデータ順に並べる '''

    ptn = re.compile(r'^(.+)_(.+)_runtables.txt$')
    runtable_fn_list = [x for x in os.listdir(rt_dirn) if ptn.search(x)]

    all_data = []
    for fn in runtable_fn_list:

        mob = ptn.search(fn)
        tt_line, tt_direc = mob.group(1), mob.group(2)

        with open(os.path.join(rt_dirn, fn), 'r', encoding='utf-8') as f:
            _ = next(f)
            data = [[x.strip() for x in l.split('\t')] for l in f]
        # ファイル名から抜き出した tt路線, tt方面を各行の頭につける
        all_data += [[tt_line, tt_direc, str(i)] + x for i, x in enumerate(data)]

    # データ長い順にsort
    print('sort start', ctime())
    all_data.sort(key=lambda x: len(x), reverse=True)
    print('sort end', ctime())

    return all_data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('wkdirn', help='tohoku/v1')
    psr.add_argument('cvedirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線')
    args = psr.parse_args()
    wkdirn = args.wkdirn
    cvedirn = args.cvedirn

    rt_dirn = os.path.join(wkdirn, 'runtables')
    lineconv_fn = os.path.join(wkdirn, 'line_conv.txt')
    stalinedirec_fn = os.path.join(wkdirn, 'stationlinedirec_n.txt')
    railstation_fn = os.path.join(cvedirn, 'railstation_master.txt')
    outdirn = os.path.join(wkdirn, 'runtable_chklist')
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)
    okfn = os.path.join(outdirn, 'runtable_ok.txt')
    osngfn = os.path.join(outdirn, 'runtable_outside_ng.txt')
    pasfn = os.path.join(outdirn, 'runtable_pass.txt')
    errfn = os.path.join(outdirn, 'runtable_err.txt')
    llfn = os.path.join(outdirn, 'runtable_line_list.txt')

    # ジョルダン -> 所定 路線対応リスト取得 1:多
    # {(ジョルダン路線名, ジョルダン方面名): [(cve路線ID, cve路線名), ...], ...}
    line_conv = mk_line_conv(lineconv_fn)

    # cve -> ジョルダン 駅名対応リスト取得 多:1
    # {cve駅名: ジョルダン駅名}
    station_conv = mk_station_conv(stalinedirec_fn)

    # railstation -> 路線 - 駅名リスト
    # {(cve路線ID, cve路線名): ジョルダン駅名, ...}
    railstation_data = mk_railstation_data(railstation_fn, station_conv)

    # Lines instance
    lines = Lines()
    for (lineID, linename), stations in railstation_data.items():
        lines.add_line(lineID, linename, stations)

    # 運行表データを全部読み、長いデータ順に
    all_data = read_data_and_sort(rt_dirn)

    ok_data, osng_data, pas_data, err_data = [], [], [], []
    vehicles = {}

    # 1列車ずつ
    for l in all_data:

        written = False
        tt_line, tt_direc, i, input_station, tt_time, tt_char1, tt_char2, \
            rt_on_station, rt_line, rt_dest, rt_direc, vehicle_no, *rt_data = l

        # 新幹線を飛ばす
        #if any('新幹線' in x for x in [tt_char2, rt_line]):
        #    continue

        outdata = [tt_line, tt_direc, i, input_station, tt_time, tt_char1, tt_char2, \
                    rt_on_station, rt_line, rt_dest, rt_direc, vehicle_no]

        rt_data = [tuple(rt_data[i: i+3]) for i in range(0, len(rt_data), 3)]
        rt_stations = [x[0] for x in rt_data]

        vehicle = Vehicle(rt_stations)

        ls_lines = line_conv[(tt_line, tt_direc)]

        for lsl in ls_lines:
            cve_lineID, cve_linename = lsl

            # 飛ばすファイル
            if cve_lineID == '0' or cve_linename == '0':
                flg = -1
                break

            line_stations = lines.lines[cve_lineID].stations

            flg = vehicle.chk(line_stations)
            
            # OK
            if flg == 0:  # or flg == 1:
                vehicle.set_lineID(cve_lineID)
                lines.lines[cve_lineID].vehicle_cnt += 1
                outdata += [str(flg), cve_lineID, cve_linename]
                ok_data.append(outdata)
                written = True
                break
            # 外側にng駅
            if flg == 7:
                vehicle.set_lineID(cve_lineID)
                lines.lines[cve_lineID].vehicle_cnt += 1
                outdata += [str(flg), cve_lineID, cve_linename, vehicle.middle_start or '', vehicle.middle_end or '']
                outdata += ['-> match'] + vehicle.match_stations
                outdata += ['-> outside ng'] + vehicle.outside_ng_stations
                osng_data.append(outdata)
                written = True
                break
            # 通過駅あり
            if flg == 8:
                new_lineID = lines.add_new_higher(cve_lineID, vehicle.match_stations, vehicle.pass_stations)
                vehicle.set_lineID(new_lineID)
                lines.lines[new_lineID].vehicle_cnt += 1
                outdata += [str(flg), cve_lineID, cve_linename, new_lineID]
                outdata += [vehicle.middle_start or '', vehicle.middle_end or '']
                outdata += ['-> match'] + vehicle.match_stations
                outdata += ['-> pass'] + vehicle.pass_stations
                if vehicle.outside_ng_stations:
                    outdata += ['-> outside ng'] + vehicle.outside_ng_stations
                pas_data.append(outdata)
                written = True
                break
                            
        # 飛ばすファイル
        if flg < 0:
            continue

        # エラー
        if not written:  #flg > 90:
            outdata += [str(flg), cve_lineID, cve_linename]
            if vehicle.mid_ng_stations:
                outdata += ['-> mid ng'] + vehicle.mid_ng_stations
            if vehicle.outside_ng_stations:
                outdata += ['-> outside ng'] + vehicle.outside_ng_stations
            err_data.append(outdata)

        # vehicles ストア
        if tt_line in vehicles:
            if tt_direc in vehicles[tt_line]:
                vehicles[tt_line][tt_direc][i] = vehicle
            else:
                vehicles[tt_line][tt_direc] = {i: vehicle}
        else:
            vehicles[tt_line] = {tt_direc: {i: vehicle}}
    
    # chklist 出力
    def sortdata(data):
        data.sort(key=lambda x: int(x[2]))
        data.sort(key=lambda x: x[1])
        data.sort(key=lambda x: x[0])
        return data
    ok_data = sortdata(ok_data)
    osng_data = sortdata(osng_data)
    pas_data = sortdata(pas_data)
    err_data = sortdata(err_data)

    header = ['tt路線', 'tt方面', 'i', '入力駅', 'tt時刻', 'tt文字列1', 'tt文字列2', \
                'rt_on駅', 'rt路線', 'rt行き先', 'rt方面', '列車no', 'flg', 'cve路線ID', 'cve路線名']

    def writedata(fn, data, header):
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\t'.join(header) + '\n')
            for l in data:
                f.write('\t'.join(l) + '\n')
    writedata(okfn, ok_data, header)
    writedata(osngfn, osng_data, header + ['途中始発', '途中終着', '-> 各駅'])
    writedata(pasfn, pas_data, header + ['new路線ID', '途中始発', '途中終着', '-> 各駅'])
    writedata(errfn, err_data, header + ['-> ng駅'])

    # 路線リスト
    line_list_data = lines.line_list()

    with open(llfn, 'w', encoding='utf-8') as llf:
        llf.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in line_list_data]))

    # pickle
    pickledirn = os.path.join(wkdirn, 'pickle')
    if not os.path.isdir(pickledirn):
        os.mkdir(pickledirn)
    vpfn = os.path.join(pickledirn, 'vehicles.pickle')
    pickle.dump(vehicles, open(vpfn, 'wb'))
    lpfn = os.path.join(pickledirn, 'lines.pickle')
    pickle.dump(lines, open(lpfn, 'wb'))

