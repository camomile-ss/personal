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
sys.path.append(os.path.join(os.path.dirname(__file__), '../jordan_scraping'))
from lines import sepID, revID

def readdata(fn):
    ''' 分割元ファイル読み込む '''
    if os.path.isfile(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            return [[x.strip() for x in l.split('\t')] for l in f]
    else:
        return None

def writedata(fn, data):
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(l) + '\n' for l in data]))

def reverse_line(rw_f, rs_f, cv_f, lineID2name_org):
    ''' 1路線の逆路線作成 '''
    lineID, _ = rw_f
    lineID_rev = revID(lineID)
    linename_rev = lineID2name_org[lineID_rev]
    rw_r = [lineID_rev, linename_rev]
    rs_r = [[lineID_rev, linename_rev] + x[2:4] + [str(i)] + x[5:] \
                for i, x in enumerate(rs_f[::-1])]
    cv_r = [x[:3] + [linename_rev] for x in cv_f[::-1]]
    return rw_r, rs_r, cv_r

def ptn_lid():
    return re.compile(r'^Line(\d+)(_(\d+))?$')

def mk_roundtrip_data(rw_data_p1, rs_data_p1, cv_data_p1, lineID2name_org):
    ''' 複数路線の片道路線データから、往復路線データ作成 '''
    ptn = ptn_lid()
    rw_data_p1_r, rs_data_p1_r, cv_data_p1_r = [], [], []  # 逆路線データ
    for lineID, linename in rw_data_p1:    #zip(lineIDs_p1, linenames_p1):
        rw_f = [lineID, linename]
        rs_f = [x for x in rs_data_p1 if x[0]==lineID]
        cv_f = [x for x in cv_data_p1 if x[3]==linename]
        rw_r, rs_r, cv_r = reverse_line(rw_f, rs_f, cv_f, lineID2name_org)
        rw_data_p1_r += [rw_r]
        rs_data_p1_r += rs_r
        cv_data_p1_r += cv_r
    rw_data = sorted(rw_data_p1 + rw_data_p1_r, key=lambda x: \
                        int(ptn.search(x[0]).group(3)) if ptn.search(x[0]).group(2) else 0)        
    rw_data = sorted(rw_data, key=lambda x: int(ptn.search(x[0]).group(1)))        
    rs_data = sorted(rs_data_p1 + rs_data_p1_r, key=lambda x: \
                        int(ptn.search(x[0]).group(3)) if ptn.search(x[0]).group(2) else 0)
    rs_data = sorted(rs_data, key=lambda x: int(ptn.search(x[0]).group(1)))
    linenames = [x[1] for x in rw_data]
    cv_data = sorted(cv_data_p1 + cv_data_p1_r, key=lambda x: linenames.index(x[3]))
    return rw_data, rs_data, cv_data

def mk_parent_and_child_data(rw_data_p, rs_data_p, cv_data_p, rw_org, rs_org):
    ''' 複数路線の親路線データから、親+子路線データ作成 '''
    ptn = ptn_lid()
    lineID2name_p = {x[0]: x[1] for x in rw_data}
    rw_data_c, rs_data_c, cv_data_c = [], [], []
    for lineID, linename in rw_org:
        if not lineID in lineID2name_p.keys():
            rw_data_c += [x for x in rw_org if x[0]==lineID]

            lineID_p, lineID_s = sepID(lineID)
            if not lineID_s:
                print('{0} curve nasi'.format(lineID))
                sys.exit()

            rs_c = [x for x in rs_org if x[0]==lineID]
            c_stationnames = [x[7] for x in rs_c]
            rs_data_c += rs_c

            # 親路線のcurve
            cv_p = [x for x in cv_data if x[3]==lineID2name_p[lineID_p]]
            cv_data_c += copy_curve(lineID, linename, c_stationnames, cv_p)

    rw_data_all = sorted(rw_data_p + rw_data_c, key=lambda x: \
                        int(ptn.search(x[0]).group(3)) if ptn.search(x[0]).group(2) else 0)        
    rw_data_all = sorted(rw_data_all, key=lambda x: int(ptn.search(x[0]).group(1)))
    rs_data_all = sorted(rs_data_p + rs_data_c, key=lambda x: \
                        int(ptn.search(x[0]).group(3)) if ptn.search(x[0]).group(2) else 0)        
    rs_data_all = sorted(rs_data_all, key=lambda x: int(ptn.search(x[0]).group(1)))
    linenames = [x[1] for x in rw_data_all]
    cv_data_all = sorted(cv_data_p + cv_data_c, key=lambda x: linenames.index(x[3]))
    return rw_data_all, rs_data_all, cv_data_all

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

    other_names = ['transporter_master.txt', 'railtransporter_master.txt', 'timetable_master.txt']

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # 元ファイル読み込み
    rw_data_org = readdata(os.path.join(orgdirn, rw_name))
    rs_data_org = readdata(os.path.join(orgdirn, rs_name))
    cv_data_org = readdata(os.path.join(orgdirn, cv_name))
 
    # 片道修正ファイル読み込み
    rw_data_p1 = readdata(os.path.join(indirn, rw_name))
    st_data = readdata(os.path.join(indirn, st_name))
    st_header = st_data.pop(0)
    rs_data_p1 = readdata(os.path.join(indirn, rs_name))
    cv_data_p1 = readdata(os.path.join(indirn, cv_name))

    # lineID
    #lineIDs_org = [x[0] for x in rw_data_org]
    #linenames_org = [x[1] for x in rw_data_org]
    #lineIDs_p1 = [x[0] for x in rw_data_p1]
    #linenames_p1 = [x[0] for x in rw_data_p1]

    lineID2name_org = {x[0]: x[1] for x in rw_data_org}

    # 編集 --------------------------------------------------
    # (1) 親路線の逆路線を作成
    rw_data, rs_data, cv_data = mk_roundtrip_data(rw_data_p1, rs_data_p1, cv_data_p1, lineID2name_org)

    # (2) 子路線作成
    rw_data_all, rs_data_all, cv_data_all\
        = mk_parent_and_child_data(rw_data, rs_data, cv_data, rw_data_org, rs_data_org)

    # 全路線データ書き出し
    writedata(os.path.join(outdirn, rw_name), rw_data_all)    
    writedata(os.path.join(outdirn, rs_name), rs_data_all)    
    writedata(os.path.join(outdirn, cv_name), cv_data_all)
    # station_master.txt は片道修正ファイルをコピー    
    shutil.copy2(os.path.join(indirn, st_name), outdirn)
    # 他のファイルは元ファイルをコピー
    for fn in other_names:
        shutil.copy2(os.path.join(orgdirn, fn), outdirn)
