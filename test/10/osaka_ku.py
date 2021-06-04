#!/usr/bin/python

import re

class GetEkidata:
    def __init__(self, fn='駅データ/station20200619free.csv'):

        with open(fn, 'r', encoding='utf-8') as f:
            _ = next(f)
            self.data = [[x.strip() for x in l.split(',')] for l in f]

    def stationname2address_mkdic(self):
        self.st2ad = {x[2]: x[8] for x in self.data}

    def stationname2address(self, stationname):
        if stationname in self.st2ad:
            return self.st2ad[stationname]
        else:
            return None 

if __name__ == '__main__':

    infn = '../../data/20201218_急ぎ_大阪メトロデータ作成/大阪メトロ_駅名.txt'
    outfn = '../../data/20201218_急ぎ_大阪メトロデータ作成/大阪メトロ_駅名_区名.txt'

    datfn = '駅データ/station20200619free.csv'

    get_ekidata = GetEkidata()
    get_ekidata.stationname2address_mkdic()

    ptn = re.compile(r'大阪市(.+区)')

    with open(infn, 'r', encoding='utf-8') as inf, open(outfn, 'w', encoding='utf-8') as outf:
        _ = next(inf)
        for l in inf:
            sta = l.strip()
            addr = get_ekidata.stationname2address(sta)
            mob = ptn.search(addr)
            ku, kugai = '', ''
            if mob:
                ku = mob.group(1)
            else:
                kugai = addr
                print('{0} : {1}'.format(sta, addr))
            outf.write('\t'.join([sta, ku, kugai]) + '\n')

