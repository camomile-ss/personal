# coding: utf-8
'''
名鉄 ジョルダンから時刻表情報を持ってくる(2)
時刻表データから運行表データ作成
'''
import argparse
import os
import urllib
import sys
import re
import time
from bs4 import BeautifulSoup
sys.path.append('../common/')
from common_web import requests_get

def mk_tt_data(fname):
    ''' 時刻表データ読み込み '''

    with open(fname, 'r', encoding='utf-8') as f:
        data = []
        for r in f:
            #l, s, direc, h, m, dest, typ, href_dec, path, *params = r.strip().split('\t')
            l, s, direc, h, m, dest, typ, href, path, *params = r.strip().split('\t')

            # path と params からURLエンコードしたhrefを作る
            #params = [x.split('=') for x in params]
            #params = ['='.join([x[0], urllib.parse.quote(x[1])]) for x in params]
            #href = path + '?' + '&'.join(params)

            data.append([l, s, direc, h, m, dest, typ, href])

    return data

def sihatsu(char):
    ''' 始発 '''
    mob = re.search(r'^(.*行) 【始発】$', char)
    if mob:
        return mob.group(1)
    else:
        return

def get_unkouhyo_details(href):
    ''' 運行表データ取得 '''

    ptn_direc = re.compile(r'：\s*(.+方面)')
    ptn_time = re.compile(r'^(\d{1,2}:\d{1,2})(.*)$')

    url = 'https://www.jorudan.co.jp' + href

    r = requests_get(url)
    # 失敗することがあるので5回繰り返してみる
    cnt = 0
    while not r:
        if cnt > 5:
            print('requests return none.')
            sys.exit()
        r = requests_get(url)
        cnt += 1

    soup = BeautifulSoup(r.content, 'html.parser').find(id='contents_out').find(id='contents').find(id='left')

    # 方面取り出し
    header = soup.find(id='to0').h3.b.string
    mob = ptn_direc.search(header)

    direc = mob.group(1) if mob else ''

    # 表データ取り出し
    tbl = soup.find('table', {'class': 'tbl_rosen_eki'})
    rows = tbl.find_all('tr')  # 各行
    data = []
    for r in rows:

        if r.get('class') and any(c in ['w', 's'] for c in r.get('class')):  # いらない行
            continue

        station = r.find('td', {'class': 'eki'}).text  # 駅
        time_cha = r.find('td', {'class': 'time'}).text  # xx:xx発(or着)
        # 時刻と発着に分ける
        mob = ptn_time.search(time_cha)
        if not mob:
            print('{0} time_char: {1}. not get time.'.format(station, time_cha))
            time = ''
            ad = ''
        else:
            time = mob.group(1)  # xx:xx （時刻）
            ad = mob.group(2)  # 発or着
            if not ad in ['発', '着']:
                print('time_char:{0} not 発 or 着.'.format(time_cha))

        data.append([station, time, ad])

    return direc, data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('outdir')
    args = psr.parse_args()

    # 時刻表データ読み込み
    ttfname = os.path.join(args.outdir, 'time_table_raw.txt')
    data_t = mk_tt_data(ttfname)

    # 時刻表データから運行表データ作成
    # 運行表データ出力
    unique_unkouhyo = []
    uafname = os.path.join(args.outdir, 'unkouhyo_all.txt')
    uufname = os.path.join(args.outdir, 'unkouhyo_uni.txt')
    with open(uafname, 'w', encoding='utf-8') as uaf, open(uufname, 'w', encoding='utf-8') as uuf:
        no = 0  # 列車番号
        for l, s, direc, h, m, dest, typ, href in data_t:
            # 始発だったら
            #ans = sihatsu(dest)  # ansは【始発】抜きの行先
            #if ans:
            # 5/20修正 始発じゃなくても取得

            no += 1  # 列車番号
            print('{0} : no.{1} {2} {3} {4} {5}:{6} {7} {8}'.format(time.ctime(), no, l, s, direc, h, m, dest, typ))
            direc_u, data_unkou = get_unkouhyo_details(href)
            if direc:
                # 時刻表と運行表の方面名比較
                if direc_u != direc:
                    print('[方面名相違] 時刻表: {0}, 運行表: {1}'.format(direc, direc_u))
            # 時刻表の方面スペースなら運行表の方面に置き換え
            else:
                direc = direc_u

            # 行先から【始発】はとる
            ans = sihatsu(dest)
            if not ans:
                ans = dest

            # unique?
            this_unkouhyo = [[l, direc, ans, typ] + x for x in data_unkou]
            this_key = [str(no), s, h, m]
            out_data = [this_key + x for x in this_unkouhyo]
            if not this_unkouhyo in unique_unkouhyo:
                print('unique')
                unique_unkouhyo.append(this_unkouhyo)

                # uni 出力
                uuf.write('\n'.join(['\t'.join(x) for x in out_data]) + '\n')

            # 全運行表データ出力
            #out_data = [[str(no), l, s, direc, ans, typ] + x for x in data_unkou]
            uaf.write('\n'.join(['\t'.join(x) for x in out_data]) + '\n')
            #data_u.extend([[str(no), l, direc, ans, typ] + x for x in data_unkou])
