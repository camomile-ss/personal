#!/usr/bin/python
# coding: utf-8

import argparse
import os
import re
import sys
from time import ctime
from rt_class import Vehicle, Lines, Line, Line_higher

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
        j_linename, j_direc, cve_lineID, cve_linename = l
        if (j_linename, j_direc) in data:
            data[(j_linename, j_direc)].append((cve_lineID, cve_linename))
        else:
            data[(j_linename, j_direc)] = [(cve_lineID, cve_linename)]

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

def mk_rail_station_dic(fn):
    with open(fn, 'r', encoding='utf-8') as f:
        indata = [[x.strip() for x in l.split('\t')] for l in f]
    data = {}
    for l in indata:
        lineID, linename, _, _, order, stationID, stationCD, stationname, *_ = l
        if (lineID, linename) in data:
            data[(lineID, linename)].append((order, stationID, stationCD, stationname))
        else:
            data[(lineID, linename)] = [(order, stationID, stationCD, stationname)]
    return data

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
    okfn = os.path.join(wkdirn, 'runtable_ok.txt')
    osngfn = os.path.join(wkdirn, 'runtable_outside_ng.txt')
    pasfn = os.path.join(wkdirn, 'runtable_pass.txt')
    errfn = os.path.join(wkdirn, 'runtable_err.txt')
    llfn = os.path.join(wkdirn, 'runtable_line_list.txt')

    # ジョルダン -> 所定 路線対応リスト取得 1:多
    # {(ジョルダン路線名, ジョルダン方面名): [(cve路線ID, cve路線名), ...], ...}
    line_conv = mk_line_conv(lineconv_fn)

    # cve -> ジョルダン 駅名対応リスト取得 多:1
    # {cve駅名: ジョルダン駅名}
    station_conv = mk_station_conv(stalinedirec_fn)

    # 路線 - 駅名リスト 辞書
    # {(cve路線ID, cve路線名): [(order, cve駅ID, cve駅CD, cve駅名), ...], ...}
    rail_station_dic = mk_rail_station_dic(railstation_fn)
    # {(cve路線ID, cve路線名): [ジョルダン駅名, ...], ...}
    rail_j_station_dic = {k: [station_conv[l[3]] for l in v] for k, v in rail_station_dic.items()}

    ptn = re.compile(r'^Line(\d+)$')
    def revID(id):
        ''' reverse_lineID を求める関数 '''
        mob = ptn.search(id)
        if not mob:
            return None
        no = int(mob.group(1))
        if no % 2 == 0:
            rev_no = no - 1
        else:
            rev_no = no + 1
        return 'Line{:03}'.format(rev_no)

    # Lines instance
    lines = Lines()
    for k, v in rail_j_station_dic.items():
        lineID, linename = k
        ptn_no = lines.add_line(lineID)
        if ptn_no < 0:
            continue
        if ptn_no == 0:
            lines.set_line_stations(lineID, linename, v)
            lines.lines[lineID].reverse_lineID = revID(lineID)
        else:
            lines.set_line_stations_higher(lineID, v)

    # runtable 順次処理
    ptn = re.compile(r'^(.+)_(.+)_runtables.txt$')
    runtable_fn_list = [x for x in os.listdir(rt_dirn) if ptn.search(x)]

    with open(okfn, 'w', encoding='utf-8') as okf, \
         open(osngfn, 'w', encoding='utf-8') as osngf, \
         open(pasfn, 'w', encoding='utf-8') as pasf, \
         open(errfn, 'w', encoding='utf-8') as errf:

        header = ['tt路線', 'tt方面', '入力駅', 'tt時刻', 'tt文字列1', 'tt文字列2', \
                  'rt路線', 'rt行き先', 'rt方面', '列車no', 'flg', 'cve路線ID', 'cve路線名']
        okf.write('\t'.join(header) + '\n')
        osngf.write('\t'.join(header + ['途中始発', '途中終着', '-> 各駅']) + '\n')
        pasf.write('\t'.join(header + ['new路線ID', '途中始発', '途中終着', '-> 各駅']) + '\n')
        errf.write('\t'.join(header + ['-> ng駅']) + '\n')
        
        for fn in runtable_fn_list:

            print(fn, ctime())

            mob = ptn.search(fn)
            j_linename, j_direc = mob.group(1), mob.group(2)

            with open(os.path.join(rt_dirn, fn), 'r', encoding='utf-8') as f:

                _ = next(f)
                # 1列車ずつ
                for i, v in enumerate(f):

                    written = False
                    input_station, tt_time, tt_char1,  tt_char2, rt_line, rt_dest, rt_direc, \
                        vehicle_no, *rt_data = [x.strip() for x in v.split('\t')]

                    # 新幹線を飛ばす
                    if any('新幹線' in x for x in [tt_char2, rt_line]):
                        continue

                    outdata = [j_linename, j_direc, input_station, tt_time, tt_char1, tt_char2, \
                               rt_line, rt_dest, rt_direc, vehicle_no]

                    rt_data = [tuple(rt_data[i: i+3]) for i in range(0, len(rt_data), 3)]
                    rt_stations = [x[0] for x in rt_data]

                    vehicle = Vehicle(rt_stations)

                    ls_lines = line_conv[(j_linename, j_direc)]

                    for lsl in ls_lines:
                        cve_lineID, cve_linename = lsl

                        # 飛ばすファイル
                        if cve_lineID == '0' or cve_linename == '0':
                            flg = -1
                            break

                        line_stations = rail_j_station_dic[lsl]

                        flg = vehicle.chk(line_stations)
                        
                        # OK
                        if flg == 0:  # or flg == 1:
                            lines.lines[cve_lineID].vehicle_cnt_up()
                            outdata += [str(flg), cve_lineID, cve_linename]
                            okf.write('\t'.join(outdata) + '\n')
                            written = True
                            break
                        # 外側にng駅
                        if flg == 7:
                            lines.lines[cve_lineID].vehicle_cnt_up()
                            outdata += [str(flg), cve_lineID, cve_linename, vehicle.middle_start or '', vehicle.middle_end or '']
                            outdata += ['-> match'] + vehicle.match_stations
                            outdata += ['-> outside ng'] + vehicle.outside_ng_stations
                            osngf.write('\t'.join(outdata) + '\n')
                            written = True
                            break
                        # 通過駅あり
                        if flg == 8:
                            new_lineID = lines.add_higher(cve_lineID, vehicle.match_stations, vehicle.pass_stations)
                            outdata += [str(flg), cve_lineID, cve_linename, new_lineID]
                            outdata += [vehicle.middle_start or '', vehicle.middle_end or '']
                            outdata += ['-> match'] + vehicle.match_stations
                            outdata += ['-> pass'] + vehicle.pass_stations
                            if vehicle.outside_ng_stations:
                                outdata += ['-> outside ng'] + vehicle.outside_ng_stations
                            pasf.write('\t'.join(outdata) + '\n')
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
                        errf.write('\t'.join(outdata) + '\n')

    # 路線リスト
    line_list_data = lines.line_list()

    with open(llfn, 'w', encoding='utf-8') as llf:
        llf.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in line_list_data]))
