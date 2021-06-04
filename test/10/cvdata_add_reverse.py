#!/usr/bin/python

import argparse
import os
import shutil
import re
import sys

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='output_20201124/for_ev_editor_scd整理後/分割_mod_マージ/')
    psr.add_argument('outdirn', help='output_20201124/for_ev_editor_scd整理後/分割_mod_マージ_往復/')
    args = psr.parse_args()

    stfn = 'station_master.txt'
    trfn = 'transporter_master.txt'
    rwfn = 'railway_master.txt'
    rtfn = 'railtransporter_master.txt'
    rsfn = 'railstation_master.txt'
    cvfn = 'curve_master.txt'

    line_ptn = re.compile(r'^Line(\d+)$')

    if not os.path.isdir(args.outdirn):
        os.mkdir(args.outdirn)

    # station_master.txt, transporter_master.txt は、そのままコピー
    def copy_file(fn):
        shutil.copy2(os.path.join(args.indirn, fn), os.path.join(args.outdirn, fn))
    copy_file(stfn)
    copy_file(trfn)

    # railway_master, railtransporter_master, railstation_master 読み込み
    def read_file(fn):
        full_fn = os.path.join(args.indirn, fn)
        if not os.path.isfile(full_fn):
            return []
        with open(full_fn, 'r', encoding='utf-8') as f:
            return [[x.strip() for x in l.split('\t')] for l in f]
    railway_data = read_file(rwfn)
    railway_data.sort(key=lambda x: int(line_ptn.search(x[0]).group(1)))
    railtransporter_data = read_file(rtfn)
    railstation_data = read_file(rsfn)
    # curve_master あれば読み込み（なければ空のリスト）
    curve_data = read_file(cvfn)

    # railway_data から line no list 作成
    line_no_list = [int(line_ptn.search(x[0]).group(1)) for x in railway_data]

    # 復路データ作成
    curve_out_data = []
    with open(os.path.join(args.outdirn, rwfn), 'w', encoding='utf-8') as rwf, \
         open(os.path.join(args.outdirn, rtfn), 'w', encoding='utf-8') as rtf, \
         open(os.path.join(args.outdirn, rsfn), 'w', encoding='utf-8') as rsf:

        # railway 1行ずつ
        for rw_l in railway_data:
            line_cd, line_name = rw_l
            line_no = int(line_ptn.search(line_cd).group(1))

            # line no 採番 : 往路の no の次が空いてればそれ、なければ最大の番号の次
            if line_no + 1 in line_no_list:
                line_no_rev = max(line_no_list)
            else:
                line_no_rev = line_no + 1
            line_no_list.append(line_no_rev)
            
            # line cd
            line_cd_rev = 'Line{:03}'.format(line_no_rev)

            # 路線名作成
            if line_name[-2:] == '_0':  # 往路が _0
                line_name_rev = line_name[:-2] + '_1'
            elif line_name[-2:] == '_1':  # 往路が _1
                line_name_rev = line_name[:-2] + '_0'
            else:  # 往路に _0, _1 がない
                line_name_rev = line_name + '_1'
                line_name = line_name + '_0'

            # railway_master 出力
            rwf.write('\t'.join(rw_l) + '\n')
            rwf.write('\t'.join([line_cd_rev, line_name_rev]) + '\n')

            # railtransporter 出力
            if line_cd in [x[0] for x in railtransporter_data]:
                rt_l = railtransporter_data[[x[0] for x in railtransporter_data].index(line_cd)]
                rt_l_rev = [line_cd_rev] + rt_l[1:]
                rtf.write('\t'.join(rt_l) + '\n')
                rtf.write('\t'.join(rt_l_rev) + '\n')

            # railstation 出力
            if line_cd in [x[0] for x in railstation_data]:
                # 元(往路)データ
                rs_line_data = [x for x in railstation_data if x[0]==line_cd]  
                # 復路データ
                rs_line_data_rev = rs_line_data[::-1]
                rs_line_data_rev = [[line_cd_rev, line_name_rev] + x[2:4] + [str(i)] + x[5:] \
                                    for i, x in enumerate(rs_line_data_rev)]  # 連番iは振り直し
                rsf.write(''.join(['\t'.join(l) + '\n' for l in rs_line_data + rs_line_data_rev]))

            # curve データ作成
            if curve_data:
                if line_name in [x[3] for x in curve_data]:
                    curve_line_data = [x for x in curve_data if x[3]==line_name]
                    curve_line_data_rev = [x[:3] + [line_name_rev] for x in curve_line_data][::-1]
                    curve_out_data = curve_out_data + curve_line_data + curve_line_data_rev
    
    # curve あれば出力
    if curve_data:
        with open(os.path.join(args.outdirn, cvfn), 'w', encoding='utf-8') as cvf:
            cvf.write(''.join(['\t'.join(l) + '\n' for l in curve_out_data]))
