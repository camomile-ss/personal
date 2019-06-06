# coding: utf-8
'''
名鉄 路線・駅情報サイトから路線情報を持ってくる
'''
import argparse
import os
import requests
import csv
from bs4 import BeautifulSoup


def requests_get(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    return r

def get_lines():
    ''' 路線・駅情報(サイドバー)から路線情報取得 '''

    r = requests_get('https://www.meitetsu.co.jp/train/station_info/index.html')

    soup = BeautifulSoup(r.content, 'html.parser').find(id='side').find(id='side').find('div', {'class': 'sNav'})

    rosen_eki_joho = soup.find_all('li')[1]

    rosen_li_list = rosen_eki_joho.find('ul').find_all('li')

    # 路線リスト [('line01', '名古屋本線', '/train/station_info/line01/index.html'), .....]
    data = [(li.get('class')[0], li.string, li.find('a').get('href')) for li in rosen_li_list]

    return data

def get_line_stations(div_stationList):
    ''' 1路線の駅情報取得 '''

    eki_li_list = div_stationList.find_all('li')

    data = []
    for no, eki in enumerate(eki_li_list):
        # branchLineはとばす
        if eki.get('class') == 'branchLine':
            continue

        name = ''
        stop = []
        divs = eki.find_all('div')
        for i, div in enumerate(divs):
            # 駅名
            if div.get('class') == ['name']:
                name = div.contents[1]
                furigana = div.find('span').text[1:-1]
                continue
            # 停車列車情報
            if not div.get('class') is None and not div.find('img') is None:
                stop.append(div.find('img').get('src'))  # altやclassは間違いがあるので、停車画像名をストア

        # 路線の駅リスト [[0, 豊橋, とよはし, [/img/a02_misc\10.ong, ...]], [1, 伊奈, いな, [.img/..., ...]], .....]
        data.append({'no': no, 'name': name, 'furigana': furigana, 'stop': stop})

    return data

def get_1page_data(url, lines_stations):
    ''' 各路線ページから路線・駅情報取得 '''

    r = requests_get('https://www.meitetsu.co.jp' + url)

    soup = BeautifulSoup(r.content, 'html.parser').find(id='main')

    heads = soup.find_all('h3', {'class': 'headlineL'})
    lines = soup.find_all('div', {'class': 'stationList'})

    for head, line in zip(heads, lines):
        linename = head.find('div').text

        # 1路線の駅情報取得
        line_data = {'linename': linename, 'stations': get_line_stations(line)}

        lines_stations.append(line_data)

    return lines_stations

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('outdir')
    args = psr.parse_args()

    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)

    # 停車画像: 停車列車対応リスト
    stop_conv = [('/img/a02_misc_10.png', 'ミュースカイ'),
                 ('/img/a02_misc_11.png', '快速特急'),
                 ('/img/a02_misc_12.png', '特急'),
                 ('/img/a02_misc_13.png', '快速急行'),
                 ('/img/a02_misc_14.png', '急行'),
                 ('/img/a02_misc_15.png', '準急'),
                 ('/img/a02_misc_16.png', '普通')
                 ]

    # 路線・駅情報(サイドバー)から路線情報取得
    lines = get_lines()

    # 路線ファイル出力
    #fname = os.path.join(args.outdir, 'lines.txt')
    #with open(fname, 'w', encoding='utf-8') as rf:
    #    rf.write('\n'.join(['\t'.join(r[:2])for r in lines]) + '\n')

    lines_stations = []
    for url in [x[2] for x in lines]:

        # 各路線ページから路線・駅情報取得
        lines_stations = get_1page_data(url, lines_stations)

        #lines_stations[line] = get_lines_stations(line)

    # 路線・駅ファイル出力
    lfname = os.path.join(args.outdir, 'lines.txt')  # 路線ファイル
    sfname = os.path.join(args.outdir, 'lines_stations.txt')  # 路線-駅ファイル
    with open(lfname, 'w', encoding='utf-8') as lf, open(sfname, 'w', encoding='utf-8') as sf:
        lfwriter = csv.writer(lf, delimiter='\t', lineterminator='\n')
        sfwriter = csv.writer(sf, delimiter='\t', lineterminator='\n')
        sfwriter.writerow(['line_no', 'line', 'name', 'furigana'] + [x[1] for x in stop_conv])
        for i, line in enumerate(lines_stations):
            line_no = i+1
            linename = line['linename']
            lfwriter.writerow([line_no, linename])  # 路線no, 路線名 -> 路線ファイル
            stations = line['stations']
            for station in stations:
                stop_flg = [1 if x[0] in station['stop'] else None for x in stop_conv]
                # 路線no, 路線名, 駅名, 駅名ふりがな, 各列車停車フラグ -> 路線-駅ファイル
                sfwriter.writerow([i+1, linename, station['name'], station['furigana']] + stop_flg)
