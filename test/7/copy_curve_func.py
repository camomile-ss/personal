#!/usr/bin/python
# coding: utf-8
'''
cv-editor ツールで生成したcurve を他のファイル・路線に反映させる関数
'''
import sys

def copy_station_latlon(st_data, fix_st_data):
    '''
    新しいstationの緯度経度をstationに反映
    '''
    fix_stationcodes = [x[0] for x in fix_st_data]
    for l in st_data:
        stationcode = l[0]
        if stationcode in fix_stationcodes:
            l[6: 8] = fix_st_data[fix_stationcodes.index(stationcode)][6: 8]
    return st_data

def copy_curve_station_latlon(cv_data, fix_st_data):
    '''
    新しいstationの緯度経度をcurveに反映
    '''
    fix_stationnames = [x[4] for x in fix_st_data]
    for l in cv_data:
        stationname = l[2]
        if stationname in fix_stationnames:
            l[0: 2] = fix_st_data[fix_stationnames.index(stationname)][6: 8]
    return cv_data

def copy_curve_sameline(cv_data, fix_cv_data):
    '''
    同じ路線があればそのままコピー
    '''
    cv_line_order = [x[3] for x in cv_data]
    cv_line_order = sorted(set(cv_line_order), key=lambda x: cv_line_order.index(x))
    fix_cv_lines = set([x[3] for x in fix_cv_data])
    cv_lines4proc = [x for x in cv_line_order if x in fix_cv_lines]
    for line in cv_lines4proc:
        cv_data = [x for x in cv_data if x[3]!=line] + [x for x in fix_cv_data if x[3]==line]
        cv_data.sort(key=lambda x: cv_line_order.index(x[3]))
    return cv_data

def copy_curve(cv, fix_cv):
    '''
    1路線のcurveコピー
    '''
    cv_stations = [x[2] for x in cv if x[2]!='-']
    cv_linename = cv[0][3]
    fix_cv_stcolumn = [x[2] for x in fix_cv]
    #if cv[0][3]=='[JRE]高崎線_0' and fix_cv[0][3]=='[JRE]上野東京ライン_0':
    #    print(cv_stations)
    #    print(cv_linename)
    #    print(fix_cv_stcolumn)    
    for i in range(len(cv_stations)-1):
        st1, st2 = cv_stations[i], cv_stations[i+1]
        if all(st in fix_cv_stcolumn for st in (st1, st2)):
            # 同じ向き
            if fix_cv_stcolumn.index(st1) < fix_cv_stcolumn.index(st2):
                cv_ = fix_cv[fix_cv_stcolumn.index(st1): fix_cv_stcolumn.index(st2) + 1]
            # 逆向き
            else:
                cv_ = fix_cv[fix_cv_stcolumn.index(st2): fix_cv_stcolumn.index(st1) + 1][::-1]
            # 路線名をセット、駅間に駅名 '-' をセット、
            cv_ = [[lat, lon, st if i in (0, len(cv_)-1) else '-', cv_linename] \
                   for i, (lat, lon, st, _) in enumerate(cv_)]
            cv_stcolumn = [x[2] for x in cv]
            cv = cv[:cv_stcolumn.index(st1)] + cv_ + cv[cv_stcolumn.index(st2) + 1:] 
    return cv

def copy_curve_data(cv_data, fix_cv_data, copy_curve_lines):
    '''
    curve_master データのコピー
    '''
    cv_line_order = [x[3] for x in cv_data]
    cv_line_order = sorted(set(cv_line_order), key=lambda x: cv_line_order.index(x))
    fix_cv_lines = set([x[3] for x in fix_cv_data])
    cv_lines4proc = [x for x in cv_line_order \
                     if x in copy_curve_lines and any(l in fix_cv_lines for l in copy_curve_lines[x])]
    for des_line in cv_lines4proc:
        src_lines = copy_curve_lines[des_line]
        cv = [x for x in cv_data if x[3]==des_line]
        for src_line in src_lines:
            if src_line in fix_cv_lines:
                fix_cv = [x for x in fix_cv_data if x[3]==src_line]
                cv = copy_curve(cv, fix_cv)  # 1路線のcurveコピー
        cv_data = [x for x in cv_data if x[3]!=des_line] + cv
        cv_data.sort(key=lambda x: cv_line_order.index(x[3]))
    return cv_data

