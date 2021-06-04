#!/usr/bin/python
# coding: utf-8

import os
import sys
import re

class StationConvRev:
    '''
    ジョルダン駅名, cve路線ID -> cve駅Code, cve駅ID, cve駅名
        ジョルダン駅名 -> だと、1対多となるので、railstationから 1対1に
    '''

    def __init__(self, stalinedirecfn, cvedirn, shinkansen=False):
        with open(stalinedirecfn, 'r', encoding='utf-8') as f:
            _ = next(f)
            data = [[x.strip() for x in l.split('\t')] for l in f]
        self.ista2csta = {}
        
        ptn = re.compile(r'^(.+)（.+）$')
        
        
        for l in data:
            sta_cd, sta_ID, sta_name, sta_input, *_ = l

            # 新幹線は駅名のカッコ書きを取る
            if shinkansen:
                mob = ptn.search(sta_input)
                if mob:
                    sta_input = mob.group(1)

            v = (sta_cd, sta_ID, sta_name)
            if sta_input in self.ista2csta:
                if v in self.ista2csta[sta_input]:
                    continue
                self.ista2csta[sta_input].append(v)
            else:
                self.ista2csta[sta_input] = [v]

        rsfn = os.path.join(cvedirn, 'railstation_master.txt')
        self.railstation = {}
        with open(rsfn, 'r', encoding='utf-8') as f:
            for l in f:
                l = [x.strip() for x in l.split('\t')]
                lineID, _, _, _, _, sta_ID, sta_cd, sta_name, *_ = l
                v = (sta_cd, sta_ID, sta_name)
                if lineID in self.railstation:
                    self.railstation[lineID].append(v)
                else:
                    self.railstation[lineID] = [v]

    def convert(self, j_stationname, lineID):
        if len(self.ista2csta[j_stationname]) == 1:
            return self.ista2csta[j_stationname][0]
        else:
            if lineID in self.railstation:
                koho = [x for x in self.ista2csta[j_stationname]
                        if x in self.railstation[lineID]]
                if len(koho) == 0:
                    return None
                if len(koho) > 1:
                    print('err 候補複数: {}'.format(
                        ', '.join([' '.join(x) for x in koho])))
                    sys.exit()
                return koho[0]

