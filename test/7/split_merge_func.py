#!/usr/bin/python
# coding: utf-8
'''
cv-editor 用データを分割する関数 split(cv_data, type, splitname2ID)
    [cv_data]
        cv-editorデータ。mk_cv_data(cvdirn) で作成
    [type]
        lineID        : 路線IDで分割
        transporterID : 会社IDで分割
    [splitname2ID]
        key  : 分割dir名
        value: 対象IDのリスト (lineID or transporterID)

分割データをマージする関数 merge(cv_datas)
'''

import os
import re

def filenames():
    rw_name = 'railway_master.txt'
    rt_name = 'railtransporter_master.txt'
    tr_name = 'transporter_master.txt'
    rs_name = 'railstation_master.txt'
    st_name = 'station_master.txt'
    cv_name = 'curve_master.txt'
    tt_name = 'timetable_master.txt'
    return rw_name, rt_name, tr_name, rs_name, st_name, cv_name, tt_name

def datanames():
    rw_nm = 'railway_and_railtransporter'
    tr_nm = 'transporter'
    rs_nm = 'railstation'
    st_nm = 'station'
    cv_nm = 'curve'
    tt_nm = 'timetable'
    return rw_nm, tr_nm, rs_nm, st_nm, cv_nm, tt_nm

def readdata(fn):
    if os.path.isfile(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            return [[x.strip() for x in l.split('\t')] for l in f]
    else:
        return None

def mk_cv_data(cvedirn):

    # ファイル名
    fnames = filenames()
    rw_name, rt_name, tr_name, rs_name, st_name, cv_name, tt_name = fnames

    cv_data = []
    for fn in fnames:
        dat = readdata(os.path.join(cvedirn, fn))
        if fn == st_name:
            st_header = dat.pop(0)
        cv_data.append(dat)

    rw_data, rt_data, tr_data, rs_data, st_data, cv_data, tt_data = cv_data
    
    # railway と railtransporter をひとつに
    if rt_data:
        rt_data ={x[0]: x[1] for x in rt_data}
        rw_data = [[x[0], x[1], rt_data[x[0]] if x[0] in rt_data else None] for x in rw_data]
    else:
        rw_data = [[x[0], x[1], None] for x in rw_data]

    return rw_data, tr_data, rs_data, st_data, cv_data, tt_data, st_header

def split(cve_data, type, splitname2ID):

    rw_data, tr_data, rs_data, st_data, cv_data, tt_data = cve_data
    #cve_names = ['railway_and_railtransporter', 'transporter', 'railstation', 'station', 'curve', 'timetable']

    rw_nm, tr_nm, rs_nm, st_nm, cv_nm, tt_nm = datanames()

    cve_names = [rw_nm, tr_nm, rs_nm, st_nm, cv_nm, tt_nm]

    split_data = {sn: {cn: [] for cn in cve_names} for sn in splitname2ID}
        
    # railway and railtransporter
    if type == 'lineID':
        idx = 0  # lineID
    elif type == 'transporterID':
        idx = 2  # transporterID
    rw_split_data = {sn: [x for x in rw_data if x[idx] in splitname2ID[sn]] for sn in splitname2ID}

    if type == 'lineID':
        splitname2lineID = splitname2ID
        splitname2transporterID = \
            {sn: sorted(set([x[2] for x in v if x[2]])) for sn, v in rw_split_data.items()}
    elif type == 'transporterID':
        splitname2transporterID = splitname2ID
        splitname2lineID = \
            {sn: [x[0] for x in v if x[2] in splitname2ID[sn]] for sn, v in splitname2ID.items()}

    # transporter
    if tr_data:
        tr_split_data = {sn: [x for x in tr_data if x[0] in splitname2transporterID[sn]] \
                         for sn in splitname2transporterID}

    # railstation
    rs_split_data = {sn: [x for x in rs_data if x[0] in splitname2lineID[sn]] for sn in splitname2ID}

    # station
    splitname2stationCDs = {sn: set([x[6] for x in rs_split_data[sn]]) for sn in rs_split_data}
    st_split_data = {sn: [x for x in st_data if x[0] in splitname2stationCDs[sn]] \
                     for sn in splitname2ID}

    # curve
    splitname2linenames = {sn: [x[1] for x in rw_split_data[sn]] for sn in splitname2ID}
    cv_split_data = {sn: [x for x in cv_data if x[3] in splitname2linenames[sn]] for sn in splitname2ID}

    # timetable
    tt_split_data = {sn: [x for x in tt_data if x[12] in splitname2linenames[sn]] for sn in splitname2ID}

    # まとめる
    split_data = [rw_split_data, tr_split_data, rs_split_data, st_split_data, cv_split_data, tt_split_data]
    split_data = {sn: {nm: dat[sn] for nm, dat in zip(cve_names, split_data)} for sn in splitname2ID}

    return split_data

def mk_org_st_data(orgdirn):
    if orgdirn:
        org_st_data = readdata(os.path.join(orgdirn, filenames()[4]))
        org_st_data.pop(0)
        return org_st_data
    else:
        return None

def merge(cv_datas, org_st_data=None):

    cvenames = datanames()
    #rw_nm, tr_nm, rs_nm, st_nm, cv_nm, tt_nm = cvenames
    rw_idx, tr_idx, rs_idx, st_idx, cv_idx, tt_idx = range(len(cvenames))
    
    merge_data = [[x for cv_data in cv_datas for x in cv_data[i]] \
                  for i in range(len(cvenames))]
    st_header = cv_datas[0][-1]

    # station は分割前データあればマージデータに無い駅を追加
    if org_st_data:
        # マージデータにない行追加
        merge_data[st_idx] += [x for x in org_st_data \
                               if not x[0] in [y[0] for y in merge_data[st_idx]]]

    # transporter と station は重複削除して最初のカラムの Code でソート
    for i in [tr_idx, st_idx]:
        merge_data[i] = sorted(set([tuple(x) for x in merge_data[i]]), key=lambda x: int(x[0]))

    # railway, railstation は路線IDの数値部分でソート
    ptn_l = re.compile(r'^Line(\d+)$')
    for i in [rw_idx, rs_idx]:
        merge_data[i] = sorted(merge_data[i], key=lambda x: int(ptn_l.search(x[0]).group(1)))

    # 路線名の、路線ID順の並び
    linename_order = [x[1] for x in merge_data[rw_idx]]

    # timetable は列車番号の数値順にソート
    ptn_t = re.compile(r'^Train(\d+)$')
    merge_data[tt_idx] = sorted(merge_data[tt_idx], key=lambda x: int(ptn_t.search(x[0]).group(1)))

    # curve は路線k名を路線コード順にソート
    merge_data[cv_idx] = sorted(merge_data[cv_idx], key=lambda x: linename_order.index(x[3]))    

    return merge_data, st_header

def writedata(fn, data):
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(x) + '\n' for x in data]))

def out_cv_data(cv_data, st_header, dirn):

    fnames = filenames()
    rw_data, tr_data, rs_data, st_data, cv_data, tt_data = cv_data

    st_data = [st_header] + st_data

    rt_data = [[x[0], x[2]] for x in rw_data]
    rw_data = [[x[0], x[1]] for x in rw_data]

    cv_data = [rw_data, rt_data, tr_data, rs_data, st_data, cv_data, tt_data]

    for fn, dat in zip(fnames, cv_data):
        writedata(os.path.join(dirn, fn), dat)
