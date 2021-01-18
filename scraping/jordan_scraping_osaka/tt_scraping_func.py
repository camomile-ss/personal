#!/usr/bin/python
# coding: utf-8
'''
ジョルダンから時刻表・運行表情報をもってくる
    1. tt_station2lines
    2. tt_stationline2timetable
    3. tt_get_runtable
    4. tt_timetable2runtable
    5. tt_stationline2runtable
'''
import argparse
import os
import urllib
import requests
import sys
from bs4 import BeautifulSoup
import re
from time import ctime
#sys.path.append('../common/')
#from common_web import requests_get

def tt_station2lines(station, dw='1'):
    '''
    駅名から路線・時刻表一覧の路線リストを取得
    [args]
        dw='1': 平日（'2': 土曜, '3': 日祝）
    [return]
        lines: (路線の色分け, 路線名) のリスト
        station_rep: ジョルダンで自動に変わった駅名。変わらない時は None
        message: メッセージ。なければ None
    # 路線の色分け: 
    '''

    station_q = urllib.parse.quote(station)
    kensaku_q = urllib.parse.quote('検索')
    url = 'https://www.jorudan.co.jp/time/cgi/time.cgi'
    params = {'rf': 'tm', 'pg': '0', 'eki1': station_q, 'Dw': dw, 'S': kensaku_q, 'Csg': '1'}
    params = '&'.join(['='.join([k, v]) for k, v in params.items()])
    url = url + '?' + params

    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    # 表示されるページの内容を調べて分岐 ------------------------------------------------- #
    pan = soup.find('div', {'id': 'pan'})  # ナビゲーション
    pan_items = pan.find_all()
    pan_texts = [x.text for x in pan.find_all()]

    station_rep, message = None, None  

    # ナビゲーションに駅名がない場合
    if pan_texts == ['Home', '時刻表']:
        # 駅名選択画面が表示されてるか取得してみる
        select = soup.find('select', {'id': 'eki1_in'})
        # 表示されてる
        if select:
            # 駅名を選択しないといけないので、メッセージに候補を入れる
            kouho = [x.text for x in select.find_all('option')]
            kouho = ', '.join(kouho)
            message = '駅名選択: ' + kouho
        # 表示されてない（該当駅がない）
        else:
            message = '該当駅なし'
        lines = []

    # 路線時刻表リストが表示される場合
    elif len(pan_items) == 3 and pan_texts[: 2] == ['Home', '時刻表']:

        # 駅名が変わることがあるので置き換える (大曲 -> 大曲（秋田）など)
        if pan_texts[-1] != station:
            message = '駅名変化 -> ' + pan_texts[-1]
            station_rep = pan_texts[-1]
        try:
            # 路線一覧は列ごとに ul が別れてるので全て取得
            ul_list = soup.find('div', {'id': 'left'}).find('div', {'class': 'bk_rosen_list'}).find_all('ul')
        except:
            # 運行されていない駅もある (津軽湯の沢 など) -> メッセージ表示されるので取得する
            try:
                msg = soup.find('div', {'id': 'left'}).find('p').text
            except:
                message = 'err 路線なし (1)'
            else:
                message = '路線なし. jordan msg: ' + msg
            lines = []
        else:
            # 路線一覧の ul が取得できたら、全 ul から路線名を取得
            lines = []
            for ul in ul_list:
                color = ul.get('class')
                if len(color) > 1:
                    print('{0}: (warn) some ul classes : {1}'.format(station, ', '.join(color)))
                color = color[0]
                lines = lines + [(color, x.text) for x in ul.find_all('li')]

            if len(lines)==0:
                message = 'err 路線なし (2)'

    # 路線が一つで時刻表が直接表示される場合
    elif len(pan_items) == 4 and pan_texts[: 2] == ['Home', '時刻表']:

        # 駅名が変わることがあるので置き換える
        if pan_texts[2] != station:
            message = '駅名変化 -> ' + pan_texts[2]
            station_rep = pan_texts[2]
        line = pan_texts[-1]
        lines = [('', line)]  # 色分けはわからない

    else:
        message = 'err htmlフォーマット違う :: ' + pan.text
        lines = []

    if message:
        print('{0}: {1}'.format(station, message))

    return lines, station_rep, message

