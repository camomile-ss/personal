#!/usr/bin/python
'''
親lineIDの片道だけのデータから、元の路線全部を作成
'''
import argparse
import os
import re
import sys
import shutil
from line_edit import copy_curve
from parent1wayToAll import readdata, writedata, reverse_line, \
                    mk_roundtrip_data, mk_parent_and_child_data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('orgdirn', \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v10')
    psr.add_argument('indirn', \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v10_parent_1way_curve修正')
    psr.add_argument('outdirn', \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v11')
    args = psr.parse_args()
    orgdirn = args.orgdirn
    indirn = args.indirn
    outdirn = args.outdirn

    # ファイル名
    rw_name = 'railway_master.txt'
    st_name = 'station_master.txt'
    rs_name = 'railstation_master.txt'
    cv_name = 'curve_master.txt'
    rt_name = 'railtransporter_master.txt'
    tt_name = 'timetable_master.txt'
    tr_name = 'transporter_master.txt'

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # 元ファイル読み込み
    rw_data_org = readdata(os.path.join(orgdirn, rw_name))
    #rs_data_org = readdata(os.path.join(orgdirn, rs_name))
    #cv_data_org = readdata(os.path.join(orgdirn, cv_name))
    rt_data_org = readdata(os.path.join(orgdirn, rt_name))
    tt_data_org = readdata(os.path.join(orgdirn, tt_name))
 
    # 片道ファイル読み込み
    rw_data_p1 = readdata(os.path.join(indirn, rw_name))
    st_data = readdata(os.path.join(indirn, st_name))
    st_header = st_data.pop(0)
    rs_data_p1 = readdata(os.path.join(indirn, rs_name))
    cv_data_p1 = readdata(os.path.join(indirn, cv_name))

    lineID2name_org = {x[0]: x[1] for x in rw_data_org}

    # 編集 --------------------------------------------------
    # 親路線の逆路線を作成
    rw_data, rs_data, cv_data = mk_roundtrip_data(rw_data_p1, rs_data_p1, cv_data_p1, lineID2name_org)

    lineIDs = [x[0] for x in rw_data]
    linenames = [x[1] for x in rw_data]
    rt_data = [x for x in rt_data_org if x[0] in lineIDs]
    tt_data = [x for x in tt_data_org if x[12] in linenames]

    # 書き出し
    writedata(os.path.join(outdirn, rw_name), rw_data)    
    writedata(os.path.join(outdirn, rs_name), rs_data)    
    writedata(os.path.join(outdirn, cv_name), cv_data)
    writedata(os.path.join(outdirn, rt_name), rt_data)
    writedata(os.path.join(outdirn, tt_name), tt_data)
    # station_master.txt, transporter_master.txt は片道ファイルをコピー    
    shutil.copy2(os.path.join(indirn, st_name), outdirn)
    shutil.copy2(os.path.join(indirn, tr_name), outdirn)
