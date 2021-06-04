#!/usr/bin/python

import argparse
import os
import re
import shutil

def readdatas(dirn, fnames):
    ''' 分割元ファイル読み込む '''

    rw_name, st_name, rs_name, tr_name, rt_name, cv_name, tt_name = fnames

    def readdata(fn):
        if os.path.isfile(fn):
            with open(fn, 'r', encoding='utf-8') as f:
                return [[x.strip() for x in l.split('\t')] for l in f]
        else:
            return None

    rw_fn = os.path.join(dirn, rw_name)
    st_fn = os.path.join(dirn, st_name)
    rs_fn = os.path.join(dirn, rs_name)
    tr_fn = os.path.join(dirn, tr_name)
    rt_fn = os.path.join(dirn, rt_name)
    cv_fn = os.path.join(dirn, cv_name)
    tt_fn = os.path.join(dirn, tt_name)

    rw_data = readdata(rw_fn)
    st_data = readdata(st_fn)
    st_header = st_data.pop(0)
    rs_data = readdata(rs_fn)
    tr_data = readdata(tr_fn)
    rt_data = readdata(rt_fn)
    cv_data = readdata(cv_fn)
    tt_data = readdata(tt_fn)

    return rw_data, st_data, st_header, rs_data, tr_data, rt_data, cv_data, tt_data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('compfname', help='input_20201124/company_conv.csv')
    psr.add_argument('indirn', help='output_20201124/for_ev_editor_scd整理後')
    psr.add_argument('outdirn', help='output_20201124/for_ev_editor_scd整理後/分割')
    args = psr.parse_args()
    compfname = args.compfname
    indirn = args.indirn
    outdirn = args.outdirn

    # ファイル名
    rw_name = 'railway_master.txt'
    st_name = 'station_master.txt'
    rs_name = 'railstation_master.txt'
    tr_name = 'transporter_master.txt'
    rt_name = 'railtransporter_master.txt'
    cv_name = 'curve_master.txt'
    tt_name = 'timetable_master.txt'
    fnames = [rw_name, st_name, rs_name, tr_name, rt_name, cv_name, tt_name]

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # 鉄道会社リスト [会社番号, 会社名, プレフィックス] のリスト
    with open(compfname, 'r', encoding='utf-8') as f:
        _ = next(f)
        companys = [[int(x.strip()) if i==0 else x.strip() for i, x in enumerate(l.split(','))] for l in f]

    # 分割元ファイル読み込み
    rw_data, st_data, st_header, rs_data, tr_data, rt_data, cv_data, tt_data \
        = readdatas(indirn, fnames)

    # dummy ファイルあるか
    infnames = os.listdir(indirn)
    ptn = re.compile(r'_dummy.txt$')
    dummyfiles = [x for x in infnames if ptn.search(x)]

    # 鉄道会社ごとに分割
    for c in companys:
        comp_cd, comp_name, _, st_prefix = c

        # station data
        st_c = [x for x in st_data if x[1][:2]==st_prefix]

        # railstation data
        rs_c = [x for x in rs_data if x[5][:2]==st_prefix]

        lineids = set([x[0] for x in rs_c])
        linenames = set([x[1] for x in rs_c])
        # railway data
        rw_c = [x for x in rw_data if x[0] in lineids]
        # railtransporter data
        rt_c = [x for x in rt_data if x[0] in lineids] if rt_data else None
        # transporter data
        if rt_c:
            transporters = set([x[1] for x in rt_c])
            tr_c = [x for x in tr_data if x[0] in transporters]
        else:
            tr_c = None
        # curve data
        cv_c = [x for x in cv_data if x[3] in linenames] if cv_data else None        
        # timetable data
        tt_c = [x for x in tt_data if x[12] in linenames] if tt_data else None

        # データあれば
        if len(st_c) or len(rs_c) or len(rw_c):
            # フォルダ作る
            compdirn = os.path.join(outdirn, "{0:03}_{1}".format(comp_cd, comp_name))
            if not os.path.isdir(compdirn):
                os.mkdir(compdirn)
            # ファイル書く
            def writefile(fn, data):
                if data:
                    with open(fn, 'w', encoding='utf-8') as f:
                        f.write(''.join(['\t'.join(l) + '\n' for l in data]))

            writefile(os.path.join(compdirn, st_name), [st_header]+st_c)
            writefile(os.path.join(compdirn, rw_name), rw_c)
            writefile(os.path.join(compdirn, rs_name), rs_c)
            writefile(os.path.join(compdirn, tr_name), tr_c)
            writefile(os.path.join(compdirn, rt_name), rt_c)
            writefile(os.path.join(compdirn, cv_name), cv_c)
            writefile(os.path.join(compdirn, tt_name), tt_c)

            # dummy ファイルはコピー
            for df in dummyfiles:
                shutil.copy2(os.path.join(indirn, df), compdirn)
