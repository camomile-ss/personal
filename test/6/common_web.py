# coding: utf-8
''' 共通 web '''

import requests

def requests_get(url, params=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, params=params)
    return r

def requests_post(url, data):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.post(url, headers=headers, data=data)
    return r

