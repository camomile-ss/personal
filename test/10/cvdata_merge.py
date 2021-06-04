#!/usr/bin/python
'''
位置調整後の分割データをマージ
station_master.txt
railway_master.txt
railstation_master.txt
'''

import argparse
import os

def exec_bunkatsu_dir(bdirn, outdirn, all_data, fnames, sort_column, first):

    #stfn, rwfn, rsfn, trfn, rtfn, cvfn, ttfn = fnames

    first_new = []
    for i, (fn, sc, fst) in enumerate(zip(fnames, sort_column, first)):

        infn = os.path.join(bdirn, fn)

        # ファイルなければとばす
        if not os.path.isfile(infn):
            first_new.append(fst)
            continue

        # railway, railstation, curve, railtransporter, timetable はそのまま全部書く
        if sc is None:

            outfn = os.path.join(outdirn, fn)

            # 最初だけ open の mode 'w'、以降 'a'
            if fst:
                mode = 'w'
            else:
                mode = 'a'

            with open(infn, 'r', encoding='utf-8') as inf, open(outfn, mode, encoding='utf-8') as outf:
                data = inf.read()
                outf.write(data)

        # station, transporter は全部読んでからソートするので、データをストア
        else:

            with open(infn, 'r', encoding='utf-8') as f:
                # station はヘッダを取得
                if fn == 'station_master.txt':
                    st_header = next(f)

                #st_data = [[x.strip() for x in l.split('\t')] for l in f]
                data_f = f.readlines()
                # 各行にディレクトリ名つける
                #data_f = [[tuple([x.strip() for x in l.split('\t')]), bdirn] for l in data_f]
                data_f = [[x.strip() for x in l.split('\t')] + [bdirn] for l in data_f]

                all_data[i] = all_data[i] + data_f

        first_new.append(False)

    return st_header, all_data, first_new        

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('indirn', help='output_20201124/for_ev_editor_scd整理後/分割_mod/')
    psr.add_argument('outdirn', help='output_20201124/for_ev_editor_scd整理後/分割_mod_マージ/')
    args = psr.parse_args()

    outdirn = args.outdirn
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    stfn = 'station_master.txt'
    rwfn = 'railway_master.txt'
    rsfn = 'railstation_master.txt'
    trfn = 'transporter_master.txt'
    rtfn = 'railtransporter_master.txt'
    cvfn = 'curve_master.txt'
    ttfn = 'timetable_master.txt'

    fnames = [stfn, rwfn, rsfn, trfn, rtfn, cvfn, ttfn]
    sort_column = [0, None, None, 0, None, -1, None]
    # 各ファイルのソートkey column。Noneはソートなしで読んですぐ書く。-1のcurveはstationの重複削除反映してから書く。

    subdirs = [os.path.join(args.indirn, x) for x in os.listdir(args.indirn) if os.path.isdir(os.path.join(args.indirn, x))]

    first = [True] * len(fnames)
    st_header, all_data = '', [[]] * len(fnames)

    # 読む。そのまま書くものはすぐ書いてしまう。
    for sd in subdirs:

        sub_subdirs = [os.path.join(sd, x) for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))]

        # さらに dir ある（JR東日本）
        if sub_subdirs:
            for s_sd in sub_subdirs:
                st_header, all_data, first = exec_bunkatsu_dir(s_sd, outdirn, all_data, fnames, sort_column, first)
                #first = False

        else:
            st_header, all_data, first = exec_bunkatsu_dir(sd, outdirn, all_data, fnames, sort_column, first)
            #first = False

    # ソートしてから書くもの
    latlon_replace = {}
    for data, fn, sc in zip(all_data, fnames, sort_column):

        if sc is None:
            continue

        # curve はあとで
        if sc < 0:
            continue

        # データなければとばす
        if not data:
            continue

        # 重複削除, ソート
        dir_dic = {tuple(x[:-1]): x[-1] for x in data}  # 辞書作成 {stationファイル項目のタプル: ディレクトリ名}
        data = set([tuple(x[:-1]) for x in data])  # ファイル項目だけで重複削除
        #st_all_data = set(st_all_data)
        data = sorted(data, key=lambda x: int(x[sc]))

        # 内容異る重複データをチェック
        cds = [int(x[sc]) for x in data]
        cd_unique = sorted(set(cds))
        cd_count = [cds.count(x) for x in cd_unique]
        chofuku_cds = [x for x, c in zip(cd_unique, cd_count) if c > 1]

        # station : 緯度経度異るデータがあれば選ばせる。
        if fn == 'station_master.txt':
            chofuku_cds = {x: [l for l in data if int(l[sc])==x] for x in chofuku_cds}
            for cd, dt in chofuku_cds.items():
                id = dt[0][1]
                name = dt[0][4]
                print('select lat-lon for {0}:{1}'.format(id, name))
                for i, l in enumerate(dt):
                    print('[{0}] lat: {1}, lon: {2}, dir:{3}'.format(i, l[6], l[7], dir_dic[l]))
                select = input('select no >> ')
                while True:
                    try:
                        select = int(select)
                    except:
                        select = input('select no >>')
                    else:
                        if select < len(dt):
                            break
                        select = input('select no >> ')
                for i, l in enumerate(dt):
                    if i == select:
                        latlon_replace[name] = [l[6], l[7]]
                    else:
                        data.pop(data.index(l))
        else:
            for line in data:
                if int(line[sc]) in chofuku_cds:
                    print('\t'.join(['[err 重複]'] + list(line) + [dir_dic[tuple(line)], fn]))

        # 出力
        outfn = os.path.join(outdirn, fn)
        with open(outfn, 'w', encoding='utf-8') as f:
            if fn == 'station_master.txt':
                f.write(st_header)
            f.write(''.join(['\t'.join(x) + '\n' for x in data]))

    # curve
    cvdata = all_data[fnames.index(cvfn)]
    if cvdata:
        cvdata = [l[:-1] for l in cvdata]
        cvdata = [latlon_replace[l[2]] + l[2:] if l[2] in latlon_replace else l for l in cvdata]

        outfn = os.path.join(outdirn, cvfn)
        with open(outfn, 'w', encoding='utf-8') as f:
            f.write(''.join(['\t'.join(x) + '\n' for x in cvdata]))    
