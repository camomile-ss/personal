# coding: utf-8
'''
検証用
ジョルダン乗換案内 経路探索＆結果保存スクリプト
'''
import sys
import csv
import os
import re
import argparse
from datetime import datetime, time, timedelta
import requests
from bs4 import BeautifulSoup
import pickle
import json
sys.path.append('../common')
from proxy_conf import set_proxy_r

def conv_st(station):
    conv = {x[0]: x[1] for x in csv.reader(open('./conf/station_conv_jordan.csv', 'r', encoding='utf-8'))}
    if station in conv:
        return(conv[station])
    else:
        return(station)

def route_search(sta1, sta2, dttm):
    '''
    sta1: 入場駅, sta2: 降車駅, dttm: 入場日時（検索指定日+入場時刻）
    '''

    # 検索指定時刻は1分後
    dttm += timedelta(minutes=1)
    
    # url編集
    url = "https://www.jorudan.co.jp/norikae/cgi/nori.cgi"
    payload = {'eki1':sta1, 'eki2':sta2, 'Dym':'{0:04}{1:02}'.format(dttm.year, dttm.month), 'Ddd':str(dttm.day),
              'Dhh':str(dttm.hour), 'Dmn1':str(dttm.minute//10), 'Dmn2':str(dttm.minute%10), 'S':'検索'}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # ルート探索
    try:
        # 変換ファイルで駅名を変換
        payload['eki1'] = conv_st(sta1)
        payload['eki2'] = conv_st(sta2)
        r = requests.get(url, params=payload, headers=headers)
    except:
        return
    
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup
    
def get_cond_and_results(body):

    try:
        # 条件（出発地-到着地、日時）
        cond1 = body.find("h2", {'class': 'time'})
        cond2 = body.find('h3')
        cond = cond1.string.strip() + ' ' + cond2.em.string.strip()
        
        # 経路
        result_devs = body.find_all('div', {'class': 'bk_result'})
    except:
        return None, None

    return cond, result_devs

def ret_name(n):
    '''
    n(soup)のclassがeki   -> 駅名
                    rosen -> 路線名
    を返す。。。
    '''

    if 'eki' in n.attrs['class']:
        return(n.find('td', {'class': 'nm'}).text.strip())
    elif 'rosen' in n.attrs['class']:
        nm = n.find('td', {'class': 'rn'}).find('div').string.strip()
        # 高速バスはわかりにくいので[高速バス]と表示
        if n.find('td', {'class': 'gf'}).find('img').attrs['alt']=='高速バス':
            return('[高速バス]' + nm)
        else:    
            return(nm)
    else:
        print('err: class=', n.attrs['class'], file=sys.stderr)
        sys.exit()

def char_to_time(char):
    ''' 時間間隔の文字を分単位の数値に '''
    mob = re.search(r'^((\d+)時間)?(\d+)分$', char)
    if mob:
        if mob.group(1):
            seconds = timedelta(hours=int(mob.group(2)), minutes=int(mob.group(3))).seconds
        else:
            seconds = timedelta(minutes=int(mob.group(3))).seconds
        return int(seconds / 60)  # 分にして返す

def edit_1route(res):
    '''
    1経路を編集
        res:  <div class="bk_result">~</div>
    '''
    # 経路no
    route_no = res.find('div', {'class': 'header'}).h5.string.strip()  # 経路 x

    # xx:xx発 → xx:xx着
    div_data = res.find('div', {'class': 'data'})
    depart_arrival = div_data.find('div', {'class':'data_line_1'}).find('div', {'class':'data_tm'}).text.strip()
    mob = re.search(r'.*\(?(\d{2}):(\d{2})\)?発 → .*\(?(\d{2}):(\d{2})\)?△?着', depart_arrival)
    if mob:
        # 発時刻、着時刻
        depart_time = time(int(mob.group(1)), int(mob.group(2)), 0)
        arrival_time = time(int(mob.group(3)), int(mob.group(4)), 0)
    else:
        print('発時刻・着時刻 分離不可')
        depart_time, arrival_time = None, None

    # 各駅・路線
    div_route = res.find('div', {'class': 'route'})
    nodes = div_route.find_all('tr', {'class': ['eki', 'rosen']})
    node_names = [ret_name(n) for n in nodes]  # [駅,路線,駅,路線,駅]
    # 経路
    route = '-'.join(node_names)

    # 利用機関
    alts = [x.find('td', {'class': 'gf'}).find('img').attrs['alt'] for x in div_route.find_all('tr', {'class': 'rosen'})]
    alts = list(set(alts))  # 重複削除
    if len(alts)==1 and alts[0]=='ＪＲ':
        facility = 'JRのみ'
    else:
        alts_notJRE = [x for x in alts if x != 'ＪＲ']
        if len(alts_notJRE)==1 and alts[0]=='徒歩':
            facility = '徒歩'
        else:
            alts_notJREorWALK = sorted([x for x in alts_notJRE if x != '徒歩'])
            facility = ','.join(alts_notJREorWALK) + '利用'

    # 所要時間など
    interval_l = div_data.find_all('dl')
    ptn = re.compile(r'^(所要時間|乗車時間|乗換)')
    interval_d = {x.find('dt').text: x.find('dd').text for x in interval_l if ptn.match(x.find('dt').text)}

    if '所要時間' in interval_d:
        total_time = char_to_time(interval_d['所要時間'])
    else:
        total_time = '-'
    if '乗車時間' in interval_d:
        onboard_time = char_to_time(interval_d['乗車時間'])
    else:
        onboard_time = '-'
    if '乗換' in interval_d:
        transfer_times = int(re.search(r'^(\d+)回$', interval_d['乗換']).group(1))
    else:
        transfer_times = 0

    # 乗換時間等（乗換、ホーム、停車）
    trans_nodes = [node for node in nodes if 'eki' in node.attrs['class'] and not 'eki_s' in node.attrs['class'] and \
                   not 'eki_e' in node.attrs['class']]  # 途中駅の <tr class="eki">
    wait_chars = []
    wait_times = {}
    ptn2 = re.compile(r'^(乗換|ホーム|停車|待ち)((\d+)時間)?((\d+)分)?$')
    for n in trans_nodes:
        nm = n.find('td', {'class': 'nm'}).text.strip()  # 駅名
        tms = list(map(lambda x: x.strip(), n.find('td', {'class': 'tm'}).text.strip().split('\n')))  # ['乗換3分', 'ホーム46分']
        tms = [x for x in tms if x]  # nullは除く
        wait_times_sub = {}
        for tm in tms:
            if tm:  # 徒歩の場合などは何も書いてないので対象外
                mob = ptn2.match(tm)
                if mob:
                    hr = int(mob.group(3)) if mob.group(2) else 0
                    mn = int(mob.group(5)) if mob.group(4) else 0
                    wait_times_sub[mob.group(1)] = hr * 60 + mn
                else:
                    print(nm, "td class='tm' : 「乗換・ホーム・停車・待ち」以外 :", tm)
        if len(tms)>0:
            wait_chars.append('(' + nm + ')' + ','.join(tms))  # (上野)乗換3分,ホーム46分
            wait_times[nm] = wait_times_sub  # {'上野': {'乗換': 3, 'ホーム': 46}, ・・・}
    wait_char = ','.join(wait_chars)  # (上野)乗換3分,ホーム46分,(小山)乗換3分,ホーム1分,・・・

    return route_no, depart_time, arrival_time, route, facility, total_time, onboard_time, transfer_times, wait_char, wait_times

def mk_datetime(yr, mo, dy, time_char):
    ''' 時刻文字列（time_char）を日時に '''
    mob = re.search(r'^(\d{1,2}):(\d{2}):(\d{2})$', time_char)
    if mob:
        hr, mi, sc = int(mob.group(1)), int(mob.group(2)), int(mob.group(3))
        if hr > 23:  # 24時以降は翌日の0時以降に
            return datetime(yr, mo, dy, hr-24, mi, sc) + timedelta(days=1)
        else:
            return datetime(yr, mo, dy, hr, mi, sc)

def judge_mark(ent_datetime, tool_arr_datetime, arrival_time, facility):
    '''
    ng判断
        1: JRのみでツールより早く着 (ng)
        2: JRのみでツールと同時刻
        3: JRのみでツールよりあと
        
        4: 他機関利用でツールより早く着
        5: 他機関利用でツールと同時刻
        6: 他機関利用でツールよりあと
        
        7: 徒歩でツールより早く着
        8: 徒歩でツールと同時刻
        9: 徒歩でツールよりあと
    '''
    # 到着時刻を到着日時に
    arrival_datetime = datetime(year=ent_datetime.year, month=ent_datetime.month, day=ent_datetime.day, \
                                hour=arrival_time.hour, minute=arrival_time.minute, \
                                second=arrival_time.second)
    # 到着日時が入場日時より前だったら日付またいでるので1日プラス
    while True:
        if arrival_datetime > ent_datetime:
            break
        arrival_datetime += timedelta(days=1)
    # ツールの結果の降車日時が、ジョルダン探索結果の降車日時よりあとだったらng（ジョルダンは分単位なので秒除く）
    comp_tool_arr_datetime = datetime(tool_arr_datetime.year, tool_arr_datetime.month, tool_arr_datetime.day, \
                                      tool_arr_datetime.hour, tool_arr_datetime.minute, 0)
    if comp_tool_arr_datetime > arrival_datetime:
        if facility == 'JRのみ':
            return '1'
        elif facility == '徒歩':
            return '7'
        else:
            return '4'
    elif comp_tool_arr_datetime == arrival_datetime:
        if facility == 'JRのみ':
            return '2'
        elif facility == '徒歩':
            return '8'
        else:
            return '5'
    else:
        if facility == 'JRのみ':
            return '3'
        elif facility == '徒歩':
            return '9'
        else:
            return '6'

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infname')
    parser.add_argument('outdir')
    parser.add_argument('-s', help='pickle and json size', type=int, default=1000)
    args = parser.parse_args()
    
    infname = args.infname
    outdir = args.outdir
    f_size = args.s

    outfname = outdir + '/result.csv'
    ngfname = outdir + '/input_ng.csv'
    pickledir = outdir + '/pickle'
    jsondir = outdir + '/json'
    os.mkdir(pickledir)
    os.mkdir(jsondir)

    infreader = csv.reader(open(infname, 'r', encoding='utf-8'))    
    outfwriter = csv.writer(open(outfname, 'w', encoding='utf-8'), lineterminator='\n')
    ngfwriter = csv.writer(open(ngfname, 'w', encoding='utf-8'), lineterminator='\n')

    keys_jordan = ['route_no', 'depart_time', 'arrival_time', 'route', 'facility', 'total_time', 'onboard_time', 'transfer_times', 'wait_char', 'wait_times']

    # みだし
    header = next(infreader)
    ngfwriter.writerow(header)  # 未処理ファイルみだし=入力ファイルみだし
    outfwriter.writerow(['no', 'mark'] + header + keys_jordan)

    # proxy 設定
    if set_proxy_r() == 'err':
        print('[err] proxy ng', file=sys.stderr)
        sys.exit()

    # 検索日
    yr = 2018
    mo = 9
    dy = 6

    # pickle, json用 obj
    obj = []
    json_obj = []
    f_no = 0
    
    # 入力ファイル一行ずつ
    for i, row in enumerate(infreader):
        sta1 = row[0]
        sta2 = row[1]

        # 時刻 -> 日時
        enter_datetime = mk_datetime(yr, mo, dy, row[2])  # 入場日時
        tool_arr_datetime = mk_datetime(yr, mo, dy, row[4])  # ツールの結果の降車日時
        while True:  # 降車日時が入場日時より前だったら日付またいでるので翌日に
            if tool_arr_datetime > enter_datetime:
                break
            tool_arr_datetime += timedelta(days=1)
        #tm = datetime.strptime(row[2], '%H:%M:%S')  # 入場時刻
        #tool_o_tm = datetime.strptime(row[4], '%H:%M:%S')  # ツールの結果の降車時刻

        # ジョルダン探索
        soup = route_search(sta1, sta2, enter_datetime)
        if not soup:
            print('err: route_search.', sta1, sta2, enter_datetime, file=sys.stderr)
            ngfwriter.writerow(row)
            continue

        # 結果取り出し
        left_body = soup.find('div', {'id': 'left'})

        # 検索条件編集、結果div受け取り
        cond, result_divs = get_cond_and_results(left_body)        
        if not cond:
            print('err: get_cond_and_results.', sta1, sta2, enter_datetime, file=sys.stderr)
            ngfwriter.writerow(row)
            continue

        print(len(result_divs), '件 :', cond)

        # pickle, json用 obj
        obj_jordan_list = []
        json_obj_jordan_list = []

        # 探索結果1経路ごとに
        for res in result_divs:
            # 項目取り出し
            #route_no, depart_time, arrival_time, route, facility, total_time, onboard_time, transfer_times, wait_char, wait_times = edit_1route(res)
            datas_jordan = edit_1route(res)

            obj_jordan = {x: y for x, y in zip(keys_jordan, datas_jordan)}
            
            # ng判断
            obj_jordan['mark'] = judge_mark(enter_datetime, tool_arr_datetime, obj_jordan['arrival_time'], obj_jordan['facility'])

            # テキストファイル出力
            outfwriter.writerow([i, obj_jordan['mark']] + row + [obj_jordan[x] for x in keys_jordan])
            
            # pickle, json用 obj
            obj_jordan_list.append(obj_jordan)
            # json用に時刻を文字列に
            json_obj_jordan = {x: y for x, y in obj_jordan.items()}
            json_obj_jordan['depart_time'] = json_obj_jordan['depart_time'].strftime('%H:%M:%S')
            json_obj_jordan['arrival_time'] = json_obj_jordan['arrival_time'].strftime('%H:%M:%S')
            json_obj_jordan_list.append(json_obj_jordan)

        # pickle, json用 obj
        obj.append({'no': i, 'input_and_tool_result': {x: y for x, y in zip(header, row)}, 'jordan_result': obj_jordan_list})
        json_obj.append({'no': i, 'input_and_tool_result': {x: y for x, y in zip(header, row)}, 'jordan_result': json_obj_jordan_list})

        # f_sizeごとに pickle, json 書き出し
        if (i+1) % f_size == 0:
            jsonfname = jsondir + '/res{:04}.json'.format(f_no)            
            picklefname = pickledir + '/res{:04}.pickle'.format(f_no)            
            with open(jsonfname, 'w', encoding='utf-8') as jsonf:
                json.dump(json_obj, jsonf, ensure_ascii=False, indent=2)
            with open(picklefname, 'wb') as picklef:
                pickle.dump(obj, picklef)
            obj = []
            json_obj = []
            f_no += 1

    if len(obj) != 0:
        # さいごの pickle, json 書き出し
        jsonfname = jsondir + '/res{:04}.json'.format(f_no)            
        picklefname = pickledir + '/res{:04}.pickle'.format(f_no)            
        with open(jsonfname, 'w', encoding='utf-8') as jsonf:
            json.dump(json_obj, jsonf, ensure_ascii=False, indent=2)
        with open(picklefname, 'wb') as picklef:
            pickle.dump(obj, picklef)
