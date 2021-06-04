# coding: utf-8
''' 共通処理（日付関係） '''

import sys
from datetime import datetime, date, time, timedelta
import calendar

def day_type(dt):
    '''
    平日休日判断の関数（祝日の考慮なし）
    arg : 日付 date型
    return : 'Weekday' （月~金）,
             'Weekend' （土、日）
    '''
    try:
        dt.weekday()
    except:
        print('day_type func err : ', dt, file=sys.stderr)
        return('err')
    else:
        if dt.weekday() in (5,6):
            return 'Weekend'
        elif dt.weekday() in range(5):
            return 'Weekday'
        else:
            print(dt, ': dt.weekday() not in 0~6', file=sys.stderr)
            return('err')

def day_type_nh(dt):
    '''
    平日休日判断の関数その２（日本の祝日->休日）
    arg : 日付 date型
    return : 'Weekday' （月~金）,
             'Weekend' （土、日、祝）
    '''
    import jpholiday

    try:
        dt.weekday()
    except:
        print('day_type func err : ', dt, file=sys.stderr)
        return('err')
    else:
        if dt.weekday() in (5,6):
            return 'Weekend'
        elif jpholiday.is_holiday(dt):
            return 'Weekend'
        elif dt.weekday() in range(5):
            return 'Weekday'
        else:
            print(dt, ': dt.weekday() not in 0~6', file=sys.stderr)
            return('err')

def wday_name(dt, ptn=1):
    '''
    曜日の文字列の関数
    arg : 日付 date型, ptn=1 or 2
    return : ptn 1: 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
             ptn 2: '月', '火', '水', '木', '金', '土', '日'
    '''
    wday = {1: ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'),
            2: ('月', '火', '水', '木', '金', '土', '日')}
    try:
        c = wday[ptn][dt.weekday()]
    except:
        print('wday_name func err : ', dt, file=sys.stderr)
        return('err')
    else:
        return(c)

def tz_width_chk(width):

    if width == 0 or width > 60:
        print("timezone width:", width, "-> 60")
        return 60

    if 60 % width != 0:
        print('[err] cannot calc timezone. width =', width)
        return('')

    return width


