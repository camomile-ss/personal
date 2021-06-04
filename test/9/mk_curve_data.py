# coding: utf-8
'''
railstation.txtとSTATION_CODE.txtから中間点なしのcurve_data.txtを作成
'''
import argparse
import os

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('rfname', help='(railstaion.txt)')
    psr.add_argument('scfname', help='(STATION_CODE.txt)')
    psr.add_argument('outdir')
    args = psr.parse_args()

    # STATION_CODE.txtから緯度経度辞書つくる
    ll_dic = {}
    with open(args.scfname, 'r', encoding='utf-8') as scf:
        _ = next(scf)
        for l in scf:
            l = [x.strip() for x in l.split('\t')]
            ll_dic[l[1]] = (l[6], l[7])  # key: 停留所コード, value: (緯度, 経度)

    # 一行ずつrailstation.txt読んでcurve_data.txt出力
    with open(args.rfname, 'r', encoding='utf-8') as inf, \
         open(os.path.join(args.outdir, 'curve_data.txt'), 'w', encoding='utf-8') as outf:
        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            outf.write('\t'.join(list(ll_dic[l[5]]) + [l[7], l[1]]) +'\n')  # 緯度, 経度, 停留所名, 路線名
