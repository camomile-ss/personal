# coding: utf-8
'''
名鉄 ジョルダンから時刻表情報を持ってくる(1)
運行表href入りの時刻表データ作成
'''
import argparse
import os
import urllib
import sys
from bs4 import BeautifulSoup
sys.path.append('../common/')
from common_web import requests_get

def mk_line_station_list():
    ''' 駅リストさくせい '''

    fname = 'tt_scraping_input.txt'  # 路線名\t駅名\n
    with open(fname, 'r', encoding='cp932') as f:
        line_station_list = [tuple(l.strip().split('\t')) for l in f]

    return line_station_list

def try_get_tt(line, station):

    line_e = urllib.parse.quote(line)
    sta_e = urllib.parse.quote(station)

    url = 'https://www.jorudan.co.jp/time/eki_' + sta_e + '_' + line_e + '.html'
    r = requests_get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tables = soup.find_all('table', {'class': 'timetable2'})
    return soup, tables

def get_time_tables(line, station):

    soup, tables = try_get_tt(line, station)

    # 結果がでなかったら
    if len(tables) == 0:
        # カッコ書きつけてみる
        for suf in ['（名鉄）', '（愛知）', '（岐阜）']:

            sta_plus = urllib.parse.quote(station + suf)
            soup, tables = try_get_tt(line, sta_plus)
            if tables:
                print('{0} {1} OK.'.format(line, sta_plus))
                break

    # まだ結果でてなければエラー
    if len(tables) == 0:
        print('{0} {1} ERROR !!'.format(line, station), file=sys.stderr)
        sys.exit()

    # 方面複数あったら方面名を取得
    #print(ls, len(tables))
    if len(tables) > 1:
        direc_tabs = soup.find_all('div', {'class': 'bk_tab_time'})
        direcs = [t.find('div', {'class': 'on'}).text for t in direc_tabs]
    else:
        direcs = ['']

    return [(d, t) for d, t in zip(direcs, tables)]

def get_time_table_details(table):

    # 時刻表の1行ごと
    rows = table.find_all('tr')
    data = []
    hr = 0  # 時
    for r in rows:

        # "時"の最初なら時を取得
        if r.find('th'):
            hr = r.find('th').text  # 時

        # 各列車データ取得
        vehis = r.find_all('div')
        for v in vehis:
            a = v.find('a')
            mn = a.b.text  # 分
            href = a.get('href')  # 運行表href

            s = v.find('span').contents
            dest = s[0]  # 行先
            tr_type = s[2]  # 列車種別

            # hrefのgetパラメータを分割
            path, paramstr = href.split('?')
            params = paramstr.split('&')
            params = [x.split('=') for x in params]
            params = ['='.join([x[0], urllib.parse.unquote(x[1])]) for x in params]

            data.append([hr, mn, dest, tr_type, href, path] + params)

    return data

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('outdir')
    args = psr.parse_args()

    # 駅リスト
    lines_stations = mk_line_station_list()

    # 運行表hrefつき時刻表データ作成
    data_t = []
    for i, (l, s) in enumerate(lines_stations):  # l: 路線, s: 駅

        if (i+1) % 10 == 0:
            print('time table {0}/{1} executing..'.format(i+1, len(lines_stations)))

        # 各路線・駅の、(方面・時刻表)のリストを取得
        data_table = get_time_tables(l, s)
        for (d, t) in data_table:  # d: 方面, t: 時刻表table soup

            # 各路線・駅・方面の、時刻表明細を取得
            data_table_detail = get_time_table_details(t)

            # [路線, 駅, 方面] + 時刻表明細 をdataに追加
            data_t.extend([[l, s, d] + x for x in data_table_detail])

    # 運行表hrefつき時刻表データを出力
    ttfname = os.path.join(args.outdir, 'time_table_raw.txt')
    print('{0} writing..'.format(ttfname))
    with open(ttfname, 'w', encoding='utf-8') as ttf:
        for l, s, direc, h, m, dest, typ, href, path, *params in data_t:
            #href_dec = urllib.parse.unquote(href)  # hrefはみにくいのでURLエンコードから戻す
            #ttf.write('\t'.join([l, s, direc, h, m, dest, typ, href_dec, path] + params) + '\n')
            ttf.write('\t'.join([l, s, direc, h, m, dest, typ, href, path] + params) + '\n')  # エンコード戻さない
