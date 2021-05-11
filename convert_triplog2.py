#!/usr/bin/python
# coding: utf-8

import argparse
import sys
import os
from datetime import datetime
#import logging

def getdirn(indirn, outdirn):
    ''' dir指定なければscriptの場所を基準に決める '''
    scriptdirn = os.path.dirname(__file__)
    if not indirn:
        indirn = os.path.join(scriptdirn, '../input')
    if not outdirn:
        outdirn = os.path.join(scriptdirn, '../output')
    return indirn, outdirn

def detect_enc(fn):
    ''' ファイルの文字コードを判別 '''
    import cchardet
    enc = cchardet.detect(open(fn, 'rb').read())['encoding'].lower()
    enc = 'cp932' if enc=='shift_jis' else enc
    return enc

def read_f(fn, enc):
    ''' ファイルを読んでリストに '''
    with open(fn, 'r', encoding=enc) as f:
        data = f.readlines()
    return [[x.strip() for x in l.split('\t')] for l in data]

def read_rs(fn, enc):
    '''
    railstation.txt から 辞書作成
        st_cd2nm : 駅cd -> 駅名, st_nm2cd : 駅名 -> 駅cd
        ln_id2nm : 路線id -> 路線名, ln_nm2id : 路線名 -> 路線id
        railstation : 路線名 ->  駅cdのリスト 
    '''
    data = read_f(fn, enc)
    st_cd2nm = {x[6]: x[7] for x in data}
    st_nm2cd = {x[7]: x[6] for x in data}
    ln_id2nm = {x[0]: x[1] for x in data}
    ln_nm2id = {x[1]: x[0] for x in data}
    railstation = {ln: [x[6] for x in data if x[0]==ln] for ln in ln_id2nm.keys()}
    return st_cd2nm, st_nm2cd, ln_id2nm, ln_nm2id, railstation

def read_rf(fn, enc, st_nm2cd):
    '''
    railfare.txt から辞書作成
        (入場駅cd, 出場駅cd) -> 運賃
    '''
    data = read_f(fn, enc)
    data.pop(0)
    def name_adj(x):
        ''' railstation.txtと違う名前の調整 '''
        adj = {'なんば': '難波', 'なかもず': '中百舌鳥', ' あびこ': '我孫子'}
        if x in adj:
            return adj[x]
        else:
            return x
    data = [[name_adj(x[0]), name_adj(x[1]), x[2]] for x in data]
    data = [x for x in data if all(st in st_nm2cd for st in (x[0], x[1]))]
    return {(st_nm2cd[x[0]], st_nm2cd[x[1]]): int(x[2]) for x in data}

def read_rok(fn, enc, ln_nm2id, st_nm2cd):
    '''
    railopkm.txt から辞書作成
        (路線id, 駅cd, 駅cd) -> 営業キロ
    '''
    data = read_f(fn, enc)
    data.pop(0)
    data = [[x[0] + '_0'] + x[1:] for x in data] + [[x[0] + '_1'] + x[1:] for x in data]
    data = [x for x in data if x[0] in ln_nm2id and all(st in st_nm2cd for st in (x[1], x[2]))]
    data = {(ln_nm2id[x[0]], st_nm2cd[x[1]], st_nm2cd[x[2]]): float(x[3]) for x in data}
    # 反対向き無かったら作っておく
    data_keys = [x for x in data.keys()]
    for k in data_keys:
        lid, st1, st2 = k
        if not (lid, st2, st1) in data_keys:
            data[(lid, st2, st1)] = data[k]
    return data

def read_tra(fn, enc):
    '''
    trainlog.txt から辞書作成
        (路線id, 列車番号) -> {'order': [0, 1, ...], 'stations': 駅cdのリスト, 
                               'sec_arr': 着時刻のリスト, 'sec_dep': 発時刻のリスト,
                               'passn': 乗車人数のリスト}
    '''
    data = read_f(fn, enc)
    trains = set([(x[0], x[1]) for x in data])
    data = {tr: [x[3: 5] + x[6: 8] + [x[10]] for x in data if (x[0], x[1]) == tr] for tr in trains}
    return {tr: {'order': [int(x[0]) for x in sts], 'stations': [x[1] for x in sts], \
                 'sec_arr': [int(x[2]) for x in sts], 'sec_dep': [int(x[3]) for x in sts], \
                 'passn': [int(x[4]) for x in sts]} \
            for tr, sts in data.items()}

