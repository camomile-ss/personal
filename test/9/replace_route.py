# coding: utf-8
'''
第1引数：curve_data.txt
第2引数：置き換え路線ファイル
curve_data.txtの路線のうち置き換え路線ファイルにある路線を置き換え路線ファイルのデータで置き換えたファイルを出力する
'''
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname')
    parser.add_argument('repfname', help='replace file.')
    parser.add_argument('outfname')

    args = parser.parse_args()

    infname = args.infname
    repfname = args.repfname
    outfname = args.outfname

    # 置き換え路線ファイル -------------------------------------------------##
    with open(repfname, 'r', encoding='utf-8') as repf:
        repdata = [line.strip().split('\t') for line in repf.readlines()]

    # 置き換え路線リスト
    rep_routes = [x[3] for x in repdata]
    
    # 路線ごとの置き換えデータ
    rep_datas = {route: [x for x in repdata if x[3]==route] for route in rep_routes}

    # 元データ ---------------------------------------------------------##
    with open(infname, 'r', encoding='utf-8') as inf:
        data = [line.strip().split('\t') for line in inf.readlines()]        
    
    # 路線リスト
    routes = [x[3] for x in data]
    routes = sorted(set(routes), key=lambda x: routes.index(x))

    # 路線ごとのデータ
    datas = {route: [x for x in data if x[3]==route] for route in routes}    

    # 置き換え ------------------##
    for route in rep_routes:
        if not route in routes:
            print('[warn] replace route [', route, '] not in inputfile.')
        else:
            datas[route] = rep_datas[route]

    # 出力
    with open(outfname, 'w', encoding='utf-8') as outf:
        for route in routes:  # 元データの路線順に
            for row in datas[route]:
                outf.write('\t'.join(row) + '\n')
