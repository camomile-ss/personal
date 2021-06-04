#!/usr/bin/python
# coding: utf-8
''' triplogの形式変換 '''
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

class RailStation:
    '''
    railstation.txt から 辞書作成
        st_cd2nm : 駅cd -> 駅名, st_nm2cd : 駅名 -> 駅cd
        ln_id2nm : 路線id -> 路線名, ln_nm2id : 路線名 -> 路線id
        railstation : 路線id -> 駅cdのリスト
    '''
    def __init__(self, fn, enc):
        data = read_f(fn, enc)
        self.st_cd2nm = {x[6]: x[7] for x in data}
        self.st_nm2cd = {x[7]: x[6] for x in data}
        self.ln_id2nm = {x[0]: x[1] for x in data}
        self.ln_nm2id = {x[1]: x[0] for x in data}
<<<<<<< HEAD
        self.railstation = {ln: [x[6] for x in data if x[0]==ln] for ln in self.ln_id2nm.keys()}
=======
        self.railstation = {ln: [x[6] for x in data if x[0]==ln] \
                            for ln in self.ln_id2nm.keys()}
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77

class RailFare:
    ''' (入場駅cd, 出場駅cd) -> 運賃 '''
    def __init__(self, fn, enc, railstation):
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
<<<<<<< HEAD
        data = [x for x in data if all(st in railstation.st_nm2cd for st in (x[0], x[1]))]
        self.railfare = {(railstation.st_nm2cd[x[0]], railstation.st_nm2cd[x[1]]): int(x[2]) \
                         for x in data}

    def get_railfare(self, o_stcd, d_stcd):
        if (o_stcd, d_stcd) in self.railfare:
            return self.railfare[(o_stcd, d_stcd)]
        if (d_stcd, o_stcd) in self.railfare:
            return self.railfare[(d_stcd, o_stcd)]
=======
        data = [x for x in data \
                if all(st in railstation.st_nm2cd for st in (x[0], x[1]))]
        self.railfare = {(railstation.st_nm2cd[x[0]], railstation.st_nm2cd[x[1]]) \
                         : int(x[2]) for x in data}

    def get_railfare(self, o_stcd, d_stcd):
        for k in [(o_stcd, d_stcd), (d_stcd, o_stcd)]:
            if k in self.railfare:
                return self.railfare[k]
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
        return

class RailOpKm:
    ''' (路線id, 発駅cd, 着駅cd) -> 営業キロ '''
    def __init__(self, fn, enc, railstation):
        data = read_f(fn, enc)
        data.pop(0)
<<<<<<< HEAD
        data = [[x[0] + '_0'] + x[1:] for x in data] + [[x[0] + '_1'] + x[1:] for x in data]
        data = [x for x in data if x[0] in railstation.ln_nm2id \
                                and all(st in railstation.st_nm2cd for st in (x[1], x[2]))]
=======
        data = [[x[0] + '_0'] + x[1:] for x in data] \
             + [[x[0] + '_1'] + x[1:] for x in data]
        data = [x for x in data \
                if x[0] in railstation.ln_nm2id \
                and all(st in railstation.st_nm2cd for st in (x[1], x[2]))]
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
        self.railopkm = {(railstation.ln_nm2id[x[0]], railstation.st_nm2cd[x[1]], \
                          railstation.st_nm2cd[x[2]]): float(x[3]) for x in data}

    def get_railopkm(self, lineid, dep_stcd, arr_stcd):
        for k in [(lineid, dep_stcd, arr_stcd), (lineid, arr_stcd, dep_stcd)]:
            if k in self.railopkm:
                return self.railopkm[k]
        return

class Train:
    ''' 列車 '''
    def __init__(self, trainno, trdata):
        self.trainno = trainno  # 列車番号
        self.lineid = trdata[0][0]  # 路線id
        self.order = [int(x[3]) for x in trdata]  # 連番
        self.stations = [x[4] for x in trdata]  # 駅cd
        self.arr_sec = [int(x[6]) for x in trdata]  # 着時刻秒
        self.dep_sec = [int(x[7]) for x in trdata]  # 発時刻秒
        self.pass_num = [int(x[10]) for x in trdata]  # 乗車人数

class TrainLog:
    def __init__(self, fn, enc):
        data = read_f(fn, enc)
<<<<<<< HEAD
        trainnos = set([x[1] for x in data])
        self.trains = {trainno: Train(trainno, [x for x in data if x[1]==trainno]) \
                       for trainno in trainnos}
=======
        self.trains = {trainno: Train(trainno, [x for x in data if x[1]==trainno]) \
                       for trainno in set([x[1] for x in data])}
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77

