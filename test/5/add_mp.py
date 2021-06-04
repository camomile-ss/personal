#!/usr/bin/python
# coding: utf-8

'''
東海道線
    curve_master.txt に、約10m間隔になるよう中間点を追加
'''

import os
import shutil
import sys
sys.path.append('../common_cv-editor')
from set_midpoints_evenly import set_midpoints_evenly

#indirn = '../../data/20200902_東海道線のデータ整備/東海道線/'
#outdirn = './all_master_v0_駅間直線均等'
indirn = './all_master_v1_ツール出力_片道/'
outdirn = './all_master_v2_片道_均等'
curvefname = 'curve_master.txt'
interval = 10

if not os.path.isdir(outdirn):
    os.mkdir(outdirn)

for f in os.listdir(indirn):
    infn = os.path.join(indirn, f)
    outfn = os.path.join(outdirn, f)

    if f == curvefname:
        set_midpoints_evenly(infn, outfn, interval)

    else:
        shutil.copy2(infn, outdirn)
