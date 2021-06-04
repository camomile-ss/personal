#!usr/bin/python
# coding: utf-8

'''
大阪メトロ 営業キロ取得スクリプト
'''
import argparse
import os
import logging
import urllib
import requests
import sys
from bs4 import BeautifulSoup
import re
from datetime import date
from time import ctime

def get_page_soup(url, param, num=5):

    url = url + '?' + param

    headers = {'User-Agent': 'Mozilla/5.0'}
    for i in range(num):
        try:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'html.parser')
        except:
            print('[retry]', param, i)
            continue
        else:
            return soup

    print('[get_page_soup err')
    return None

def ext_data(soup):  #, rail_ptn):

    date_ptn = re.compile(r'(\d{4})\/(\d{2})(\/(\d{2}))?')
    dist_ptn = re.compile(r'(\d+(\.\d+)?)km')

    rec_list = soup.find('div', {'class': 'content'}).find('ul', {'class': 'record-list'}) \
               .find_all('li', {'class': 'record-list__item'})
    #content = soup.find('div', {'id': 'mm-wrap'}).find_all('div', {'class': 'content'})   # 'container-fluid'})

    pagedata = []
    for i, rec in enumerate(rec_list):
        rec = rec.find('div', {'class': 'rail-list__outer'})
        st_divs = rec.find_all('div', {'class': 'rail-list__station'})
        rail_divs = rec.find_all('div', {'class': 'rail-list__rail'})

        stations = [x.text.strip() for x in st_divs]

        rail_text = rail_divs[0].text
        mob = date_ptn.search(rail_text)
        if mob:
            if mob.group(3):
                dateo = date(int(mob.group(1)), int(mob.group(2)), int(mob.group(4)))
            else:
                dateo = date(int(mob.group(1)), int(mob.group(2)), 1)
        else:
            logging.warning('日付取得エラー {} {} {}'.format(stations[0], stations[1], i))
            dateo = None
        mob = dist_ptn.search(rail_text)
        if mob:
            distance = float(mob.group(1))
        else:
            logging.warning('営業キロ取得エラー {} {} {}'.format(stations[0], stations[1], i))
            distance = None

        recdata = stations + [distance, dateo] + [len(st_divs), len(rail_divs)]
        pagedata.append(recdata)

    return pagedata

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-c', '--conffn', help='testデータのとき指定。', default='tetsureko_input.txt')
    psr.add_argument('-o', '--outfn', default='tetsureko_output.txt')
    args = psr.parse_args()
    conffn = args.conffn
    outfn = args.outfn

    logger = logging.getLogger()
    logging.basicConfig()   # level=logging.DEBUG)

    #rail_ptn = re.compile(r'(\d{4}\/\d{2}\/\d{2})[\s\S]*(\d+(\.\d+)?)km')

    with open(conffn, 'r', encoding='utf-8') as f:
        _ = next(f)
        indata = [[x.strip() for x in l.split('\t')] for l in f]

    with open(outfn, 'w', encoding='utf-8') as f:
        f.write('\t'.join(['路線名', '出発', '到着', '営業キロ', '日付', 'chk1(2)', 'chk2(1)']) + '\n')

        for linename, urlno, pagenum in indata:

            print('[{}]'.format(linename))
            url='https://raillab.jp/service/' + urlno + '/records/list'

            for pageid in range(1, int(pagenum)+1):

                print('[{}]'.format(pageid))
                param = 'pageid={}'.format(pageid)

                soup = get_page_soup(url, param)

                outdata = [[linename] + x for x in ext_data(soup)]  #, rail_ptn)

                f.write(''.join(['\t'.join([str(x) for x in l]) + '\n' for l in outdata]))
