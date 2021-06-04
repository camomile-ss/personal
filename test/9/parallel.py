# coding: utf-8
'''
Created on Fri Nov 16 14:42:11 2018

@author: otani
'''

import sys
import numpy as np
import csv
sys.path.append('../common')
from common_character import enc_detect

def parallel_data(lines, dist=0.00005):

    # 回転（反時計回りpi/2）だけど緯度,経度はy,xになるのでふつうと逆にする
    rot = np.array([[0, 1],
                    [-1, 0]])

    p = np.array([l[:2] for l in lines])  # もとの緯度・経度
    p_ = [None] * len(lines)  # ずらした点の緯度・経度

    for i, l in enumerate(lines):

        # 進む方向のベクトル
        if i==0:
            x = p[1] - p[0]
        elif i==len(lines)-1:
            x = p[-1] - p[-2]
        else:
            x = p[i+1] - p[i-1]
    
        # ずらす方向のベクトル（大きさdist）
        d = rot.dot(x) * dist / np.linalg.norm(x)
    
        # ずらした点
        p_[i] = p[i] + d

    return p_        


if __name__ == '__main__':

    infname = sys.argv[1]
    outfname = sys.argv[2]
    dist = float(sys.argv[3])
    
    # ファイル読み込み
    with open(infname, 'r', encoding=enc_detect(infname)) as inf:
        in_lines = [l.strip().split(',') for l in inf.readlines()]
        in_lines = [[float(l[0]), float(l[1])] + l[2:] for l in in_lines]
    
    in_lines_down = in_lines[::-1]  # 逆順
    
    #  ずらした緯度・経度のarrayのリスト
    p_up = parallel_data(in_lines, dist=dist)  # 上り
    p_down = parallel_data(in_lines_down, dist=dist)  # 下り
    
    with open(outfname, 'w', encoding='utf-8') as outf:
        outfwriter = csv.writer(outf, lineterminator='\n')

        for i, l in enumerate(in_lines):
            outfwriter.writerow(list(p_up[i]) + [in_lines[i][2], in_lines[i][3] + '_0'])
        for i, l in enumerate(in_lines_down):       
            outfwriter.writerow(list(p_down[i]) + [in_lines_down[i][2], in_lines_down[i][3] + '_1'])
