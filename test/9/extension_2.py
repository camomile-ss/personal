# coding: utf-8
'''
常磐線 路線延伸用 (2/2)
output:railstation.txt
    JREJBN00	[JRE]常磐線_0	0	-	0	JE0036	36	上野
    
## JREしか使えない。他事業者で使う場合、6カラム目の駅コード(数字)対応必要 ##
'''
import sys
import argparse
import csv

def extension(rdata, add_stations, direction):
    
    # 路線コード~最初の4カラム
    head = rdata[0][:4]

    # 連番の番号確認
    seqno = [int(x[4]) for x in rdata]
    org_len = len(rdata)  # 元の長さ
    if seqno != list(range(org_len)):
        print('no (columns 4) not sequential. :', head[:2], seqno)

    # add_stations順におしりに追加
    if direction == 0:

        # 最初の4カラム + [連番, 駅コード, 駅コード(数値), 駅名]
        add_data = [head + [org_len+i, x[0], int(x[0][3:]), x[1]] for i, x in enumerate(add_stations)]     
        # JREJBN00	[JRE]常磐線_0	0	-	18	JE0252	252	取手

        return rdata + add_data

    # add_stations逆順にあたまに追加
    elif direction == 1:

        # 最初の4カラム + [連番, 駅コード, 駅コード(数値), 駅名]
        add_data = [head + [i, x[0], int(x[0][3:]), x[1]] for i, x in enumerate(add_stations[::-1])]     

        # 元データの連番振り直し
        add_len = len(add_data)
        rdata = [x[:4] + [add_len + i] + x[5:] for i, x in enumerate(rdata)]

        return add_data + rdata

    else:
        print('invalid direction. :', head[0], direction)
        sys.exit()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument('rfname', help='file contains routes. format: routecd \t derection')  # wk_20181220viewer/joban/route.txt
    parser.add_argument('wkfname', help='output of extension_1.py. (station_wk.txt).')
    parser.add_argument('infname', help='railstation.txt(input)')
    parser.add_argument('outfname', help='railstation.txt(output)')
    args = parser.parse_args()
    wkfname = args.wkfname
    infname = args.infname
    rfname = args.rfname
    outfname = args.outfname
    
    # 対象路線よみこみ
    with open(rfname, 'r', encoding='utf-8') as rf:
        target_routes = [x.strip().split('\t') for x in rf.readlines()]
        target_routes = {x[0]: int(x[1]) for x in target_routes}  # 路線コード: 向き

    # 追加駅読込
    with open(wkfname, 'r', encoding='utf-8') as wkf:
        add_stations = [x.strip().split('\t')[1:] for x in wkf.readlines()]
        # ひたち野うしく	JE0256	ひたち野  -> ['JE0256', 'ひたち野']

    # railstation.txt 丸読み
    with open(infname, 'r', encoding='utf-8') as inf:
        data = [x.strip().split('\t') for x in inf.readlines()]
    
    # railstation.txt の路線順リスト(路線コード)
    routes = sorted(set([r[0] for r in data]), key=lambda x: [r[0] for r in data].index(x))

    with open(outfname, 'w', encoding='utf-8') as outf:
        writer = csv.writer(outf, delimiter='\t', lineterminator='\n')

        # 路線順に
        for route in routes:
            print(route, ': executing...')
            
            rdata = [r for r in data if r[0]==route]  # その路線のデータ

            # 対象路線だったら追加処理
            if route in target_routes:
                rdata = extension(rdata, add_stations, target_routes[route])
        
            # 出力
            for r in rdata:
                writer.writerow(r)  # '\t'.join(r) + '\n')
