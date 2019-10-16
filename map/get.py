# coding: utf-8
'''
Created on Wed Oct 16 16:11:54 2019

@author: otani
'''

from address2coordinates import get_lat_lon_from_address

if __name__ == '__main__':

    addresses = ['国分寺駅', '東京都国立市中区３－１', '新座市道場2-1-10', '埼玉大学']

    coords = get_lat_lon_from_address(addresses)

    print(coords)

