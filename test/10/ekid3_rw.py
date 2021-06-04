# coding: utf-8
'''
駅データ.jpから所定データ作成(3)
RAILSAY.txt, railstation.txt 作成
・逆順データ作成
'''
import sys
import argparse
import pandas as pd

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('infname', help='station_ext_mod2_stname.csv')
    psr.add_argument('SCfname', help='STATION_CODE.txt(input)')
    psr.add_argument('RWfname', help='RAILWAY.txt')
    psr.add_argument('rsfname', help='railstation.txt')
    psr.add_argument('--no', '-n', help='Linexxx start number. default 1.', type=int, default=1)
    psr.add_argument('--rev', '-r', help='make rev data y or n. default y.', default='y', choices=['y', 'n'])
    psr.add_argument('--linenum', '-l', help='line numbering. step 1 or 2. default=1.', type=int, choices=[1, 2], default=1)
    args = psr.parse_args()

    # データ読み込み
    data = pd.read_csv(args.infname, engine='python', encoding='utf-8', dtype=object)

    # 路線名リスト
    lines = data['linename'].drop_duplicates().values.tolist()

    alldata = []
    for line in lines:

        # 路線データ抽出
        line_data = data.loc[data['linename']==line, :].reset_index(drop=True)
        line_data['order'] = line_data.index

        if args.rev == 'y':

            # 逆順データ作成
            line_data_pair = [None] * 2
            if line[-2:] == '_0':
                idx_fwd, idx_rev = 0, 1
                rev_name = line[:-2] + '_1'
            else:
                idx_fwd, idx_rev = 1, 0
                rev_name = line[:-2] + '_0'
            line_data_pair[idx_fwd] = line_data
            rev_data = line_data.sort_index(ascending=False).reset_index(drop=True)
            rev_data['linename'] = rev_name
            rev_data['order'] = rev_data.index
            line_data_pair[idx_rev] = rev_data

            alldata.append(pd.concat(line_data_pair, ignore_index=True))

        else:
            alldata.append(line_data)

    alldata = pd.concat(alldata, ignore_index=True)

    # RAILWAYデータ作成
    railwaynames = alldata['linename'].drop_duplicates()
    railway = pd.DataFrame()
    railway['code'] = ['Line{:03}'.format(x) for x in range(args.no, args.no+len(railwaynames)*args.linenum, args.linenum)]
    railway['name'] = railwaynames.values
    line_dic = {r[1]: r[0] for r in railway.values.tolist()}

    # railstationデータ作成
    alldata['lineID'] = alldata['linename'].apply(lambda x: line_dic[x])
    alldata['fxd1'] = 1
    alldata['fxd2'] = 0
    alldata['dmy1'] = 35
    alldata['dmy2'] = 10
    alldata['dmy3'] = 10
    alldata['dmy4'] = 15
    alldata = alldata.reindex(columns=['lineID', 'linename', 'fxd1', 'fxd2', 'order', 'StationID',
                                       'Station Code', 'station_name', 'dmy1', 'dmy2', 'dmy3', 'dmy4'])
    # 出力
    railway.to_csv(args.RWfname, index=None, header=None, encoding='utf-8', sep='\t')
    alldata.to_csv(args.rsfname, index=None, header=None, encoding='utf-8', sep='\t')