def timezone(tm_cha, width=60):
    '''
    時刻の文字列を時間帯に変換
    arg : tm_cha : 時刻（文字列）(e.g. 235959)
          width  : 時間帯の幅（分）(e.g. 15)
    return : 時間帯（time型）(e.g. 23:45:00)
    '''
    width = tz_width_chk(width)

    hr = int(tm_cha[:2])
    mn = width * (int(tm_cha[2:4]) // width)
    return(time(hr, mn, 0))

def timezone_withdate(dttm_cha, width=60):
    '''
    時刻の文字列を時間帯に変換 **日付も考慮**
    arg : tm_cha : 時刻（文字列）(e.g. 2018-11-09 23:59:59)
          width  : 時間帯の幅（分）(e.g. 15)
    return : 時間帯（datetime型）(e.g. 2018-11-09 23:45:00)
    '''
    yr = int(dttm_cha[:4])
    mo = int(dttm_cha[5:7])
    dy = int(dttm_cha[8:10])

    width = tz_width_chk(width)

    hr = int(dttm_cha[11:13])
    mn = width * (int(dttm_cha[14:16]) // width)
    return(datetime(yr, mo, dy, hr, mn, 0))

def timezone_min(tmzn, dt):
    '''
    時間帯を、datetime型から分単位のintegerにする
    arg : tmzn : 時間帯（datetime型）
          dt   : 基準の日付（datetime型)
    return : 時間帯(分)（int型）
    '''
    delta_d = (tmzn - dt).days
    delta_s = (tmzn - dt).seconds
    if delta_s % 60 != 0:
        print('[warn] timezone =', tmzn)
    return int(delta_d * 24 * 60 + delta_s / 60)

def timezone_cha_both(tm_cha, width=60):
    '''
    時刻の文字列を時間帯に変換 **秒なし, 範囲**
    arg : tm_cha : 時刻（文字列）(e.g. 09:52)
          width  : 時間帯の幅（分）(e.g. 15)
    return : 時間帯（文字列）(e.g. 09:45-10:00)
    '''
    width = tz_width_chk(width)

    s_hr = int(tm_cha[:2])
    s_mn = width * (int(tm_cha[3:5]) // width)
    e_mn = (s_mn + width) % 60
    if e_mn == 0:
        e_hr = 0 if s_hr == 23 else (s_hr + 1)
    else:
        e_hr = s_hr
    return('{0:02}:{1:02}-{2:02}:{3:02}'.format(s_hr, s_mn, e_hr, e_mn))

def timezone_cha(tm_cha, width=60):
    '''
    時刻の文字列を時間帯に変換 **24時以降もあり, 秒なし**
    arg : tm_cha : 時刻（文字列）(e.g. 24:29)
          width  : 時間帯の幅（分）(e.g. 15)
    return : 時間帯（文字列）(e.g. 24:15)
    '''

    width = tz_width_chk(width)

    hr = tm_cha[:2]
    mn = width * (int(tm_cha[3:5]) // width)
    return('{0}:{1:02}'.format(hr, mn))

def timezone_from_sec(sec, width=60, tune=True):
    '''
    00:00:00 からの通算秒を時間帯に変換
    **秒なし**
    arg : sec    : 00:00:00からの通算秒（int）(e.g. 51569) (14:19)
          width  : 時間帯の幅（分）(e.g. 15)
          tune   : True なら(00時⇒24時、01時⇒25時、02⇒26時、03⇒27時)
    return : 時間帯（文字列）(e.g. 14:15)
    '''
    width = tz_width_chk(width)
    hr = sec // 3600
    mn = width * ((sec - 3600*hr) // 60 // width)

    if tune:
        hr = hr % 24  # 24時以上 -> いったん0~23時に
        if hr < 4:  # 0~3時は24~27時に
            hr = hr + 24

    return('{0:02}:{1:02}'.format(hr, mn))

def timezone_from_num_o24(dttm_num, ref_dt, width=60):
    '''
    入力: 14桁数字(str)、基準日は8桁数字(str)
    24時以降あり
    dttm_num:       20180603231652, 20180604012200
    ref_dt(基準日): 20180603,       (同左)
    return:         23:00,          25:00
    '''
    width = tz_width_chk(width)
    # datetime型に
    dttm = datetime(int(dttm_num[:4]), int(dttm_num[4:6]), int(dttm_num[6:8]),
                    int(dttm_num[8:10]), int(dttm_num[10:12]), int(dttm_num[12:]))
    ref_dt = datetime(int(ref_dt[:4]), int(ref_dt[4:6]), int(ref_dt[6:]))
    sec = int((dttm - ref_dt).total_seconds())
    hr = sec // 3600
    mn = width * ((sec - 3600*hr) // 60 // width)
    return '{0:02}:{1:02}'.format(hr, mn)

def date_list(start, end):
    '''
    start, end 間の日付のリストを返す
    arg : start, end 文字列 e.g. 20181016, 20181018
    return : 日付文字列のリスト ['20181016', '20181017', '20181018']
    '''
    try:
        s_dt = datetime.strptime(start, '%Y%m%d')
        e_dt = datetime.strptime(end, '%Y%m%d')
    except:
        print('date format err : ', start, end, file=sys.stderr)
        return(['err'])
    else:
        dt_list = []
        while s_dt <= e_dt:
            dt_list.append(s_dt.strftime('%Y%m%d'))
            s_dt += timedelta(days=1)
        return dt_list

def date_list_month(year, month):
    '''
    その月の日(date型)のリストを返す
    '''
    return [date(year, month, d+1) for d in range(calendar.monthrange(year, month)[1])]

def date_list_wd(year, month, we):
    '''
    その月の平日/休日のリストを返す(date型)
    we='Weekday' -> 平日
    we='Weekend' -> 休日
        (祝日は休日)
    '''
    return [d for d in date_list_month(year, month) if day_type_nh(d)==we]

def timezone_list(starthour=4, endhour=28, startmin=0, sec=False, onlystart=True, zero=False, zone_width=15):
    '''
    任意の範囲の時間帯リスト作成
        sec: False -> 23:30, True -> 23:30:00
        onlystart: True -> 23:30, False -> 23:30-23:45
        zero: True -> 03:15:00, False -> 3:15:00
    '''
    if 60 % zone_width != 0:
        print('[err] zone_width =', zone_width, file=sys.stderr)
        sys.exit()

    hr = list(range(starthour, endhour))
    mn = list(range(0, 60, zone_width))

    # format用（0:hour, 1:min）
    if zero:
        form = '{0:02}:{1:02}'
    else:
        form = '{0}:{1:02}'
    if sec:
        form = form + ':00'

    # 始時刻
    start = [form.format(hr[i], mn[j]) for i in range(len(hr)) for j in range(len(mn))]
    start = start[mn.index(startmin): ]  #

    if onlystart:
        return start
    else:
        # 終時刻
        end = start[1:] + [form.format(hr[-1]+1, mn[0])]
        return [s + '-' + e for s, e in zip(start, end)]

def timezone_list_old(zone_width=15):
    '''
    04:00-04:15 ～ 03:45-04:00 の時間帯リスト作成
    '''
    if 60 % zone_width != 0:
        print('[err] zone_width =', zone_width, file=sys.stderr)
        sys.exit()

    hr = list(range(4, 24)) + list(range(0, 4))
    mn = list(range(0, 60, zone_width))

    start = ['{0:02}:{1:02}'.format(hr[i], mn[j]) for i in range(len(hr)) for j in range(len(mn))]
    end = start[1:] + start[:1]
    return [s + '-' + e for s, e in zip(start, end)]

def sec2chartime(sec, zero=False, corr=False):
    '''
    秒を時刻の文字列に
    98765 -> 27:26:05
    (corr = True ... 3:26:05
            False...27:26:05)
    (zero = True ... 03:15:00
            False...  3:15:00)
    '''
    sc = sec % 60
    mn = (sec // 60) % 60
    hr = sec // 3600
    if corr:
        hr = hr % 24

    if zero:
        return ('{0:02}:{1:02}:{2:02}'.format(hr, mn, sc))
    return ('{0}:{1:02}:{2:02}'.format(hr, mn, sc))

def char2sectime(char, day_split_hour=0):
    '''
    文字列の時刻を秒に
    '3:15'     -> 11700
    '03:15:00' -> 11700
    '3:15:15'  -> 11715
    # day_split_hour 指定時以降を当日に
    '''
    hr, mn, *sc = char.split(':')
    hr, mn = int(hr), int(mn)
    if hr < day_split_hour:
        hr = hr + 24
    if len(sc):
        try:
            sc = int(sc[0])
        except:
            sc = float(sc[0])
    else:
        sc = 0
    return hr * 3600 + mn * 60 + sc

def str_date_delta(dt, delta):
    '''
    str日付の加減算
    input:  20190101(str), -2(int)
    output: 20181230(str)
    '''
    dt_wk = datetime(int(dt[:4]), int(dt[4:6]), int(dt[6:]))
    dt_wk = dt_wk + timedelta(days=delta)

    return '{0:04}{1:02}{2:02}'.format(dt_wk.year, dt_wk.month, dt_wk.day)

if __name__ == '__main__':

    #print(timezone_list())
    #print(timezone_list(starthour=6, endhour=24, sec=True, zone_width=5))
    #print(timezone_list(starthour=4, endhour=28, sec=False, onlystart=False, zone_width=15))
    #print(timezone_list(starthour=4, endhour=28, sec=False, onlystart=False, zero=True, zone_width=15))
    print(timezone_list(starthour=11, endhour=14, startmin=35, sec=False, zero=True, zone_width=5))

    #print(timezone_from_num_o24('20180601030500', '20180531', width=5))
    #print(timezone_from_num_o24('20180601030500', '20180601', width=5))
    #print(timezone_from_num_o24('20180601085959', '20180601', width=5))

    #print(char2sectime('03:15'))
    #print(char2sectime('03:15:00'))
    #print(char2sectime('03:15:15'))
    #print(char2sectime('00:00:00'))
    #print(char2sectime('12:25:10.5'))
    #print(str_date_delta('20190101', -2))
    #print(str_date_delta('20160831', 1))
    #print(str_date_delta('20160813', -1))

    #print(sec_to_chartime(98765))
    #print(sec_to_chartime(7200))

    #print(date_list_wd(2017,3, 'Weekday'))
    #print(date_list_wd(2017,3, 'Weekend'))

    #print(timezone("125959", 15))
    #print(day_type_nh(date(2017,3,20)))
    #print(day_type(date(2017,3,20)))
    #print(date_list('20171130', '20171227'))
    #print('09:55', timezone_cha_both('09:55',15))
    #print('23:55', timezone_cha_both('23:55',15))
    #print('00:00', timezone_cha_both('00:00',15))
    #print('04:20', timezone_cha_both('04:20',15))
    #print('12:30', timezone_cha_both('12:30',15))
    #print('12:30', timezone_cha_both('12:30',25))
    """
    print(51569, timezone_from_sec(51569, 15))
    print(14399, timezone_from_sec(14399, 15))
    print(14401, timezone_from_sec(14401, 15))
    print(14400, timezone_from_sec(14401, 15))
    print(36900, timezone_from_sec(36900, 15))
    print(36899, timezone_from_sec(36899, 15))
    print(111674, timezone_from_sec(111674, 15))
    print(86405, timezone_from_sec(86405, 15))
    """