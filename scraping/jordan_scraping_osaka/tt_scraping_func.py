#!/usr/bin/python
# coding: utf-8
'''
ジョルダンから時刻表・運行表情報をもってくる
    1. sta2line(station, dw='1')
    2. staLine2direc(station, line)
    3. sta2lineDirec(station, dw='1')
    4. staLineDirec2timetable(station, line, tt_direc)
    5-1. get_runtable_zairaisen(soup, heading2_h2)
    5-2. get_runtable_shinkansen(soup, heading2_h1)
    5. get_runtable(href)
    6. timetable2runtable(timetable)
    7. staLineDirec_list2runtable(sta_line_direc_list)
'''
import argparse
import os
import urllib
import requests
import sys
from bs4 import BeautifulSoup
import re
from time import ctime

def sta2line(station, dw='1'):
    '''
    駅名から路線・時刻表一覧の路線リストを取得
    [args]
        dw='1': 平日（'2': 土曜, '3': 日祝）
    [return]
        lines: 路線名 のリスト
        station_rep: ジョルダンで自動に変わった駅名。変わらない時は None
        message: メッセージ。なければ None
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
                lines += [x.text for x in ul.find_all('li')]

            if len(lines)==0:
                message = 'err 路線なし (2)'

    # 路線が一つで時刻表が直接表示される場合
    elif len(pan_items) == 4 and pan_texts[: 2] == ['Home', '時刻表']:

        # 駅名が変わることがあるので置き換える
        if pan_texts[2] != station:
            message = '駅名変化 -> ' + pan_texts[2]
            station_rep = pan_texts[2]
        lines = [pan_texts[-1]]  # 唯一の路線

    else:
        message = 'err htmlフォーマット違う :: ' + pan.text
        lines = []

    if message:
        print('{0}: {1}'.format(station, message))

    return lines, station_rep, message

def staLine2direc(station, line, dw='1'):
    '''
    駅, 路線 から方面リストを取得
    [args]
        dw='1': 平日（'2': 土曜, '3': 日祝）
    [return]
        tt_direc_list: [tt方面名, ...]
        tt_table_list: [時刻表soup, ...]
        message: なければ None
    '''

    station_q = urllib.parse.quote(station)
    line_q = urllib.parse.quote(line)

    message = None

    url = 'https://www.jorudan.co.jp/time/eki_{0}_{1}.html?&Dw={2}'.format(station_q, line_q, dw)
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    tt_direc_list, tt_table_list = [], []
    try:
        soup = BeautifulSoup(r.content, 'html.parser')
        left = soup.find('div', {'id': 'left'})
    except:
        message = 'err 時刻表なし (soup or left なし) : {0} {1}'.format(station, line)
    else:

        try:
            # 方面名を取得（複数）
            h_big_list = left.find_all('div', {'class': 'h_big'}, recursive=False)
            tt_direc_list = []
            for h_big in h_big_list:
                h = h_big.find('h2').find('b').text
                _, tt_direc = h.split('\n')
                tt_direc_list.append(tt_direc)

            # 時刻表全体を取得
            tt_table_list = left.find_all('table', {'class': 'timetable2'})

        except:
            message = 'err 時刻表なし (h_big or h_big.text) : {0} {1}'.format(station, line)
        else:
            if len(tt_table_list) == 0:
                message = 'err 時刻表なし (len=0) : {0} {1}'.format(station, line)
            elif len(tt_table_list) != len(tt_direc_list):
                message = 'err 方面, 時刻表 数が相違 : {0} {1}'.format(station, line)

    return tt_direc_list, tt_table_list, message

def sta2lineDirec(station, dw='1'):
    '''
    駅から、路線・方面リスト取得
    [args]
        dw='1': 平日（'2': 土曜, '3': 日祝）
    [return]
        lines_direcs: [(路線名, [方面, ...], 路線単位のメッセージ), ...]
        station_rep: ジョルダンで自動に変わった駅名。変わらない時は None
        message1: 駅単位のメッセージ
    # 路線の色分け: 
    '''
    lines, station_rep, message1 = sta2line(station, dw=dw)
    lines_direcs = []
    for line in lines:
        tt_direc_list, _, message2 = staLine2direc(station, line)
        lines_direcs.append((line, tt_direc_list, message2))

    return lines_direcs, station_rep, message1

def staLineDirec2timetable(station, line, tt_direc, dw='1'):
    '''
    駅, 路線, 方面 から時刻表データを取得
    [return]
        timetable: [[時刻, tt文字列1, tt文字列2, 運行表ファイル名], ...]
        message1: 駅・路線単位のメッセージ
        message2: 駅・路線・方面単位のメッセージ
    # tt文字列1 e.g.) 飯能行【始発】
    # tt文字列2 e.g.) 西武池袋線, むさし1号(Laview)
    # 運行表ファイル名-> /time/cgi/time.cgi?Csg=........
    '''

    # 方面リスト, 時刻表soupリストを取得
    tt_direc_list, tt_table_list, message1 = staLine2direc(station, line, dw=dw)

    # 方面がない
    message2 = None
    if not tt_direc in tt_direc_list: 
        #message2 = 'err 方面なし : {0} {1} {2}'.format(station, line, tt_direc)
        message2 = 'err 方面なし'
        timetable = None
    else:
        table = tt_table_list[tt_direc_list.index(tt_direc)]
        # 時刻表の1行ごと
        trs = table.find_all('tr', recursive=False)
        timetable = []
        hr = None  # 時
        for tr in trs:

            # "時"の最初なら時を取得
            if tr.find('th', recursive=False):
                hr = tr.find('th', recursive=False).text  # 時

            # 各列車データ取得
            vehicles = tr.find('td', recursive=False).find_all('div', recursive=False)
            for v in vehicles:
                a = v.find('a', recursive=False)
                mn = a.b.text  # 分
                tt_time = '{0:02}:{1:02}'.format(int(hr), int(mn))  # 時刻
                href = a.get('href')  # 運行表href

                vs = [s for s in a.find('span', recursive=False).strings]
                tt_cha1 = vs[0]  # 行先など
                tt_cha2 = vs[1] if len(vs) > 1 else ''  # 列車名、路線名など

                timetable.append([tt_time, tt_cha1, tt_cha2, href])

    return timetable, message1, message2

def get_runtable_zairaisen(soup, heading2_h2):
    ''' 運行表データ取得 在来線 '''

    ptn_heading2_h2 = re.compile(r'^(.+)：(.+)の運行表$')
    ptn_h_big_h3 = re.compile(r'：\s*(.+方面)$')
    ptn_time = re.compile(r'^(\d{1,2}:\d{1,2})(発|着)$')

    messages = []

    # 路線名、行き先、方面取り出し
    heading2_h2 = heading2_h2.text
    mob1 = ptn_heading2_h2.search(heading2_h2)
    if mob1:
        rt_line = mob1.group(1)
        rt_dest = mob1.group(2)
        h_big_h3 = soup.find(id='to0').h3.b.string
        mob2 = ptn_h_big_h3.search(h_big_h3)
        if mob2:
            rt_direc = mob2.group(1)
        else:
            messages.append('warn h_big format : ' + h_big_h3)
            rt_direc = ''
    else:
        messages.append('warn heading2 format : ' + heading2_h2)
        rt_line, rt_dest, rt_direc = '', '', ''

    # 表データ取り出し
    tbl = soup.find('table', {'class': 'tbl_rosen_eki'})
    tr_list = tbl.find_all('tr')  # 各行
    runtable = []
    for tr in tr_list:

        # いらない行
        if tr.get('class') and any(c in ['w', 's'] for c in tr.get('class')):
            continue

        station = tr.find('td', {'class': 'eki'}).text  # 駅
        time_cha = tr.find('td', {'class': 'time'}).text  # xx:xx発(or着)
        # 時刻と発着に分ける
        mob3 = ptn_time.search(time_cha)
        if not mob3:
            messages.append('{0} time_char: {1}. not get time.'.format(station, time_cha))
            time = ''
            ad = ''
        else:
            time = mob3.group(1)  # xx:xx （時刻）
            ad = mob3.group(2)  # 発or着

        runtable.append([station, time, ad])

    return rt_line, rt_dest, rt_direc, runtable, messages

def get_runtable_shinkansen(soup, heading2_h1):
    ''' 運行表データ取得 新幹線 '''

    ptn_heading2_h1 = re.compile(r'^(.+)（(.+)）の運行表$')
    ptn_h_big_h2 = re.compile(r'^.*→(.*)$')
    ptn_time = re.compile(r'^(\d{1,2}:\d{1,2})(発|着)$')

    messages = []

    # 路線名、行き先、方面取り出し
    heading2_h1 = heading2_h1.text
    mob1 = ptn_heading2_h1.search(heading2_h1)
    if mob1:
        rt_line = mob1.group(1)
        rt_dest = mob1.group(2)
        h_big_h2 = soup.find(id='to0').h2.b.string
        mob2 = ptn_h_big_h2(h_big_h2)
        if mob2:
            rt_direc = mob2.group(1)
        else:
            messages.append('warn h_big h2 format : ' + h_big_h2)
            rt_direc = ''
    else:
        messages.append('warn heading2 h1 format : ' + heading2_h1)
        rt_line, rt_dest, rt_direc = '', '', ''

    # 表データ取り出し
    tbl = soup.find('table', {'class': 'tbl_unk_sin'})
    tr_list = tbl.find_all('tr')  # 各行
    runtable = []
    for tr in tr_list:

        # 最初の行 -> 列車名取得
        if tr.get('class') and 's' in tr.get('class'):
            vehicle_no = tr.find('th', {'class': 'g'}).text
            vehicle_no = vehicle_no.replace('\n', '')
            continue
        # 最後の行 -> 飛ばす
        if tr.get('class') and 'e' in tr.get('class'):
            continue

        station = tr.find('td', {'class': 'eki'}).text
        # xx:xx発(or着) <- 発着両方ある場合もある
        time_cha_list = [x for x in tr.find('td', {'class': 'time g'}).strings]
        # 時刻と発着に分ける
        for tc in time_cha_list:
            tc = tc.replace('\n', '')
            mob3 = ptn_time.search(tc)
            if mob3:
                time = mob3.group(1)  # xx:xx （時刻）
                ad = mob3.group(2)  # 発or着

                runtable.append([station, time, ad])
        
    return rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages

def get_runtable(href):
    '''
    運行表データ取得
    [return]
        runtable: [[駅, 時刻(hh:mm), 発or着], ....]
    '''

    url = 'https://www.jorudan.co.jp' + href
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser').find(id='left')

    messages = []
    
    try:
        heading2 = soup.find('div', {'class': 'heading2'})
        heading2_h1 = heading2.find('h1')  # 新幹線などはh1がある
        heading2_h2 = heading2.find('h2')  # 在来線はh2がある
    except:
        messages = ['get runtable err']
        return None, None, None, None, [], messages
    else:
        # 在来線、新幹線 分岐
        if heading2_h2:  # 在来線
            rt_line, rt_dest, rt_direc, runtable, messages \
                = get_runtable_zairaisen(soup, heading2_h2)
            vehicle_no = None
        elif heading2_h1:  # 新幹線
            rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages \
                = get_runtable_shinkansen(soup, heading2_h1)

    return rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages

def timetable2runtable(timetable):
    '''
    timetable データから、運行表リストを取得
    [args]
        timetable: [[時刻, tt文字列1, tt文字列2, 運行表href], ...]
    [return]
        runtableByVehicle:
            [[tt時刻, tt文字列1, tt文字列2, rt路線, rt行き先, rt方面, 列車no, runtable], ...]
        runtable (運行表): [[駅, 時刻, 発or着], ...]
    # tt~ : 運行表の取得元時刻表項目
    # rt~ : 運行表の項目
    '''

    messages_out = []

    runtableByVehicle = []

    if not timetable:
        messages_out = ['err timetable=None']
        return [], messages_out

    for vehi in timetable:
        tt_time, tt_cha1, tt_cha2, rt_href = vehi
        rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages = get_runtable(rt_href)

        if messages:
            messages_out += [', '.join([tt_time, rt_line, rt_dest, rt_direc, vehicle_no, x]) \
                             for x in messages]

        data = [tt_time, tt_cha1, tt_cha2, rt_line, rt_dest, rt_direc, vehicle_no, runtable]
        runtableByVehicle.append(data)

    return runtableByVehicle, messages_out

def staLineDirec_list2runtable(sta_line_direc_list, dw='1'):
    '''
    駅, 路線, 方面 のリストから、運行表を取得して重複を削除して返す
    [args]
        sta_line_direc_list: [(駅, [(路線, [tt方面, tt方面, ...]), ...]), 
                              (駅, [(路線, [tt方面, tt方面, ...]), ...]), ...]
    [return]
        runtableByVehicle_out:
            [[入力駅, 入力路線, tt方面, tt時刻, tt文字列1, tt文字列2, rt路線, rt行き先, rt方面, 列車no, runtable], ...]
        runtable (運行表): [[駅, 時刻, 発or着], ...]
        messages_out
    '''
    # 定数（runtableByVehicle のカラム位置）
    i_input_station, _, _, _, _, _, _, i_rt_dest, _, i_vehicle_no, i_runtable = range(11)

    runtableByVehicle_out, messages_out = [], []
    for station, line_direc_list in sta_line_direc_list:
        print('[{0}] {1}'.format(station, ctime()))  # 経過print
        for line, direc_list in line_direc_list:
            print(line, ctime())  # 経過print
            for tt_direc in direc_list:
                print(tt_direc, ctime())
                timetable, message1, message2 = staLineDirec2timetable(station, line, tt_direc, dw=dw)
                if message1:
                    #messages1 = []
                    messages_out.append('{0} {1} : {2}'.format(station, line, message1))
                if message2:
                    messages_out.append('{0} {1} {2} : {3}'.format(station, line, tt_direc, message2))
                runtableByVehicle, messages = timetable2runtable(timetable)
                if messages:
                    messages_out += ['{0} {1} {2}: {3}'.format(station, line, tt_direc, x) for x in messages]

                # 運行表ひとつずつ既存か判断、既存でなければ追加
                for rt_1vehi in runtableByVehicle:
                    _, _, _, _, rt_dest, _, vehicle_no, runtable = rt_1vehi

                    # 新幹線などの場合(列車noがある)
                    if vehicle_no:
                        # 同じ列車noで運行表が長い方を生かす。短いほうは捨てる
                        vehicle_no_list = [x[i_vehicle_no] for x in runtableByVehicle_out]
                        if vehicle_no in vehicle_no_list:
                            runtable_old = runtableByVehicle_out[vehicle_no_list.index(vehicle_no)][i_runtable]
                            if len(runtable) > len(runtable_old):
                                runtableByVehicle_out.pop(vehicle_no_list.index(vehicle_no))
                                runtableByVehicle_out.append([station, line, tt_direc] + rt_1vehi)
                        # 新しい列車noは追加
                        else:
                            runtableByVehicle_out.append([station, line, tt_direc] + rt_1vehi)

                    # 在来線などの場合(列車noがない)
                    else:
                        # rt_dest, runtable で同一列車を判断
                        zairai_comp = [[x[i_rt_dest], x[i_runtable]] for x in runtableByVehicle_out]
                        if [rt_dest, runtable] in zairai_comp:
                            # 入力駅が早い方を生かす。
                            # (遅い方には快速などの情報が無い場合がある)
                            idx = zairai_comp.index([rt_dest, runtable])
                            station_old = runtableByVehicle_out[idx][i_input_station]
                            rt_stations = [x[0] for x in runtableByVehicle_out[idx][i_runtable]]
                            if rt_stations.index(station) < rt_stations.index(station_old):
                                runtableByVehicle_out[idx] = [station, line, tt_direc] + rt_1vehi
                        else:
                            runtableByVehicle_out.append([station, line, tt_direc] + rt_1vehi)

    return runtableByVehicle_out, messages_out

