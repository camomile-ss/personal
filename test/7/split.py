#!/usr/bin/python
# coding: utf-8
'''
cv-editor 用データを分割
'''
import argparse
import os
from split_merge_func import mk_cv_data, split

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('cvedirn')
    psr.add_argument('outdirn')
    args = psr.parse_args()
    cvedirn = args.cvedirn
    outdirn = args.outdirn

    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    *cve_data, st_header = mk_cv_data(cvedirn)

    # 分割基準のファイル
    with open('lineids4split.txt', 'r', encoding='utf-8') as f:
        indata = [[x.strip() for x in l.split('\t')] for l in f.readlines()]
    
    splitname2ID = {x[0]: [y[1] for y in indata if y[0]==x[0]] for x in indata}

    split_data = split(cve_data, 'lineID', splitname2ID)

    for sn, dats in split_data.items():
        sdirn = os.path.join(outdirn, sn)
        if not os.path.isdir(sdirn):
            os.mkdir(sdirn)

        for cn, dat in dats.items():

            def writefile(cn, outdata):
                with open(os.path.join(sdirn, '{}_master.txt'.format(cn)), 'w', encoding='utf-8') as f:
                    f.write(''.join(['\t'.join(x) + '\n' for x in outdata]))

            if cn == 'railway_and_railtransporter':
                cn1, cn2 = 'railway', 'railtransporter'
                writefile(cn1, [x[:2] for x in dat])
                writefile(cn2, [[x[0], x[2]] for x in dat])
            else:
                if cn == 'station':
                    dat = [st_header] + dat
                writefile(cn, dat)