def tt_stationline2timetable(station, line):
    '''
    駅, 路線 から時刻表データを取得
    [return]
        timetableByDirec: [[方面名, [[時, 分, 行き先, 路線名or列車名, 運行表ファイル名], ...], ...], ...]
        message
    # 運行表ファイル名-> /time/cgi/time.cgi?Csg=........
    '''

    station_q = urllib.parse.quote(station)
    line_q = urllib.parse.quote(line)

    message = None

    url = 'https://www.jorudan.co.jp/time/eki_{0}_{1}.html'.format(station_q, line_q)
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    left = soup.find('div', {'id': 'left'})

    # 方面名を取得（複数）
    h_bigs = left.find_all('div', {'class': 'h_big'}, recursive=False)
    direcs = []
    msgs = []
    for h in h_bigs:
        h = h.find('h2').find('b').text
        h, direc = h.split('\n')
        station_rep, line_rep = h.split(' ： ')
        if station_rep != station + '駅' or line_rep != line:
            msgs.append('{0} {1} -> jordan: {2} {3} ({4})'.format(station, \
                                        line, station_rep, line_rep, direc))
        direcs.append(direc)
    if msgs:
        message = ', '.join(msgs)

    # 時刻表全体を取得
    tables = left.find_all('table', {'class': 'timetable2'})

    # 結果がない
    if len(tables) == 0:
        message = 'err 時刻表ない'
        timetableByDirec = None 

    elif len(tables) != len(direcs):
        message = 'err 方面, 時刻表 数が相違'
        timetableByDirec = None

    else:
        # 時刻表の1行ごと
        timetableByDirec = []
        for direc, table in zip(direcs, tables):
            #print(direc)
            trs = table.find_all('tr', recursive=False)
            timetable = []
            hr = None  # 時
            for tr in trs:

                # "時"の最初なら時を取得
                if tr.find('th', recursive=False):
                    hr = tr.find('th').text  # 時
                    #print(hr + '時')

                # 各列車データ取得
                vehis = tr.find('td', recursive=False).find_all('div', recursive=False)
                for v in vehis:
                    a = v.find('a', recursive=False)
                    mn = a.b.text  # 分
                    #print(mn + '分')
                    href = a.get('href')  # 運行表href

                    vs = [s for s in a.find('span', recursive=False).strings]
                    
                    dest = vs[0]  # 行先
                    
                    line_v = vs[1] if len(vs) > 1 else ''  # 列車種別

                    timetable.append([hr, mn, dest, line_v, href])
            timetableByDirec.append([direc, timetable])

    return timetableByDirec, message

def tt_get_runtable(href):
    ''' 運行表データ取得 '''

    ptn_vehi = re.compile(r'^(.+)：(.+)の運行表$')
    ptn_shinkansen = re.compile(r'^(.+新幹線)（(.+)）の運行表$')
    ptn_direc = re.compile(r'：\s*(.+方面)')
    ptn_time = re.compile(r'^(\d{1,2}:\d{1,2})(発|着)$')

    url = 'https://www.jorudan.co.jp' + href
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    #soup = BeautifulSoup(r.content, 'html.parser').find(id='contents_out').find(id='contents').find(id='left')
    soup = BeautifulSoup(r.content, 'html.parser').find(id='left')

    messages = []
    
    # 路線名、列車名、方面取り出し
    heading2 = soup.find('div', {'class': 'heading2'}).find(['h1', 'h2']).text
    print(heading2)
    # 在来線
    mob = ptn_vehi.search(heading2)
    if mob:
        line = mob.group(1)
        vehi = mob.group(2)
        h_big = soup.find(id='to0').h3.b.string
        mob = ptn_direc.search(h_big)
        if mob:
            direc = mob.group(1)
        else:
            messages.append('warn h_big format : ' + h_big)
            direc = ''
    else:
        # 新幹線
        mob = ptn_shinkansen.search(heading2)
        if mob:
            line = mob.group(1)
            vehi = mob.group(2)
            direc = soup.find(id='to0').h2.b.string
        else:
            messages.append('warn header format : ' + heading2)
            line, vehi, direc = '', '', ''

    print(line, vehi, direc)

    # 表データ取り出し
    tbl = soup.find('table', {'class': 'tbl_rosen_eki'})
    rows = tbl.find_all('tr')  # 各行
    runtable = []
    for r in rows:

        if r.get('class') and any(c in ['w', 's'] for c in r.get('class')):  # いらない行
            continue

        station = r.find('td', {'class': 'eki'}).text  # 駅
        time_cha = r.find('td', {'class': 'time'}).text  # xx:xx発(or着)
        # 時刻と発着に分ける
        mob = ptn_time.search(time_cha)
        if not mob:
            messages.append('{0} time_char: {1}. not get time.'.format(station, time_cha))
            time = ''
            ad = ''
        else:
            time = mob.group(1)  # xx:xx （時刻）
            ad = mob.group(2)  # 発or着

        runtable.append([station, time, ad])

    return line, vehi, direc, runtable, messages

