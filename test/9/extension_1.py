# coding: utf-8
'''
常磐線 路線延伸用 1/2
output(station_wk.txt): 正式駅名, 駅コード, 短縮駅名
'''

import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument('infname', help='file of station names (formal name).')  # ./wk_20181220viewer/joban/station_add.txt
    parser.add_argument('cdfname', help='STATION_CODE.txt')
    parser.add_argument('outfname')  # ./wk_20181220viewer/joban/station_wk.txt
    args = parser.parse_args()
    infname = args.infname
    cdfname = args.cdfname
    outfname = args.outfname
    
    # 常磐線駅リストよみこみ
    with open(infname, 'r', encoding='utf-8') as inf:
        stations = [x.strip() for x in inf.readlines()]

    # STATION_CODE.txt読込
    with open(cdfname, 'r', encoding='cp932') as cdf:
        sta_cd_master = [x.strip().split(',') for x in cdf.readlines()]
        # JE0256,1,Station,ひたち野,ひたち野うしく,36.00754318,140.1582897

    # 常磐線駅順に
    outdata = []
    for s in stations:
        sta_cd_ext = [x for x in sta_cd_master if x[0][:2]=='JE' and x[4]==s]
        
        # 二つ以上ある
        if len(sta_cd_ext) > 1:
            print('2 or more :', s, sta_cd_ext)
            continue
        
        # ひとつもない
        if len(sta_cd_ext) < 1:
            print(s, 'not in cdf')
            continue
        
        # ひとつだけあったら出力用にストア
        outdata.append([sta_cd_ext[0][4], sta_cd_ext[0][0], sta_cd_ext[0][3]])                
        
    # 出力
    with open(outfname, 'w', encoding='utf-8') as outf:
        for r in outdata:
            outf.write('\t'.join(r) + '\n')

