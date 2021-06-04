#!/usr/bin/python
# coding: utf-8
'''
路線追加・変更・削除
cv-editor データ一式に反映させる
'''
import argparse
import os
import sys
import shutil
import re
from station_edit import read_data, write_data
sys.path.append('../jordan_scraping')
from lines import sepID

def get_seiri(indata):
    '''
    路線整理データ
    [return]
        [路線ID, 路線名, 駅, 駅]
    '''
    indata = [l[1:] for l in indata if l[1]]
    for l in indata:
        while not l[-1]:
            l.pop(-1)
    return indata

def edit_railstation(station_master, stationnames, stationcds, stationIDs):

    railstation_master_out = []
    lineID2name = {}
    for l in line_seiri:
        lineID, linename, *stations = l
        # 重複チェック
        if lineID in lineID2name.keys():
            print('lineID: {} duplicate'.format(lineID))
            sys.exit()
        if linename in lineID2name.values():
            print('linename: 「{}」 duplicate'.format(linename))
            sys.exit()
        lineID2name[lineID] = linename

        for i, s in enumerate(stations):
            if not s in stationnames:
                print('{0} not in station_master. {1} {2} i:{3}'.format(s, lineID, linename, i))
                sys.exit()
            stationcd, stationID = stationcds[s], stationIDs[s]
            railstation_master_out.append( \
                [lineID, linename, '1', '0', str(i), stationID, stationcd, s, '35', '10', '10', '15'] \
            )

    # lineID順にsort
    ptn = re.compile(r'^(Line\d+)(_(\d+))?$')
    def ptnno(x):
        mob = ptn.search(x)
        if mob.group(2):
            return int(mob.group(3))
        else:
            return 0

    lineIDs = sorted(lineID2name.keys(), key=lambda x: ptnno(x))
    lineIDs.sort(key=lambda x: ptn.search(x).group(1))
    railstation_master_out.sort(key = lambda x: lineIDs.index(x[0]))

    return railstation_master_out, lineIDs, lineID2name

def edit_railtransporter(railtransporter_master, lineIDs):

    line2trans = {x[0]: x[1] for x in railtransporter_master}
    railtransporter_master_out = []
    for lineID in lineIDs:
        if lineID in line2trans:
            trans = line2trans[lineID]
        else:
            lineID_p, _ = sepID(lineID)
            if lineID_p in line2trans:
                trans = line2trans[lineID_p]
            else:
                trans = ''
        railtransporter_master_out.append([lineID, trans])
    return railtransporter_master_out

def copy_curve(lineID, linename, rs_sta, cv, latlon=None):
    # 元のcurveデータからできるだけ構成する
    cv_sta = [x[2] for x in cv]
    cv_out = []
    for i in range(len(rs_sta)-1):
        s_from, s_to = rs_sta[i], rs_sta[i+1]
        # 駅の緯度経度はstation_masterから(あれば)
        if latlon:            
            cv_out.append(list(latlon[s_from]) + [s_from, linename])
        else:
            cv_out.append(cv[cv_sta.index(s_from)][:3] + [linename])
        # 駅間のcurve持って来る
        #if all(x in cv_sta for x in (s_from, s_to)):
        cv_between = cv[cv_sta.index(s_from)+1: cv_sta.index(s_to)]
        cv_between = [x[:2] + ['-', linename] for x in cv_between]
        cv_out += cv_between
    if rs_sta:  # 最後の駅
        if latlon:
            cv_out.append(list(latlon[rs_sta[-1]]) + [rs_sta[-1], linename] )
        else:
            cv_out.append(cv[cv_sta.index(rs_sta[-1])][:3] + [linename])
    return cv_out