def tt_timetable2runtable(timetable):
    '''
    timetable データから、運行表リストを取得
    [args]
        timetable: [[時, 分, 行き先, 路線, 運行表href], ...]
    [return]
        runtables: [[路線, 行き先, 方面, [[駅, 時刻, 発or着], ...]], ...]
    '''

    messages_out = []

    runtables = []
    for tt in timetable:
        _, _, tt_vehi, tt_line, rt_href = tt
        rt_line, rt_vehi, rt_direc, runtable, messages = tt_get_runtable(rt_href)

        if messages:
            messages_out += [[rt_line, rt_vehi, rt_direc, x] for x in messages]
        if rt_line != tt_line:
            messages_out.append([rt_line, rt_vehi, rt_direc, 'line diff. timetable:{0}, runtable: {1}'.format(tt_line, rt_line)])
        if rt_vehi != tt_vehi:
            messages_out.append([rt_line, rt_vehi, rt_direc, 'vehi diff. timetable:{0}, runtable: {1}'.format(tt_vehi, rt_vehi)])

        data = [rt_line, rt_vehi, rt_direc, runtable]
        runtables.append(data)

    return runtables, messages_out

def tt_stationline2runtable(stationline_list):
    '''
    駅、路線のリストから、運行表を取得して重複を削除して返す
    [args]
        stationline_list: [(駅, 路線), (駅, 路線), ...]
    [return]
        runtables_out: [[路線, 行き先, 方面, [[駅, 時刻, 発or着], ...]], ...]
        messages_out
    '''
    runtables_out, messages_out = [], []
    for s, l in stationline_list:
        print('{0} {1}: {2}'.format(s, l, ctime()))
        timetableByDirec, message_1 = tt_stationline2timetable(s, l)
        if message_1:
            messages_out.append([s, l, message_1])
        for tt_bd in timetableByDirec:
            direc, tt = tt_bd
            print('{0}: {1}'.format(direc, ctime()))
            runtables, messages_2 = tt_timetable2runtable(tt)                
            if messages_2:
                messages_out += [[s, l, x] for x in messages_2]
            for rt_row in runtables:
                if rt_row in runtables_out:
                    continue
                runtables_out.append(rt_row)

    return runtables_out, messages_out

if __name__ == '__main__':

    #psr = argparse.ArgumentParser()

    #station, line = '仙台', '仙石線'
    station, line = '東京', '東海道・山陽新幹線'
    data, message = tt_stationline2timetable(station, line)
    tt1 = data[0][1]
    runtables, messages = tt_timetable2runtable(tt1)
    print(runtables)
    print(messages)
    '''
    hrefs = ['/time/cgi/time.cgi?Csg=0&Sok=1&pg=22&rf=tm&lnm=%E4%BB%99%E7%9F%B3%E7%B7%9A%28%E7%9F%B3%E5%B7%BB%E8%A1%8C%29&rnm=%E4%BB%99%E7%9F%B3%E7%B7%9A&lid=7995537&eki0=%E3%81%82%E3%81%8A%E3%81%B0%E9%80%9A&eki1=%E4%BB%99%E5%8F%B0&eki2=%E7%9F%B3%E5%B7%BB&dir=D%E7%9F%B3%E5%B7%BB%E6%96%B9%E9%9D%A2&Dym=202101&Ddd=15&Dhh=5&Dmn=1&Dw=0&jmp=1']
 
    for h in hrefs:
        line, vehi, direc, data, messages = tt_get_runtable(h)
        print(line)
        print(vehi)
        print(direc)
        print(data)
        print(messages)
    '''
    '''
    list = [('仙台', '仙石線'), ('仙台', '仙山線')]
    for s, l in list:

        data, message = tt_stationline2timetable(s, l)
        print(data)
        print(message)
        print('')
    '''
    '''
    stations = ['仙台', '該当無し', '福島', '庭坂', '大曲', '津軽湯の沢']

    for station in stations:
        print(station)
        lines, station_rep, message = tt_station2lines(station)
        print(lines)
        print(station_rep)
        print(message)
        print('')
    '''