def readdata(fn):
    if os.path.isfile(fn):
        with open(fn, 'r', encoding='utf-8') as f:
            return [[x.strip() for x in l.split('\t')] for l in f]
    else:
        return None

def writedata(fn, data):
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(''.join(['\t'.join(l) + '\n' for l in data]))

if __name__ == '__main__':
    import argparse
    import os
    import shutil

    psr = argparse.ArgumentParser()
    psr.add_argument('fixdirn')
    psr.add_argument('olddirn')
    psr.add_argument('newdirn')
    psr.add_argument('conffn', help='copy_curve_lines.txt')
    args = psr.parse_args()
    fixdirn, olddirn, newdirn, conffn = args.fixdirn, args.olddirn, args.newdirn, args.conffn

     # ファイル名
    rw_name = 'railway_master.txt'
    st_name = 'station_master.txt'
    rs_name = 'railstation_master.txt'
    tr_name = 'transporter_master.txt'
    rt_name = 'railtransporter_master.txt'
    cv_name = 'curve_master.txt'
    tt_name = 'timetable_master.txt'
    other_names = [rw_name, rs_name, tr_name, rt_name]
   
    # fixデータ
    st_fn = os.path.join(fixdirn, st_name)
    fix_st_data = readdata(st_fn)
    if not fix_st_data:
        print('err fix station data nasi')
        sys.exit()
    st_header = fix_st_data.pop(0)
    cv_fn = os.path.join(fixdirn, cv_name)
    fix_cv_data = readdata(cv_fn)
    if not fix_cv_data:
        print('err fix curve data nasi')
        sys.exit()

    # コピー路線リスト {コピー先路線名: [コピー元路線名, ...], ...}
    copy_curve_lines = readdata(conffn)
    _ = copy_curve_lines.pop(0)  # header飛ばす
    copy_curve_lines = {des: [src for src in [x[1] for x in copy_curve_lines if x[3]==des]] \
                        for des in set([x[3] for x in copy_curve_lines])}

    # olddir内再帰処理
    def recursive(rel_dirn):  # rel_dirn: outdirn からの相対パス
        olddirn_ = os.path.join(olddirn, rel_dirn)
        newdirn_ = os.path.join(newdirn, rel_dirn)
        if not os.path.isdir(newdirn_):
            os.mkdir(newdirn_)
        list_ = os.listdir(olddirn_)
        files = [x for x in list_ if os.path.isfile(os.path.join(olddirn_, x))]
        subdirs = [x for x in list_ if os.path.isdir(os.path.join(olddirn_, x))]

        # 下層があれば下層へ
        for subdirn in subdirs:
            recursive(os.path.join(rel_dirn, subdirn))
        
        # ファイルがあれば処理
        if files:
            # 修正前データ読み込み
            st_data = readdata(os.path.join(olddirn, rel_dirn, st_name))
            _ = st_data.pop(0)
            cv_data = readdata(os.path.join(olddirn, rel_dirn, cv_name))
            tt_data = readdata(os.path.join(olddirn, rel_dirn, tt_name))

            # station の緯度経度をstation, curve に反映
            st_data = copy_station_latlon(st_data, fix_st_data)
            cv_data = copy_curve_station_latlon(cv_data, fix_st_data)
            # curve (同一路線あればそのままコピー)
            cv_data = copy_curve_sameline(cv_data, fix_cv_data)
            # curve (別路線を参照するものの処理)
            cv_data = copy_curve_data(cv_data, fix_cv_data, copy_curve_lines)
            # timetable はツールで列車種別が 1 になってしまうので 0 に戻す
            tt_data = [x[: 10] + ['0'] + x[11: ] for x in tt_data]

            st_data = [st_header] + st_data            

            # 出力
            writedata(os.path.join(newdirn_, st_name), st_data)
            writedata(os.path.join(newdirn_, cv_name), cv_data)
            writedata(os.path.join(newdirn_, tt_name), tt_data)
            # tr, rt, rw, rs はそのままコピー
            for nm in other_names:
                fn = os.path.join(olddirn_, nm)
                if os.path.isfile(fn):
                    shutil.copy2(fn, newdirn_)

    recursive('')

