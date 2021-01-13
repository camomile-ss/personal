# coding: utf-8
'''
ジョルダンから運行表情報を持ってくる
時刻表データから運行表データ作成
'''
import argparse
import os
import urllib
import sys
import re
from bs4 import BeautifulSoup
sys.path.append('../common/')
from common_web import requests_get

def mk_tt_data(fname):
    ''' 時刻表データ読み込み '''

    with open(fname, 'r', encoding='utf-8') as f:
        data = []
        for r in f:
            l, s, direc, h, m, dest, typ, href_dec, path, *params = r.strip().split('\t')

            # path と params からURLエンコードしたhrefを作る
            params = [x.split('=') for x in params]
            params = ['='.join([x[0], urllib.parse.quote(x[1])]) for x in params]
            href = path + '?' + '&'.join(params)

            data.append([l, s, direc, h, m, dest, typ, href])

    return data

def sihatsu(char, sihatsu_flg):
    ''' 始発 '''
    mob = re.search(r'^(.*行)( 【始発】)?$', char)
    if not mob:
        print('[err] destination: {}'.format(char))
        sys.exit()
    # 始発指定駅・方面、または、行先に【始発】表記あり
    if sihatsu_flg or mob.group(2):
        return mob.group(1)
    else:
        return

def get_unkouhyo_details(href):
    ''' 運行表データ取得 '''

    ptn_direc = re.compile(r'：\s*(.+方面)')
    ptn_time = re.compile(r'^(\d{1,2}:\d{1,2})(発|着)$')

    url = 'https://www.jorudan.co.jp' + href
    r = requests_get(url)
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

        data.append([station, time, ad])

    return direc, data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('dirname')
    args = psr.parse_args()
    dirn = args.dirname

    # 時刻表データ読み込み
    ttfname = os.path.join(dirn, 'time_table_raw.txt')
    data_t = mk_tt_data(ttfname)

    # 始発指定駅・方面ファイルあれば読み込み
    fname = os.path.join(dirn, 'sihatsu.txt')
    sihatsu_station_direc = []
    if os.path.isfile(fname):
        with open(fname, 'r', encoding='cp932') as f:
            sihatsu_station_direc = [tuple([x.strip() for x in l.split('\t')]) for l in f]

    # 【始発】の時刻表データから運行表データ作成
    # 運行表データ出力
    uufname = os.path.join(dirn, 'unkouhyo.txt')
    with open(uufname, 'w', encoding='utf-8') as uuf:
        no = 0  # 列車番号
        for l, s, direc, h, m, dest, typ, href in data_t:
            # 始発だったら
            sihatsu_flg = (l, s, direc) in sihatsu_station_direc
            dest_naked = sihatsu(dest, sihatsu_flg)  # dest_nakedは【始発】抜きの行先
            if dest_naked:
                no += 1  # 列車番号
                print('運行表取得: {0} {1} {2} {3}:{4} {5} {6}'.format(l, s, direc, h, m, dest, typ))
                direc_u, data_unkou = get_unkouhyo_details(href)
                if direc:
                    # 時刻表と運行表の方面名比較
                    if direc_u != direc:
                        print('[方面名相違] 時刻表: {0}, 運行表: {1}'.format(direc, direc_u))
                # 時刻表の方面スペースなら運行表の方面に置き換え
                else:
                    direc = direc_u

                # 出力
                out_data = [[str(no), l, direc, dest_naked, typ] + x for x in data_unkou]
                uuf.write('\n'.join(['\t'.join(x) for x in out_data]) + '\n')
