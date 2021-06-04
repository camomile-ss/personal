#!/usr/bin/python
# coding: utf-8

import argparse
import os
import sys
from split_merge_func import mk_cv_data, mk_org_st_data, merge, out_cv_data

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('splitdirn')
    psr.add_argument('mergedirn')
    psr.add_argument('-o', '--orgdirn', help='分割前のdir(stationを全部入れるため)', default=None)
    args = psr.parse_args()
    splitdirn, mergedirn, orgdirn = args.splitdirn, args.mergedirn, args.orgdirn

    if not os.path.isdir(mergedirn):
        os.mkdir(mergedirn)

    # 分割データを読み込む再帰処理
    def recursive(fp_dirn, cv_datas):
        list_ = os.listdir(fp_dirn)
        files = [x for x in list_ if os.path.isfile(os.path.join(fp_dirn, x))]
        subdirs = [x for x in list_ if os.path.isdir(os.path.join(fp_dirn, x))]

        # ファイルがあれば読み込み
        if files:
            cv_data = mk_cv_data(fp_dirn)
            cv_datas.append(cv_data)

        # 下層があれが下層へ
        for subdir in subdirs:
            cv_datas = recursive(os.path.join(fp_dirn, subdir), cv_datas)

        return cv_datas

    cv_datas = recursive(splitdirn, [])

    # 分割前の駅マスタ読み込み
    org_st_data = mk_org_st_data(orgdirn)

    # マージ
    merge_data, st_header = merge(cv_datas, org_st_data=org_st_data)

    # 出力
    out_cv_data(merge_data, st_header, mergedirn)
