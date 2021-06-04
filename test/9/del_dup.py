# coding: utf-8
'''
駅の前後の緯度経度同じ部分を削除
'''

#import sys
import argparse

def del_duplicate(rdata, size=6):

    print('[route] ' + rdata[0][3])  # 路線名print
    i_del = []  # 消す行のインデックス用
    for r in range(1, len(rdata)-1):
        # 駅の行だったら処理
        if rdata[r][2] != '-':
            # 前後1行～size行まで比較
            for s in range(1, min(size, r, len(rdata)-r-1)):
                i_b = list(range(r-s, r))  # 直前s行のインデックス
                i_a = list(range(r+1, r+s+1))  # 直後s行のインデックス

                # 比較
                if [rdata[x] for x in i_b] == [rdata[x] for x in i_a]:

                    i_del.extend(i_b)
                    i_del.extend(i_a)                    
                    break

    # 残す行のインデックス
    i_remain = [i for i in list(range(len(rdata))) if i not in i_del]
    # 残すデータ
    return [rdata[x] for x in i_remain]

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname')
    parser.add_argument('outfname')

    args = parser.parse_args()

    infname = args.infname
    outfname = args.outfname
    
    with open(infname, 'r', encoding='utf-8') as inf:
        data = [line.strip().split('\t') for line in inf.readlines()]        
    
    # 路線リスト
    routes = [x[3] for x in data]
    routes = sorted(set(routes), key=lambda x: routes.index(x))

    outdata = []
    # 路線ごとに
    for route in routes:
        # その路線のデータ
        rdata = [x for x in data if x[3]==route]
        # 駅前後の重複削除
        rdata = del_duplicate(rdata, size=6)        
        # 出力データに追加
        outdata.extend(rdata)

    with open(outfname, 'w', encoding='utf-8') as outf:
        for row in outdata:
            outf.write('\t'.join(row) + '\n')
        