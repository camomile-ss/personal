#!/usr/bin/python
# coding: utf-8
'''
駅名変更・駅削除(他駅に統一)
cv-editor データ一式に反映させる
'''

import argparse
import os
import sys
import shutil

def get_chng(indata):
    '''
    変更ファイル読み込み
    [return]
        {(駅cd, 駅ID, 駅名): (変更後駅cd, 変更後駅ID, 変更後駅名), ...}
        変更後駅名が同じのが複数あるときは、先頭のcd, ID に統一される
    '''

    newnames = [x[3] for x in indata]
    newnames_ = sorted(set(newnames), key=lambda x: newnames.index(x))
    news = [indata[i] for i in [newnames.index(x) for x in newnames_]]
    news = {y[3]: tuple(y[:2]+[y[3]]) for y in news}

    chng = {}
    for l in indata:
        cd, ID, name, newname = l
        chng[(cd, ID, name)] = news[newname]

    return chng

def read_data(fn, encoding='utf-8', header=False):
    with open(fn, 'r', encoding=encoding) as f:
        if header:
            _ = next(f)
        return [[x.strip() for x in l.split('\t')] for l in f]

def write_data(data, fn, header=None):
    with open(fn, 'w', encoding='utf-8') as f:
        if header:
            f.write('\t'.join(header) + '\n')
        f.write(''.join(['\t'.join(l) + '\n' for l in data]))

def chng_station(data, chng):

    header = data.pop(0)
    i_cd = header.index('Station Code')
    i_ID = header.index('StationID')
    i_name = header.index('Station Name')
    i_name2 = header.index('STN Station Name')
    i_lat = header.index('latitude')
    i_lon = header.index('longitude')

    latlon = {}

    for before, after in chng.items():
        data_keys = [(l[i_cd], l[i_ID], l[i_name]) for l in data]
        if not before in data_keys:
            print('err {} not in station_master'.format(before))
            sys.exit()
        i = data_keys.index(before)

        b_cd, b_ID, _ = before
        a_cd, a_ID, a_name = after

        if (b_cd, b_ID) == (a_cd, a_ID):
            data[i][i_name] = a_name
            data[i][i_name2] = a_name

            # 緯度経度保存
            latlon[a_name] = (data[i][i_lat], data[i][i_lon])
        else:
            data.pop(i)

    return header, data, latlon

def chng_railstation(data, chng):

    i_cd, i_ID, i_name = 6, 5, 7
    for l in data:
        k = (l[i_cd], l[i_ID], l[i_name])
        if k in chng:
            (l[i_cd], l[i_ID], l[i_name]) = chng[k]

    return data

def chng_curve(data, chng, latlon):

    i_lat, i_lon, i_name = range(3)
    chng = {k[2]: v[2] for k, v in chng.items()}  # curve は駅名だけ

    for l in data:
        if l[i_name] in chng:
            l[i_name] = chng[l[i_name]]
            (l[i_lat], l[i_lon]) = latlon[l[i_name]]

    return data

def chng_timetable(data, chng):

    i_cd = 3
    chng = {k[0]: v[0] for k, v in chng.items()}  # timetable はcodeだけ

    for l in data:
        if l[i_cd] in chng:
            l[i_cd] = chng[l[i_cd]]

    return data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v2')
    psr.add_argument('outdirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v3')
    psr.add_argument('chngfn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/station_edit.txt')
    args = psr.parse_args()
    indirn = args.indirn
    outdirn = args.outdirn
    chngfn = args.chngfn
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    stfn = 'station_master.txt'
    rsfn = 'railstation_master.txt'
    cvfn = 'curve_master.txt'
    ttfn = 'timetable_master.txt'

    other_fns = ['transporter_master.txt', 'railway_master.txt', 'railtransporter_master.txt', \
                'curve_dummy.txt', 'timetable_dummy.txt']

    # 変更ファイル読み込み
    indata = read_data(chngfn, header=True)
    chng = get_chng(indata)

    # station_master 変更
    infn = os.path.join(indirn, stfn)
    indata = read_data(infn)
    header, outdata, latlon = chng_station(indata, chng)  # 緯度経度がcurve変更で必要
    outfn = os.path.join(outdirn, stfn)
    write_data(outdata, outfn, header=header)
    
    # railstation_master 変更
    infn = os.path.join(indirn, rsfn)
    if os.path.isfile(infn):
        indata = read_data(infn)
        outdata = chng_railstation(indata,chng)
        outfn = os.path.join(outdirn, rsfn)
        write_data(outdata, outfn)

    # curve_master 変更
    infn = os.path.join(indirn, cvfn)
    if os.path.isfile(infn):
        indata = read_data(infn)
        outdata = chng_curve(indata, chng, latlon)
        outfn = os.path.join(outdirn, cvfn)
        write_data(outdata, outfn)

    # timetable_master 変更
    infn = os.path.join(indirn, ttfn)
    if os.path.isfile(infn):
        indata = read_data(infn)
        outdata = chng_timetable(indata, chng)
        outfn = os.path.join(outdirn, ttfn)
        write_data(outdata, outfn)

    # 他のファイルはコピー
    for ofn in other_fns:
        infn = os.path.join(indirn, ofn)
        if os.path.isfile(infn):
            shutil.copy2(infn, outdirn)