def edit_curve_master(curve_master, railstation_master_out, lineIDs, \
                      lineID2name, lineID2oldname, latlon):

    curve_master_out = []
    # 路線ごとに
    for lineID in lineIDs:
        linename = lineID2name[lineID]
        # railstationから駅順取得
        rs = [x for x in railstation_master_out if x[0]==lineID]
        rs_sta = [x[7] for x in rs]
        # 元のcurveデータあればそれから構成
        if lineID in lineID2oldname:
            oldlinename = lineID2oldname[lineID]
        else:
            oldlinename = None
        if oldlinename and oldlinename in [x[3] for x in curve_master]:
            cv = [x for x in curve_master if x[3]==oldlinename]
            cv_out = copy_curve(lineID, linename, rs_sta, cv, latlon)
        else:
            # 親路線のcurveデータあればそれから構成
            lineID_p, _ = sepID(lineID)
            if lineID_p in lineID2oldname:
                oldlinename_p = lineID2oldname[lineID_p]
            else:
                oldlinename_p = None
            if oldlinename_p and oldlinename_p in [x[3] for x in curve_master]:
                cv_p = [x for x in curve_master if x[3]==oldlinename_p]
                cv_out = copy_curve(lineID, linename, rs_sta, cv_p, latlon)
            # なければ駅の緯度経度のみ
            else:
                cv_out = [list(latlon[s]) + [s, linename] for s in rs_sta]
        curve_master_out += cv_out

    return curve_master_out

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v3')
    psr.add_argument('outdirn', help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v4')
    psr.add_argument('seirifn', help='tohoku/v2/路線整理.txt')
    args = psr.parse_args()
    indirn = args.indirn
    outdirn = args.outdirn
    seirifn = args.seirifn
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    stfn = 'station_master.txt'
    rsfn = 'railstation_master.txt'
    cvfn = 'curve_master.txt'
    ttfn = 'timetable_master.txt'
    trfn = 'transporter_master.txt'
    rwfn = 'railway_master.txt'
    rtfn = 'railtransporter_master.txt'

    other_fns = [stfn, ttfn, trfn]

    # 変更ファイル読み込み
    indata = read_data(seirifn, encoding='cp932', header=True)
    line_seiri = get_seiri(indata)

    # master 読み込み ----------------------------------##
    def read_master(fn):
        infn = os.path.join(indirn, fn)
        if os.path.isfile(infn):
            return read_data(infn)
        else:
            return []
    
    station_master = read_master(stfn)
    railstation_master = read_master(rsfn)
    curve_master = read_master(cvfn)
    timetable_master = read_master(ttfn)
    #railway_master = read_master(rwfn)
    railtransporter_master = read_master(rtfn)

    # 旧データの路線ID->路線名
    lineID2oldname = {x[0]: x[1] for x in railstation_master}    

    # station_master から
    stationnames = [x[4] for x in station_master]
    stationcds = {x[4]: x[0] for x in station_master}
    stationIDs = {x[4]: x[1] for x in station_master}
    latlon = {x[4]: (x[6], x[7]) for x in station_master}
    # railstation_master 変更
    railstation_master_out, lineIDs, lineID2name \
        = edit_railstation(station_master, stationnames, stationcds, stationIDs)
    # railway_master 変更
    railway_master_out = [[x, lineID2name[x]] for x in lineIDs]
    # railtransporter 変更
    railtransporter_master_out = edit_railtransporter(railtransporter_master, lineIDs)
    # curve_master 変更
    curve_master_out = edit_curve_master(curve_master, railstation_master_out, lineIDs, \
                                         lineID2name, lineID2oldname, latlon)

    outfn = os.path.join(outdirn, rsfn)
    write_data(railstation_master_out, outfn)
    outfn = os.path.join(outdirn, rwfn)
    write_data(railway_master_out, outfn)
    outfn = os.path.join(outdirn, rtfn)
    write_data(railtransporter_master_out, outfn)
    outfn = os.path.join(outdirn, cvfn)
    write_data(curve_master_out, outfn)
    
    # 他のファイルはコピー
    for ofn in other_fns:
        infn = os.path.join(indirn, ofn)
        if os.path.isfile(infn):
            shutil.copy2(infn, outdirn)

