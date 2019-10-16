# coding: utf-8
'''
Created on Wed Oct 16 16:07:45 2019

@author: otani
'''

import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm


def get_lat_lon_from_address(address_l):
    """
    address_lにlistの形で住所を入れてあげると、latlonsという入れ子上のリストで緯度経度のリストを返す関数。
    >>>>get_lat_lon_from_address(['東京都文京区本郷7-3-1','東京都文京区湯島３丁目３０−１'])
    [['35.712056', '139.762775'], ['35.707771', '139.768205']]
    """
    url = 'http://www.geocoding.jp/api/'
    latlons = []
    for address in tqdm(address_l):
        payload = {"v": 1.1, 'q': address}
        r = requests.get(url, params=payload)
        ret = BeautifulSoup(r.content,'lxml')
        if ret.find('error'):
            raise ValueError(f"Invalid address submitted. {address}")
        else:
            lat = ret.find('lat').string
            lon = ret.find('lng').string
            latlons.append([lat,lon])
            time.sleep(10)
    return latlons