def chk(trip, sections, railstation, trainlog, railfare, railopkm, ln_id2nm, st_cd2nm):
    '''
    triplog.txt のチェック
    入出場時刻・運賃取得
    '''
    tripid, o_st, d_st, o_datetime, _, _, d_datetime, *_ = trip

    for i, s in enumerate(sections):
        trainno, lineid, dep_stcd, _, arr_stcd, *_ = s

        msg = [tripid, '区間{}'.format(i + 1), None, 'railstation.txtにない']
        if not lineid in railstation:
            msg[2] = '路線{}'.format(lineid)
            return 9, msg
        if not dep_stcd in railstation[lineid]:
            msg[2] = '路線{0} 駅{1}'.format(lineid, dep_stcd)
            return 9, msg
        if not arr_stcd in railstation[lineid]:
            msg[2] = '路線{0} 駅{1}'.format(lineid, arr_stcd)
            return 9, msg

        msg[3] = 'trainlog.txtにない'
        if not (lineid, trainno) in trainlog:
            msg[2] = '路線{0} 列車番号{1}'.format(lineid, trainno)
            return 9, msg
        if not dep_stcd in trainlog[(lineid, trainno)]['stations'][: -1]:
            msg[2] = '路線{0} 列車番号{1} 発駅{2}'.format(lineid, trainno, dep_stcd)
            return 9, msg
        if not arr_stcd in trainlog[(lineid, trainno)]['stations'][1: ]:
            msg[2] = '路線{0} 列車番号{1} 着駅{2}'.format(lineid, trainno, arr_stcd)
            return 9, msg

        if not (lineid, dep_stcd, arr_stcd) in railopkm and not (lineid, arr_stcd, dep_stcd) in railopkm:
            linenm = ln_id2nm(lineid)
            dep_stnm, arr_stnm = st_cd2nm(dep_stcd), st_cd2nm(arr_stcd)
            msg[2] = '{0} {1} {2}'.format(linenm, dep_stnm, arr_stnm)
            msg[3] = 'railopkm.txtにない'
            return 9, msg

    msg[1] = '-'
    msg[3] = 'railstation.txtにない'
    if not o_st in st_cd2nm:
        msg[2] = '入場駅{}'.format(o_st)
        return 9, msg
    if not d_st in st_cd2nm:
        msg[2] = '出場駅{}'.format(d_st)
        return 9, msg

    if (o_st, d_st) in railfare:
        fare = railfare[(o_st, d_st)]
    else:
        msg[2] = '入場駅{0} 出場駅{1}'.format(o_st, d_st)
        msg[3] = 'railfare.txtにない'
        return 9, msg

    msg[3] = '書式不整'
    def chk_datetime(dt_c):
        try:
            dt = datetime.strptime(dt_c, '%Y%m%d %H:%M:%S')
        except:
            return 9, None
        return 0, '{0}:{1:02}:{2:02}'.format(dt.hour, dt.minute, dt.second)        
    flg, o_time = chk_datetime(o_datetime)
    if flg == 9:
        msg[2] = '入場時刻 {}'.format(o_datetime)
        return 9, msg
    flg, d_time = chk_datetime(d_datetime)
    if flg == 9:
        msg[2] = '出場時刻 {}'.format(d_datetime)
        return 9, msg        

    values = (o_time, d_time, fare)

    if o_st != sections[0][2]:
        msg[2] = '入場駅{}'.format(o_st)
        msg[3] = '区間1の発駅 {} と不一致'.format(sections[0][2])
        return 1, msg, values
    if d_st != sections[-1][4]:
        msg[2] = '出場駅{}'.format(d_st)
        msg[3] = '最終区間の着駅 {} と不一致'.format(sections[-1][4])
        return 1, msg, values
    
    return 0, None, values

