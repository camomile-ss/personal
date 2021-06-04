# coding: utf-8
'''
駅データ.jpから所定データ作成(1)
抽出
'''
import sys
import os
import argparse
import pandas as pd

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('input_dir', help='input_xxxxxxxx')
    psr.add_argument('infname', help='stationyyyymmddfree.csv')
    psr.add_argument('linefname', help='lineyyyymmddfree.csv')
    psr.add_argument('outfname', help='station_ext.csv')
    args = psr.parse_args()


    # 抽出路線ファイル
    #exfname = 'input/lines.csv'
    exfname = os.path.join(args.input_dir, 'lines.csv')

    # {line_cd: company_cd} の辞書作成
    with open(args.linefname, 'r', encoding='utf-8') as linef:
        _ = next(linef)
        compcd = {l[0]: l[1] for l in [[c.strip() for c in l.split(',')] for l in linef]}

    # 処理順リスト[{'name': 変換後路線名, 'line_cd': line_cdのリスト, 'company_cd': company_cd}, ...] 作成
    with open(exfname, 'r', encoding='utf-8') as exf:
        _ = next(exf)
        lines = []
        for r in exf:
            r = r.strip().split(',')
            linename, line_cd = r[0], [c for c in r[1:] if c]
            company_cd = compcd[line_cd[0]]

            lines.append({'name': linename, 'line_cd': line_cd, 'company_cd': company_cd})

    # 駅データ読み込み
    data = pd.read_csv(args.infname, engine='python', encoding='utf-8', usecols=[0,2,5,9,10], dtype=object)

    # 処理順リスト順にデータ抽出
    all_data = []
    for line in lines:

        # 各line_cdのデータ抽出
        line_data = []
        for cd in line['line_cd']:
            line_data.append(data.loc[data['line_cd']==cd, :])

        # 重複駅削除
        for i in range(1, len(line_data)):
            if line_data[i].iloc[0]['station_name']==line_data[i-1].iloc[-1]['station_name'] and \
               line_data[i].iloc[0]['lon']==line_data[i-1].iloc[-1]['lon'] and \
               line_data[i].iloc[0]['lat']==line_data[i-1].iloc[-1]['lat']:
                line_data[i] = line_data[i].iloc[1:, :]

        # つなげる
        line_data = pd.concat(line_data, ignore_index=True)

        # linename, company_cd 列作成
        line_data['linename'] = line['name']
        line_data['company_cd'] = line['company_cd']

        all_data.append(line_data)

    all_data = pd.concat(all_data, ignore_index=True)
    all_data = all_data.reindex(columns=['company_cd', 'linename', 'line_cd', 'station_cd', 'station_name', 'lat', 'lon'])
    all_data.to_csv(args.outfname, index=None, encoding='utf-8')
