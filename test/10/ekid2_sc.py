# coding: utf-8
'''
駅データ.jpから所定データ作成(2)
STATION_CODE.txt 作成
・別事業者の同一駅を区別
'''
import sys
import os
import argparse
import pandas as pd

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('input_dir', help='input_xxxxxxxx')
    psr.add_argument('infname', help='station_ext_mod.csv')
    psr.add_argument('SCfname', help='STATION_CODE.txt')
    psr.add_argument('outfname', help='station_ext_mod2_stname.csv')
    psr.add_argument('--no', '-n', help='Station Code start number. default 1.', type=int, default=1)
    args = psr.parse_args()

    # 事業者名辞書作成
    #comfname = 'input/company_conv.csv'
    comfname = os.path.join(args.input_dir, 'company_conv.csv')
    with open(comfname, 'r', encoding='utf-8') as comf:
        _ = next(comf)
        com_conv = {l[0]: l[2] for l in [[c.strip() for c in l.split(',')] for l in comf]}

    # データ読み込み
    data = pd.read_csv(args.infname, engine='python', encoding='utf-8', dtype=object)

    # 駅リスト作成
    com_stations = data.reindex(columns=['company_cd', 'station_name', 'lat', 'lon'])  #.copy()
    com_stations = [tuple(x) for x in com_stations.values.tolist()]
    com_stations = sorted(set(com_stations), key=com_stations.index)

    # campany_cd と station_name で unique かチェック
    test = set(r[:2] for r in com_stations)  # company_cd, station_name だけのリスト
    if len(test) != len(com_stations):
        print('same station have diff lat or lon.')
        for t in sorted(test, key=lambda x: int(x[0])):
            com_st_t = [x for x in com_stations if x[:2]==t]
            # 同じ company_cd, station_name が複数行あったら
            if len(com_st_t) != 1:
                for i, c_s in enumerate(com_st_t):
                    print(' '.join(c_s))
                    # 2件目以降削除
                    if i != 0:
                        com_stations.remove(c_s)

        #com_stations_sorted = sorted(com_stations, key=lambda x: x[1])
        #for s in com_stations_sorted:
        #    print(s)

    # 同じ駅名を区別
    stations = set(r[1] for r in com_stations)  # 駅名のみの一意リスト
    for s in stations:
        samename = [r for r in com_stations if r[1]==s]
        # 同じ駅名いっこだけなら次へ
        if len(samename) == 1:
            continue
        # 同じ駅名2個以上なら事業者名つけて区別
        for x in samename:
            if not x[0] in com_conv:
                print('conpany_cd {0} not in company_conv.csv.'.format(x[0]))
                sys.exit()
            cn = com_conv[x[0]]  # 事業者名 (JRK, 西鉄, ...)
            new_name = '{0}[{1}]'.format(x[1], cn)  # 変換駅名 e.g.) 大牟田[JRK], 大牟田[西鉄]
            # データを修正
            data.loc[(data['company_cd']==x[0])&(data['station_name']==x[1]), 'station_name'] = new_name

    # STATION_CODE データ作成
    sc_data = data.reindex(columns=['station_name', 'lat', 'lon']).drop_duplicates(subset='station_name').reset_index(drop=True)
    #sc_data = pd.DataFrame([x[1:] for x in com_stations])
    sc_data.columns = ['Station Name', 'latitude', 'longitude']
    #sc_data = sc_data.drop_duplicates(subset=['Station Name']).reset_index(drop=True)

    #sc_data['Station Code'] = pd.Series(sc_data.index).apply(lambda x: 'Station{:03}'.format(x + args.no))
    #sc_data['StationID'] = pd.Series(sc_data.index).apply(lambda x: '{:03}'.format(x + args.no))
    sc_data['Station Code'] = pd.Series(sc_data.index).apply(lambda x: x + args.no)
    sc_data['StationID'] = pd.Series(sc_data.index).apply(lambda x: 'Station{:03}'.format(x + args.no))
    sc_data['Validity'] = 1
    sc_data['Type'] = 'Station'
    sc_data['STN Station Name'] = sc_data['Station Name']
    sc_data = sc_data.reindex(columns=['Station Code', 'StationID', 'Validity', 'Type', 'Station Name',
                               'STN Station Name', 'latitude', 'longitude'])
    sc_data.to_csv(args.SCfname, encoding='utf-8', sep='\t', index=None)

    # データに Station Code, StationID 追加
    sc_dic = {r[4]: (r[0], r[1]) for r in sc_data.values.tolist()}
    data['Station Code'] = data['station_name'].apply(lambda x: sc_dic[x][0])
    data['StationID'] = data['station_name'].apply(lambda x: sc_dic[x][1])
    # データ出力
    data.to_csv(args.outfname, encoding='utf-8', index=None)

