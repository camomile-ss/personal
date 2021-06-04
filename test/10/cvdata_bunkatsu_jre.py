#!/usr/bin/python

import argparse
import os
import re
import shutil

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirn', help='output_20201124/for_ev_editor_scd整理後/分割/002_JR東日本')
    psr.add_argument('--num', '-n', help='一分割の路線数。default=10', type=int, default=10)
    args = psr.parse_args()
    dirn = args.dirn
    num = args.num

    rw_name = 'railway_master.txt'
    rs_name = 'railstation_master.txt'
    st_name = 'station_master.txt'
    tr_name = 'transporter_master.txt'
    rt_name = 'railtransporter_master.txt'
    cv_name = 'curve_master.txt'
    tt_name = 'timetable_master.txt'

    # 分割元読み込み
    def readdata(fn):
        if os.path.isfile(fn):
            with open(fn, 'r', encoding='utf-8') as f:
                return [[x.strip() for x in l.split('\t')] for l in f]
        else:
            return None

    rw_data = readdata(os.path.join(dirn, rw_name))
    rs_data = readdata(os.path.join(dirn, rs_name))
    st_data = readdata(os.path.join(dirn, st_name))
    st_header = st_data.pop(0)
    tr_data = readdata(os.path.join(dirn, tr_name))
    rt_data = readdata(os.path.join(dirn, rt_name))
    cv_data = readdata(os.path.join(dirn, cv_name))
    tt_data = readdata(os.path.join(dirn, tt_name))

    # dummy ファイルあるか
    infnames = os.listdir(dirn)
    ptn = re.compile(r'_dummy.txt$')
    dummyfiles = [x for x in infnames if ptn.search(x)]

    # 路線num個ごとに分ける
    def writedata(fn, data):
        if data:
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(''.join(['\t'.join(l) + '\n' for l in data]))

    for i in range(0, len(rw_data), num):

        rw_i = rw_data[i: i+num]
        lineids = set([y[0] for y in rw_i])
        linenames = set([y[1] for y in rw_i])
        rs_i = [x for x in rs_data if x[0] in lineids]
        st_i = [x for x in st_data if x[0] in set([y[6] for y in rs_i])]
        rt_i = [x for x in rt_data if x[0] in lineids] if rt_data else None
        tr_i = [x for x in tr_data if x[0] in set([y[1] for y in rt_i])] if tr_data else None
        cv_i = [x for x in cv_data if x[3] in linenames] if cv_data else None
        tt_i = [x for x in tt_data if x[12] in linenames] if tt_data else None

        # ファイル書く
        bundirn = os.path.join(dirn, '{0}-{1}'.format(rw_i[0][0], rw_i[-1][0]))
        if not os.path.isdir(bundirn):
            os.mkdir(bundirn)

        writedata(os.path.join(bundirn, rw_name), rw_i)
        writedata(os.path.join(bundirn, rs_name), rs_i)
        writedata(os.path.join(bundirn, st_name), [st_header] + st_i)
        writedata(os.path.join(bundirn, rt_name), rt_i)
        writedata(os.path.join(bundirn, tr_name), tr_i)
        writedata(os.path.join(bundirn, cv_name), cv_i)
        writedata(os.path.join(bundirn, tt_name), tt_i)

        # dummy ファイルはコピー
        for x in dummyfiles:
            shutil.copy2(os.path.join(dirn, x), bundirn)
