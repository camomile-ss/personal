#!/usr/bin/python
# coding: utf-8
"""
時刻表（路線単位）
    index:  駅, 発着
    column: 列車
"""
import argparse
import sys
import os
import pandas as pd
sys.path.append('../common')
from common_date import sec2chartime

def read_railstation(fn, line_name):
    ''' railstation_master から路線の駅のリストと、駅コード->駅名変換辞書をつくる '''
    with open(fn, 'r', encoding='utf-8') as f:
        data = [[x.strip() for x in l.split('\t')] for l in f]
    data = [l for l in data if l[1]==line_name]

    station_names = [l[7] for l in data]
    station_cd2nm = {l[5]: l[7] for l in data}

    return station_names, station_cd2nm

def mk_index(station_names):
    ''' 駅リストから、発着をつけてindex作成 '''
    return [[station_names[0]] + [s for s in station_names[1: -1] for i in range(2)] + [station_names[-1]],
            [ad for i in range(len(station_names) - 1) for ad in ['発', '着']]]

def set_sec(tfn, df, station_cd2nm):
    ''' データ読んで時刻をセット '''
    with open(tfn, 'r', encoding='utf-8') as tf:
        for l in tf:
            l = [x.strip() for x in l.split('\t')]
            trainno, _, _, station_cd, _, _, ar_time, dep_time, _, _, _, _, line_name, _, _ = l
            if line_name == target_line_name:
                if ar_time != '16777215':
                    df.at[(station_cd2nm[station_cd], '着'), trainno] = int(ar_time)
                if dep_time != '16777215':
                    df.at[(station_cd2nm[station_cd], '発'), trainno] = int(dep_time)
    return df

def sort_column(df):
    ''' 左から時刻順に並べる '''
    # 列車番号と1行目の累積秒(始発駅発時刻)をセットにして、1行目の累積秒でソート
    trainnos = list(df.columns)  # 列見出し=列車番号
    firstline = df.iloc[0].to_list()  # 1行目の累積秒
    t_fline = [x for x in list(zip(trainnos, firstline)) if x[1]==x[1]]  # nan除く
    t_fline = sorted(t_fline, key=lambda x: x[1])  # 1行目の累積秒でsort

    # 列車番号
    t_sorted = [x[0] for x in t_fline]  # 1行目あるのの並び
    # 1行目の累積秒ない列車(途中発の列車)を該当の時刻の位置へ
    t_nan = [x for x in trainnos if x not in t_sorted]  # 1行目がない列車番号
    for tno in t_nan:
        # 数字の入ってる最初の行さがす
        for i in range(len(df)):
            if df.iloc[i].loc[tno] == df.iloc[i].loc[tno]:
                comp_v = df.iloc[i].loc[tno]
                # その行の、col_fline_sortedにある列車番号の時刻のリスト
                compline = [df.iloc[i].loc[x] for x in t_sorted]
                break
        # 位置を探す
        for j, c in enumerate(compline):
            if c > comp_v:
                break
        # insert
        t_sorted = t_sorted[:j] + [tno] + t_sorted[j:]

    # dfをならべかえ
    df = df.reindex(t_sorted, axis=1)
    return df

def jikokuhyo(mstdir, target_line_name):

    # 駅リスト, 駅コード->駅名辞書
    rfn = os.path.join(mstdir, 'railstation_master.txt')
    station_names, station_cd2nm = read_railstation(rfn, target_line_name)
    # 枠（駅名、発着 をindexに）
    df = pd.DataFrame(index = mk_index(station_names))
    # 時刻表データ読み込み
    tfn = os.path.join(mstdir, 'timetable_master.txt')
    df = set_sec(tfn, df, station_cd2nm)
    # 左から時刻順にならべる
    df = sort_column(df)
    # 累積秒を時刻表示に
    df = df.applymap(lambda x: sec2chartime(int(x)) if x==x else x)
    df = df.fillna('-')

    return df

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('linename')
    psr.add_argument('mstdir', help='自動化ツール用データ(all_master)')
    psr.add_argument('outfname')
    args = psr.parse_args()
    target_line_name = args.linename
    mstdir = args.mstdir
    outfname = args.outfname

    jikokuhyo_df = jikokuhyo(mstdir, target_line_name)

    jikokuhyo_df.to_csv(outfname)