def chk(trip, sections, railstation, trainlog, railfare, railopkm):
    '''
    triplog.txt の1行のチェック
    入出場時刻・運賃・各区間の営業キロ取得
    [return] flg, msg, 入場時刻文字, 出場時刻文字, 運賃, 営業キロのリスト
        flg  0: ok
             1: warning(triplog2.txtに出力はする)
             9: error(triplog2.txtに出力しない)
    '''
    tripid, o_st, d_st, o_datetime, _, _, d_datetime, *_ = trip

    opkms = []
    for i, s in enumerate(sections):
        trainno, lineid, dep_stcd, _, arr_stcd, *_ = s

        msg = [tripid, '区間{}'.format(i + 1), None, 'railstation.txtにない']
        if not lineid in  railstation.railstation:
            msg[2] = '路線{}'.format(lineid)
            return 9, msg
        if not dep_stcd in railstation.railstation[lineid]:
            msg[2] = '路線{0} 駅{1}'.format(lineid, dep_stcd)
            return 9, msg
        if not arr_stcd in railstation.railstation[lineid]:
            msg[2] = '路線{0} 駅{1}'.format(lineid, arr_stcd)
            return 9, msg

        msg[3] = 'trainlog.txtにない'
<<<<<<< HEAD
        if not trainno in trainlog.trains or lineid != trainlog.trains[trainno].lineid:
=======
        if not trainno in trainlog.trains \
          or lineid != trainlog.trains[trainno].lineid:
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
            msg[2] = '路線{0} 列車番号{1}'.format(lineid, trainno)
            return 9, msg
        if not dep_stcd in trainlog.trains[trainno].stations[: -1]:
            msg[2] = '路線{0} 列車番号{1} 発駅{2}'.format(lineid, trainno, dep_stcd)
            return 9, msg
        if not arr_stcd in trainlog.trains[trainno].stations[1: ]:
            msg[2] = '路線{0} 列車番号{1} 着駅{2}'.format(lineid, trainno, arr_stcd)
            return 9, msg

        # 営業キロ
        opkm = railopkm.get_railopkm(lineid, dep_stcd, arr_stcd)
        if not opkm:
<<<<<<< HEAD
            linenm = railstation.ln_id2nm[lineid]
            dep_stnm, arr_stnm = railstation.st_cd2nm[dep_stcd], railstation.st_cd2nm[arr_stcd]
            msg[2] = '{0} {1} {2}'.format(linenm, dep_stnm, arr_stnm)
=======
            msg[2] = '{0} {1} {2}'.format(railstation.ln_id2nm[lineid], \
                                          railstation.st_cd2nm[dep_stcd], \
                                          railstation.st_cd2nm[arr_stcd])
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
            msg[3] = 'railopkm.txtにない'
            return 9, msg
        opkms.append(opkm)

    msg[1] = '-'
    msg[3] = 'railstation.txtにない'
    if not o_st in railstation.st_cd2nm:
        msg[2] = '入場駅{}'.format(o_st)
        return 9, msg
    if not d_st in railstation.st_cd2nm:
        msg[2] = '出場駅{}'.format(d_st)
        return 9, msg

    # 運賃
    fare = railfare.get_railfare(o_st, d_st)
    if not fare:
<<<<<<< HEAD
        msg[2] = '入場駅{0} 出場駅{1}'.format(o_st, d_st)
=======
        msg[2] = '{0} {1}'.format(railstation.st_cd2nm[o_st], \
                                  railstation.st_cd2nm[d_st])
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
        msg[3] = 'railfare.txtにない'
        return 9, msg

    # 入出場時刻
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

    # warning
    if o_st != sections[0][2]:
        msg[2] = '入場駅{}'.format(o_st)
        msg[3] = '区間1の発駅 {} と不一致'.format(sections[0][2])
        flg = 1
    elif d_st != sections[-1][4]:
        msg[2] = '出場駅{}'.format(d_st)
        msg[3] = '最終区間の着駅 {} と不一致'.format(sections[-1][4])
        flg = 1
    else:
        flg, msg = 0, None
<<<<<<< HEAD

    return flg, msg, o_time, d_time, fare, opkms

=======

    return flg, msg, o_time, d_time, fare, opkms

