# coding: utf-8
'''
往復の構成が同じかどうかチェック
'''

import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname')
    parser.add_argument('chkfname')

    args = parser.parse_args()

    infname = args.infname
    chkfname = args.chkfname

    # 読込み
    with open(infname, 'r', encoding='utf-8') as inf:
        data = [line.strip().split('\t') for line in inf.readlines()]        
    
    # 路線リスト
    routes = set([x[3] for x in data])

    # 方向ぬきの路線リスト
    one_side = set([x[:-2] for x in routes])

    # 路線ごとのデータ
    datas = {route: [x for x in data if x[3]==route] for route in routes}    

    # 比較
    outdata = []
    for r in one_side:
        # 往復あるか
        if not (r + '_0' in routes and r + '_1' in routes):
            print('[one side] ', r)  # 片方しかない
            continue
        
        # 往路 1~3カラム
        fwd = [x[:2] for x in datas[r + '_0']]
        # 復路 1~3カラム 逆順
        rvs = [x[:2] for x in datas[r + '_1']][::-1]

        # 比較
        if fwd != rvs:
            print('[not eq] ', r)  # 往復不一致
            
            outdata.extend(datas[r + '_0'])
            outdata.extend(datas[r + '_1'])

    # 不一致データを出力
    with open(chkfname, 'w', encoding='utf-8') as chkf:
        for r in outdata:
            chkf.write('\t'.join(r) + '\n')
