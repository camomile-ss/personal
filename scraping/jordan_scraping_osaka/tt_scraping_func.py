#!/usr/bin/python
# coding: utf-8
'''
ジョルダンから時刻表・運行表情報をもってくる
    1. tt_station2lines
    2. tt_stationline2timetable
    3-1. tt_get_runtable_zairaisen
    3-2. tt_get_runtable_shinkansen
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
        timetableByDirec: [[方面名, timetable], ...]
               timetable: [[時刻, tt文字列1, tt文字列2, 運行表ファイル名], ...]
        message
    # tt文字列1 e.g.) 飯能行【始発】
    # tt文字列2 e.g.) 西武池袋線, むさし1号(Laview)
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
    h_big_list = left.find_all('div', {'class': 'h_big'}, recursive=False)
    tt_direc_list = []
    for h_big in h_big_list:
        h = h_big.find('h2').find('b').text
        _, tt_direc = h.split('\n')
        tt_direc_list.append(tt_direc)

    # 時刻表全体を取得
    tables = left.find_all('table', {'class': 'timetable2'})

    # 結果がない
    if len(tables) == 0:
        message = 'err 時刻表ない'
        timetableByDirec = None 

    elif len(tables) != len(tt_direc_list):
        message = 'err 方面, 時刻表 数が相違'
        timetableByDirec = None

    else:
        # 時刻表の1行ごと
        timetableByDirec = []
        for tt_direc, table in zip(tt_direc_list, tables):
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
            timetableByDirec.append([tt_direc, timetable])

    return timetableByDirec, message

def tt_get_runtable_zairaisen(soup, heading2_h2):
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

def tt_get_runtable_shinkansen(soup, heading2_h1):
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

def tt_get_runtable(href):
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
    
    heading2 = soup.find('div', {'class': 'heading2'})
    heading2_h1 = heading2.find('h1')  # 新幹線などはh1がある
    heading2_h2 = heading2.find('h2')  # 在来線はh2がある
    # 在来線、新幹線 分岐
    if heading2_h2:  # 在来線
        rt_line, rt_dest, rt_direc, runtable, messages \
            = tt_get_runtable_zairaisen(soup, heading2_h2)
        vehicle_no = None
    elif heading2_h1:  # 新幹線
        rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages \
            = tt_get_runtable_shinkansen(soup, heading2_h1)

    return rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages

def tt_timetable2runtable(timetable):
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
    for vehi in timetable:
        tt_time, tt_cha1, tt_cha2, rt_href = vehi
        rt_line, rt_dest, rt_direc, vehicle_no, runtable, messages = tt_get_runtable(rt_href)

        if messages:
            messages_out += [', '.join([tt_time, rt_line, rt_dest, rt_direc, vehicle_no, x]) for x in messages]

        data = [tt_time, tt_cha1, tt_cha2, rt_line, rt_dest, rt_direc, vehicle_no, runtable]
        runtableByVehicle.append(data)

    return runtableByVehicle, messages_out

def tt_stationline2runtable(stationline_list):
    '''
    駅、路線のリストから、運行表を取得して重複を削除して返す
    [args]
        stationline_list: [(駅, 路線), (駅, 路線), ...]
    [return]
        runtableByVehicle_out:
            [[入力駅, 入力路線, tt方面, tt時刻, tt文字列1, tt文字列2, rt路線, rt行き先, rt方面, 列車no, runtable], ...]
        runtable (運行表): [[駅, 時刻, 発or着], ...]
        messages_out
    '''
    # 定数（runtableByVehicle のカラム位置）
    _, _, _, _, _, _, i_rt_line, i_rt_dest, i_rt_direc, i_vehicle_no, i_runtable = range(11)

    runtableByVehicle_out, messages_out = [], []
    for s, l in stationline_list:
        print('{0} {1}: {2}'.format(s, l, ctime()))  # 経過print
        # 駅・路線から時刻表取得
        timetableByDirec, message_1 = tt_stationline2timetable(s, l)
        if message_1:
            messages_out.append(', '.join([s, l, message_1]))
        # 方面ごとに
        for tt_bd in timetableByDirec:
            tt_direc, timetable = tt_bd
            print('{0}: {1}'.format(tt_direc, ctime()))  # 経過print
            # 各列車の運行表取得
            runtableByVehicle, messages_2 = tt_timetable2runtable(timetable)                
            if messages_2:
                messages_out += [', '.join([s, l, x]) for x in messages_2]

            # 運行表ひとつずつ既存か判断、既存でなければ追加
            for rt_1vehi in runtableByVehicle:
                _, _, _, rt_line, rt_dest, rt_direc, vehicle_no, runtable = rt_1vehi

                # 新幹線などの場合(列車noがある)
                if vehicle_no:
                    # 同じ列車noで運行表が長い方を生かす。短いほうは捨てる
                    vehicle_no_list = [x[i_vehicle_no] for x in runtableByVehicle_out]
                    if vehicle_no in vehicle_no_list:
                        runtable_old = runtableByVehicle_out[vehicle_no_list.index(vehicle_no)][i_runtable]
                        if len(runtable) > len(runtable_old):
                            runtableByVehicle_out.pop(vehicle_no_list.index(vehicle_no))
                            runtableByVehicle_out.append([s, l, tt_direc] + rt_1vehi)
                    # 新しい列車noは追加
                    else:
                        runtableByVehicle_out.append([s, l, tt_direc] + rt_1vehi)

                # 在来線などの場合(列車noがない)
                else:
                    # rt_dest, runtable で同一列車を判断
                    zairai_comp = [x[i_rt_dest], x[i_runtable]] for x in runtableByVehicle_out]
                    if [rt_dest, runtable] in zairai_comp:
                        continue
                    runtableByVehicle_out.append([s, l, tt_direc] + rt_1vehi)

    return runtableByVehicle_out, messages_out

if __name__ == '__main__':

    #psr = argparse.ArgumentParser()
    station = '金浜'
    lines, station_rep, message = tt_station2lines(station)
    print(lines)
    print(station_rep)
    print(message)

    '''
    #station, line = '仙台', '仙石線'
    station, line = '東京', '東海道・山陽新幹線'
    data, message = tt_stationline2timetable(station, line)
    tt1 = data[0][1]
    runtables, messages = tt_timetable2runtable(tt1)
    print(runtables)
    print(messages)
    '''
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
