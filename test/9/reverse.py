# coding: utf-8
'''
第3引数に指定した上り(下り)路線をもとに、その路線の下り(上り)路線を書き換える
'''

import sys
import argparse
from functools import reduce

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname')
    parser.add_argument('outfname')
    parser.add_argument('routename', help='路線名。e.g. [東京メトロ]有楽町線')

    args = parser.parse_args()

    infname = args.infname
    outfname = args.outfname
    base_route = args.routename

    if base_route[-2:] == '_0':
        target_route = base_route.replace('_0', '_1')
    elif base_route[-2:] == '_1':
        target_route = base_route.replace('_1', '_0')
    else:
        print('[err] invalid route_name :', base_route, file = sys.stderr)
        sys.exit()

    with open(infname, 'r', encoding='utf-8') as inf:
        data = [line.strip().split('\t') for line in inf.readlines()]        
    
    # 路線リスト
    routes = [x[3] for x in data]
    routes = sorted(set(routes), key=lambda x: routes.index(x))

    # データに片道しかない場合、反対向きは追加
    if not target_route in routes:
        routes.append(target_route)

    # 路線ごとのデータ
    datas = {route: [x for x in data if x[3]==route] for route in routes}    

    # target <- base の路線名を置き換えて逆順に。
    datas[target_route] = [x[:3] + [target_route] for x in datas[base_route]][::-1]

    outdata=[]
    for route in routes:
        outdata.extend(datas[route])

    #outdata = reduce(lambda x, y: x.extend(y), [datas[route] for route in routes])
    
    with open(outfname, 'w', encoding='utf-8') as outf:
        for row in outdata:
            outf.write('\t'.join(row) + '\n')