def sec2char(sec):
    ''' 秒を時刻の文字列に '''
    sc = sec % 60
    mn = (sec // 60) % 60
    hr = (sec // 3600) % 24
    return ('{0}:{1:02}:{2:02}'.format(hr, mn, sc))

def section_conv(s, trainlog, railopkm):
    ''' 区間を変換 '''
    trainno, lineid, dep_stcd, _, arr_stcd, *_ = s

    train = trainlog[(lineid, trainno)]

    dep_i = train['stations'].index(dep_stcd)
    arr_i = train['stations'].index(arr_stcd)

    # 乗降時刻
    sec_dep = train['sec_dep'][dep_i]
    sec_arr = train['sec_arr'][arr_i]
    od_time = '{0}-{1}'.format(sec2char(sec_dep), sec2char(sec_arr))

    # 区間情報
    secinfo = ';'.join(['-'.join([st, nst, str(pas)]) for st, nst, pas \
                        in zip(train['stations'][dep_i: arr_i], \
                               train['stations'][dep_i + 1: arr_i + 1], \
                               train['passn'][dep_i: arr_i])]) + ';'

    # 営業キロ
    opkm = railopkm[(lineid, dep_stcd, arr_stcd)]

    return [lineid, trainno, od_time, secinfo, str(opkm)]

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-i', '--inputdirname', default=None)
    psr.add_argument('-o', '--outputdirname', default=None)
    psr.add_argument('-d', '--detectenc', help='入力ファイルの文字コードを判別する場合 "y"', \
                     default='n', choices=['y', 'n'])
    args = psr.parse_args()
    indirn, outdirn = getdirn(args.inputdirname, args.outputdirname)
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # ファイルの文字コード
    fns = 'railstation.txt', 'triplog.txt', 'trainlog.txt', 'railfare.txt', 'railopkm.txt'
    encs = 'utf-8', 'ascii', 'utf-8-sig', 'cp932', 'cp932'
    fnfs = [os.path.join(indirn, fn) for fn in fns]
    if args.detectenc == 'y':
        encs = [detect_enc(fnf) for fnf in fnfs]
    rs_fnf, tri_fnf, tra_fnf, rf_fnf, rok_fnf = fnfs
    rs_enc, tri_enc, tra_enc, rf_enc, rok_enc = encs
    ofn, errfn = 'triplog2.txt', 'err.txt'
    ofnf = os.path.join(outdirn, ofn)
    errfnf = os.path.join(outdirn, errfn)

    # railstation.txt
    st_cd2nm, st_nm2cd, ln_id2nm, ln_nm2id, railstation = read_rs(rs_fnf, rs_enc)

    # railfare.txt
    railfare = read_rf(rf_fnf, rf_enc, st_nm2cd)

    # railopkm.txt
    railopkm = read_rok(rok_fnf, rok_enc, ln_nm2id, st_nm2cd)

    # trainlog.txt
    trainlog = read_tra(tra_fnf, tra_enc)

    # 変換
    err_out = []
    with open(tri_fnf, 'r', encoding=tri_enc) as inf, open(ofnf, 'w') as outf:

        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            trip, sections = l[: 9], l[9:]
            tripid, o_st, d_st, o_datetime, _, num, d_datetime, *_ = trip
            sections = [sections[i: i + 8] for i in range(0, len(sections), 8)]

            result = chk(trip, sections, railstation, trainlog, railfare, railopkm, ln_id2nm, st_cd2nm)

            if result[0] != 0:
                err_out.append(result[1])
                if result[0] == 9:
                    continue
            
            o_time, d_time, fare = result[2]

            outline = [tripid, o_st, d_st, o_time, d_time, str(num), str(fare), '0', '0', '0']

            for s in sections:
                outline += section_conv(s, trainlog, railopkm)

            outf.write('\t'.join(outline) + '\n')

    # errあれば出力
    if err_out:
        with open(errfnf, 'w') as errf:
            errf.write('\t'.join(['ID', '区間番号', 'エラー値', '内容']) + '\n')
            errf.write(''.join(['\t'.join(l) + '\n' for l in err_out]))
