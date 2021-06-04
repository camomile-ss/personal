#!/usr/bin/python
# coding: utf-8
'''
latlon2distance :     緯度経度から直線距離・方位角を求める
get_distance_matrix : google API で移動距離・時間を求める

'''
import numpy as np
import googlemaps

def latlon2distance(lat1, lon1, lat2, lon2, delta=1e-12, max_loop=100, confirm=False):
    '''
    緯度経度から距離・方位角を求める
        参考
            Vincenty法 - Wikipedia
            https://ja.wikipedia.org/wiki/Vincenty%E6%B3%95
            日本の測地系 | 国土地理院
            https://www.gsi.go.jp/sokuchikijun/datum-main.html#p5
            測量計算(距離と方位角の計算)
            https://vldb.gsi.go.jp/sokuchi/surveycalc/surveycalc/bl2stf.html
        距離は m 、方位角は radian
    '''

    # 2点が同じ
    if abs(lat1 - lat2) < delta and abs(lon1 - lon2) < delta:
        return 0, 0, 0

    # 定数
    # GRS80地球楕円体
    a = 6378137  # 長半径（赤道半径）
    f = 1 / 298.257222101  # 扁平率
    b = (1 - f) * a  # 短軸半径（極半径）

    phi1 = np.deg2rad(lat1)  # 緯度 φ1, φ2
    phi2 = np.deg2rad(lat2)
    L1 = np.deg2rad(lon1)  # 経度
    L2 = np.deg2rad(lon2)

    U1 = np.arctan((1 - f) * np.tan(phi1))  # 更成緯度（補助球上の緯度）
    U2 = np.arctan((1 - f) * np.tan(phi2))

    L = L1 - L2  # 2点間の経度差

    '''
    alpha1, alpha2  # 各点における方位角
    s  # 2点間の楕円体上の距離
    sigma  # 補助球上の弧の長さ
    '''

    # λをλ=Lで初期化し、以下の計算をλが収束するまで反復する
    lamb = L
    sin_U1, sin_U2, cos_U1, cos_U2 = np.sin(U1), np.sin(U2), np.cos(U1), np.cos(U2)
    for i in range(max_loop):

        sin_lamb, cos_lamb = np.sin(lamb), np.cos(lamb)
        sin_sigma = np.sqrt((cos_U2 * sin_lamb) ** 2 \
                            + (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lamb) ** 2)
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lamb
        sigma = np.arctan(sin_sigma / cos_sigma)
        sin_alpha = cos_U1 * cos_U2 * sin_lamb / sin_sigma
        cos_2_alpha = 1 - sin_alpha ** 2
        cos_2sigmam = cos_sigma - 2 * sin_U1 * sin_U2 / cos_2_alpha
        C = f / 16 * cos_2_alpha * (4 + f * (4 - 3 * cos_2_alpha))
        lamb_prev = lamb
        lamb = L + (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * (cos_2sigmam \
                   + C * cos_sigma * (-1 + 2 * cos_2sigmam ** 2)))

        if abs(lamb - lamb_prev) < delta:
            break

    if confirm:
        print('loop: {0}/{1}'.format(i, max_loop))

    u_2 = cos_2_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + u_2 / 16384 * (4096 + u_2 * (-768 + u_2 * (320 - 175 * u_2)))
    B = u_2 / 1024 * (256 + u_2 * (-128 + u_2 * (74 - 47 * u_2)))
    d_sigma = B * sin_sigma * (cos_2sigmam + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigmam ** 2)
              - B / 6 * cos_2sigmam * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigmam ** 2)))
    s = b * A * (sigma - d_sigma)
    alpha1 = np.arctan(cos_U2 * sin_lamb / (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lamb))
    alpha2 = np.arctan(cos_U1 * sin_lamb / (-sin_U1 * cos_U2 + cos_U1 * sin_U2 * cos_lamb))

    return s, alpha1, alpha2

def get_distance_matrix(origins, destinations, apikey, mode):
    '''
    google API
    移動時間・距離のmatrix
    [return]:
        {'destination_addresses': [住所(英語), ...],
         'origin_addresses': 同上,
         'rows': [{'elements': [{'distance': {'text': '0.6m', 'value': 603},
                                 'duration': {'text': '8 min', 'value': 455},
                                 'status': 'OK'},
                                {'distande': ...,
                                 'duration': ,,,,
                                 'status': 'OK'},
                                ... ]},
                  {'elements': ... }., ... ],
         'status': 'OK'}
    # len(result['rows'] = origin数, len(result['rows'][0]['elements']) = destination数)
    # origin_idx, destination_idx = i, j の要素へのアクセス: result['rows'][i]['elements'][j]
    '''
    gmaps = googlemaps.Client(key=apikey)
    return gmaps.distance_matrix(origins=origins, destinations=destinations, mode=mode)

def google_api_key():
    ''' api key を返す '''
    with open('../personal/apikey.txt', 'r') as keyf:
        return keyf.read().strip()

if __name__ == '__main__':

    '''
    apikey = google_api_key()

    origins = [(33.59600254704502, 130.41658222675323)]
    destinations = [(33.59735197662633, 130.41822373867032)]
    mode = 'walking'
    #print(get_distance_matrix(origins=origins, destinations=destinations, apikey=apikey, mode=mode))
    gmaps = googlemaps.Client(key=apikey)
    from datetime import datetime
    dt = datetime(2020, 8, 6, 12, 00, 00)
    print(dt)
    print(gmaps.distance_matrix(origins=origins, destinations=destinations, mode='transit', transit_mode='bus', departure_time=dt))
    # だめぽい。徒歩と同じ 
    '''   
    
    lat1, lon1, lat2, lon2 = 33.59735197662633, 130.41822373867032, 33.59956821250876, 130.4168826341629
    #lat1, lon1, lat2, lon2 = 33.5897319, 130.4185387, 33.8852305, 130.9878057

    s, alpha1, alpha2 = latlon2distance(lat1, lon1, lat2, lon2)

    print(s, np.rad2deg(alpha1), np.rad2deg(alpha2))

    