>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
def sec2char(sec, corr=True):
    ''' 秒を時刻の文字列に '''
    sc = sec % 60
    mn = (sec // 60) % 60
    hr = (sec // 3600)
    if corr:  # corr -> 24~ は 0~ に
        hr = hr % 24
    return ('{0}:{1:02}:{2:02}'.format(hr, mn, sc))

def section_edit(train, dep_stcd, arr_stcd):
    ''' 区間の乗降時刻・区間情報を編集 '''
    dep_i = train.stations.index(dep_stcd)
    arr_i = train.stations.index(arr_stcd)

    # 乗降時刻
<<<<<<< HEAD
    dep_sec = train.dep_sec[dep_i]
    arr_sec = train.arr_sec[arr_i]
    od_time = '{0}-{1}'.format(sec2char(dep_sec), sec2char(arr_sec))

    # 区間情報
    secinfo = ''.join(['-'.join([st, nst, str(pas)])  + ';' for st, nst, pas \
                        in zip(train.stations[dep_i: arr_i], \
                               train.stations[dep_i + 1: arr_i + 1], \
                               train.pass_num[dep_i: arr_i])])
=======
    od_time = '{0}-{1}'.format(sec2char(train.dep_sec[dep_i]), \
                               sec2char(train.arr_sec[arr_i]))

    # 区間情報
    secinfo = ''.join(['-'.join([st, nst, str(pas)])  + ';' for st, nst, pas \
                       in zip(train.stations[dep_i: arr_i], \
                              train.stations[dep_i + 1: arr_i + 1], \
                              train.pass_num[dep_i: arr_i])])
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77

    return od_time, secinfo

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-i', '--inputdirname', help='入力dir。\
                     defaultはscriptの位置から ../input。', default=None)
    psr.add_argument('-o', '--outputdirname', help='出力dir。\
                     defaultはscriptの位置から ../output。', default=None)
    psr.add_argument('-d', '--detectenc', help='入力ファイルの文字コードを \
                     判別する場合 "y"', default='n', choices=['y', 'n'])
    args = psr.parse_args()
    indirn, outdirn = getdirn(args.inputdirname, args.outputdirname)
    if not os.path.isdir(outdirn):
        os.mkdir(outdirn)

    # ファイル、文字コード
    fns = 'railstation.txt', 'triplog.txt', 'trainlog.txt', 'railfare.txt', \
          'railopkm.txt'
    encs = 'utf-8', 'ascii', 'utf-8-sig', 'cp932', 'cp932'
    fnfs = [os.path.join(indirn, fn) for fn in fns]
    if args.detectenc == 'y':
        encs = [detect_enc(fnf) for fnf in fnfs]
    rs_fnf, tri_fnf, tra_fnf, rf_fnf, rok_fnf = fnfs
    rs_enc, tri_enc, tra_enc, rf_enc, rok_enc = encs
    ofn, errfn = 'triplog2.txt', 'err.txt'
    ofnf = os.path.join(outdirn, ofn)
    errfnf = os.path.join(outdirn, errfn)

<<<<<<< HEAD
=======
    # 読込
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
    railstation = RailStation(rs_fnf, rs_enc)
    railfare = RailFare(rf_fnf, rf_enc, railstation)
    railopkm = RailOpKm(rok_fnf, rok_enc, railstation)
    trainlog = TrainLog(tra_fnf, tra_enc)

    # 変換
    err_out = []
    with open(tri_fnf, 'r', encoding=tri_enc) as inf, open(ofnf, 'w') as outf:

        for l in inf:
            l = [x.strip() for x in l.split('\t')]
            trip, sections = l[: 9], l[9:]
            tripid, o_st, d_st, o_datetime, _, num, d_datetime, *_ = trip
            sections = [sections[i: i + 8] for i in range(0, len(sections), 8)]

<<<<<<< HEAD
            flg, msg, *values = chk(trip, sections, railstation, trainlog, railfare, railopkm)
=======
            flg, msg, *values \
                = chk(trip, sections, railstation, trainlog, railfare, railopkm)
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77

            if flg != 0:
                err_out.append(msg)
                if flg == 9:
                    continue
            
            o_time, d_time, fare, opkms = values
<<<<<<< HEAD
=======

            outline = [tripid, o_st, d_st, o_time, d_time, str(num), str(fare), \
                       '0', '0', '0']
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77

            # 各区間
            for s, opkm in zip(sections, opkms):
                trainno, lineid, dep_stcd, _, arr_stcd, *_ = s
                od_time, secinfo = section_edit(trainlog.trains[trainno], \
                                                dep_stcd, arr_stcd)

<<<<<<< HEAD
            # 各区間
            for s, opkm in zip(sections, opkms):
                trainno, lineid, dep_stcd, _, arr_stcd, *_ = s
                od_time, secinfo = section_edit(trainlog.trains[trainno], dep_stcd, arr_stcd)

=======
>>>>>>> 1b0b25d1bea6c3f58eaee261a5b528dd0b3d5e77
                outline += [lineid, trainno, od_time, secinfo, str(opkm)]

            outf.write('\t'.join(outline) + '\n')

    # errあれば出力
    if err_out:
        with open(errfnf, 'w') as errf:
            errf.write('\t'.join(['ID', '区間番号', 'エラー値', '内容']) + '\n')
            errf.write(''.join(['\t'.join(l) + '\n' for l in err_out]))
