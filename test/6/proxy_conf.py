# coding: utf-8
'''
proxy設定
'''
import os
import csv
from datetime import date
import requests

def set_proxy_r():
    ''' requestsモジュール用proxy設定 '''
    
    url = "https://www.jorudan.co.jp/norikae/cgi/nori.cgi"
    test_payload = {'eki1':'東京', 'eki2':'浦和', 'Dym':'{0:04}{1:02}'.format(date.today().year, date.today().month), 'Ddd':str(date.today().day),
              'Dhh':'12', 'Dmn1':'3', 'Dmn2':'0', 'S':'検索'}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        requests.get(url, params=test_payload, headers=headers)
    except:
        proxy_conf = {x[0]: x[1] for x in csv.reader(open('../common/files/proxy.conf', 'r', encoding='utf-8'), delimiter='\t')}
        #uid = input('proxy user >> ')
        #pwd = input('proxy password >> ')
        os.environ['https_proxy'] = "http://{0}:{1}@obprx01.intra.hitachi.co.jp:8080".format(proxy_conf['uid'], proxy_conf['pwd'])
        try:
            requests.get(url, params=test_payload, headers=headers)
        except:
            return 'err'
        else:
            return 'set from conf.'
    else:
        return 'ok'
