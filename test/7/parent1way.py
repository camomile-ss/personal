#!/usr/bin/python
'''
ツールでのカーブ作成用に、親lineIDの片道だけのデータを作成
'''
import argparse
import os
import re
import sys
import shutil
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

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v10')
    psr.add_argument('outdirn', \
        help='../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v10_parent_1way')
    args = psr.parse_args()
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
    #fnames = [rw_name, st_name, rs_name, tr_name, rt_name, cv_name, tt_name]

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # 元ファイル読み込み
    rw_fn = os.path.join(indirn, rw_name)
    st_fn = os.path.join(indirn, st_name)
    rs_fn = os.path.join(indirn, rs_name)
    cv_fn = os.path.join(indirn, cv_name)
    tr_fn = os.path.join(indirn, tr_name)
    rt_fn = os.path.join(indirn, rt_name)
    tt_fn = os.path.join(indirn, tt_name)

    rw_data = readdata(rw_fn)
    #st_data = readdata(st_fn)
    #st_header = st_data.pop(0)
    rs_data = readdata(rs_fn)
    cv_data = readdata(cv_fn)
    tr_data = readdata(tr_fn)
    rt_data = readdata(rt_fn)
    tt_data = readdata(tt_fn)

    # 残すID
    ptn = re.compile(r'Line(\d+)$')
    lineIDs = [x[0] for x in rw_data]
    lineIDs_r = []
    # 親ID で、片道だけ残す
    for ID in lineIDs:
        ID_p, ID_s = sepID(ID)
        # 親ID で、逆路線が残すIDにない
        if not ID_s and not revID(ID) in lineIDs_r:
            lineIDs_r.append(ID)

    out_rw_data = [x for x in rw_data if x[0] in lineIDs_r]
    linename_r = [x[1] for x in out_rw_data]  # 残す路線名
    out_rs_data = [x for x in rs_data if x[0] in lineIDs_r]
    out_cv_data = [x for x in cv_data if x[3] in linename_r]
    out_rt_data = [x for x in rt_data if x[0] in lineIDs_r]
    out_tr_data = [x for x in tr_data if x[0] in set([x[1] for x in out_rt_data])]
    out_tt_data = [x for x in tt_data if x[12] in linename_r]

    # 親ID片道データ書き出し
    writedata(os.path.join(outdirn, rw_name), out_rw_data)    
    writedata(os.path.join(outdirn, rs_name), out_rs_data)    
    writedata(os.path.join(outdirn, cv_name), out_cv_data)    
    writedata(os.path.join(outdirn, rt_name), out_rt_data)    
    writedata(os.path.join(outdirn, tr_name), out_tr_data)    
    writedata(os.path.join(outdirn, tt_name), out_tt_data)    
    shutil.copy2(st_fn, outdirn)  # station_master.txt はコピー

