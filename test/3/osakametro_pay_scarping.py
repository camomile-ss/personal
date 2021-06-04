#!/usr/bin/python
# coding: utf-8
'''
大阪メトロ 各ODの最安運賃取得スクリプト
'''
import argparse
import os
import urllib
import requests
import sys
from bs4 import BeautifulSoup
import re
from datetime import date
from time import ctime

def get_kensaku_result(ostation, dstation, via=None, dt=date.today(), num=5):
    '''
    経路検索結果のhtml soupを返す
    [args]
        ostation, dstation, via : 出発駅、到着駅、経由駅
        dt : 検索日付
        num: requestsがうまくいかない時のretry数
    '''
    ostation_q = urllib.parse.quote(ostation)
    dstation_q = urllib.parse.quote(dstation)
    if via:
        via_q = urllib.parse.quote(via)
    else:
        via_q = ''
    yyyymm = '{0:04}{1:02}'.format(dt.year, dt.month)
    dd = '{:02}'.format(dt.day)
    url = 'https://kensaku.osakametro.co.jp/route/web/dia/result'
    params = {'val_from': ostation_q, 'get_val_from': '', 'val_to': dstation_q, 'get_val_to': '', \
              'val_via': via_q, 'get_val_via': '', \
              'val_yyyymm': yyyymm, 'val_dd': dd, 'val_hh': '09', 'val_mm': '00', \
              'exp_type': 'departure', 'search_target': 'subway', 'currentBox': '3'}
    params = '&'.join(['='.join([k, v]) for k, v in params.items()])
    url = url + '?' + params

    headers = {'User-Agent': 'Mozilla/5.0'}
    for i in range(num):
        try:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
        except:
            print('[retry]', ostation, dstation, i)
            continue
            #message = 'request or soup err'
            #return [], '', message
        else:
            return soup

    print('[get_kensaku err')
    return None

def get_min_pay_route(ostation, dstation, via=None, dt=date.today()):
    '''
    ODペア・経由駅で、経路・運賃検索
    徒歩で他駅へ乗換ている経路を排除して、最安の運賃を求める。
    (「徒歩(同駅)」は排除しない。)
    '''
    result = get_kensaku_result(ostation, dstation, via=via, dt=dt)
    # 結果がない
    if not result:
        print(ostation, dstation, '検索失敗')
        print('異常終了')
        sys.exit()

    # 表示される候補を取得
    try:
        sections = result.find('div', {'class': 'rightbox'}).find_all('table', {'class': 'pi_keiro'})
    except:
        print('sections 取得失敗')
        return None

    # 徒歩(同駅) 以外の 徒歩除く
    ptn = re.compile(r'徒歩((\(同駅\)|:))?')
    sections_notwalk = []
    for section in sections:
        ng_section = False
        trs = section.find_all('tr')
        for tr in trs:
            mob = ptn.search(tr.text)
            if mob and not mob.group(1):
                ng_section = True
                break
        if ng_section:
            continue
        sections_notwalk.append(section)

    # sectionが残ってるか
    if sections_notwalk:
        pay_texts = [x.find('th', {'class': 'keiro'}).text for x in sections_notwalk]
        ptn_pay = re.compile(r'(\d+)円')
        # 運賃リスト
        pay_list = [int(ptn_pay.search(x).group(1)) for x in pay_texts if ptn_pay.search(x)]
        if pay_list:
            return min(pay_list)

    return None

def get_min_pay_od(ostation, dstation, dt, stations):
    '''
    ODペアの最安運賃を求める。
    '''
    # 発駅、着駅で検索
    min_pay = get_min_pay_route(ostation, dstation, dt=dt)

    # 結果がなければ、経由駅を変えながら最小運賃を探す
    if min_pay is None:
        min_pay = 999999
        for via in stations:
            if via in (ostation, dstation):
                continue
            min_pay_kouho = get_min_pay_route(ostation, dstation, via=via, dt=dt)
            if min_pay_kouho is None:
                continue
            min_pay = min(min_pay, min_pay_kouho)
    
    return min_pay

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-f', '--fn', help='station_master.txt, testデータのとき指定。', default=None)
    psr.add_argument('-s', '--sfx', help='出力ファイルのsuffix', default=None)
    psr.add_argument('-d', '--kdate', help='検索日付。過去だとエラーになる。指定しなければ今日になる。', \
                     default=None)
    args = psr.parse_args()
    fn = args.fn
    sfx = args.sfx
    kdate = args.kdate
    if kdate:
        dt = date(int(kdate[:4]), int(kdate[4:6]), int(kdate[6:]))
    else:
        dt = date.today()

    # 駅リスト
    if not fn:
        rfn = '../../data/20191202_大阪メトロ/自動化ツール用データ/all_master/station_master.txt'
        fn = os.path.join(os.path.dirname(__file__), rfn)
    with open(fn, 'r', encoding='utf-8') as f:
        _ = next(f)
        stations = [[x.strip() for x in l.split('\t')] for l in f.readlines()]
    stations = [l[4] for l in stations]

    # 出力ファイル
    if sfx:
        m_fn = 'message_{}.txt'.format(sfx)
        o_fn = 'od_pay_{}.txt'.format(sfx)
    else:
        m_fn = 'message.txt'
        o_fn = 'od_pay.txt'

    # 各odの運賃検索
    n = len(stations)
    min_pays = {}  # 往復同じかチェック用

    with open(m_fn, 'w', encoding='utf-8') as mf, open(o_fn, 'w', encoding='utf-8') as of:
        mf.write('\t'.join(['出発駅', '到着駅', 'warn or err']) + '\n')
        of.write('\t'.join(['出発駅', '到着駅', '運賃']) + '\n')

        #for i in range(0, n-1):  # 片道だけ調べる用
        #    for j in range(i+1, n):
        for i in range(n):  # 往復別に調べる用
            for j in list(range(0, i)) + list(range(i+1, n)):
                ostation = stations[i]
                dstation = stations[j]
                print(i, ostation, j, dstation, ctime())

                # 運賃調べる
                min_pay = get_min_pay_od(ostation, dstation, dt, stations)
                if min_pay == 999999:
                    mf.write('\t'.join([ostation, dstation, '徒歩のない経路無し']) + '\n')

                # 往復で違う
                if (dstation, ostation) in min_pays:
                    if min_pay != min_pays[(dstation, ostation)]:
                        mf.write('\t'.join([ostation, dstation, '逆向きと違う運賃']) + '\n')

                min_pays[(ostation, dstation)] = min_pay

                # 出力
                of.write('\t'.join([ostation, dstation, str(min_pay)]) + '\n')

