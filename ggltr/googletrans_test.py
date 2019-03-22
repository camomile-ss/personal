# coding: utf-8
'''
'''
import argparse
import json
import time
import os
import re
import requests
import urllib.parse
from getpass import getpass
from googletrans import Translator

def set_env_proxy(first, flg, envname):
    '''
    環境変数https_proxyをセット
    return
      1個め: 今のos.environの設定状況。 1, 2, 9
        1: http(s)://host:port
        2: http(s)://user:password@host:port
        9: 書式不正 or 合っててもproxy通らなかった -> err
      2個め: 環境変数のなまえ（大文字or小文字）
    '''
    ptn_hp = re.compile(r'^(https?:\/\/)([^@]+:\d+)$')  # パターン1 http(s)://host:port
    ptn_hpup = re.compile(r'^https?:\/\/[^@]+:[^@]+@[^@]+:\d+$')  # パターン2 http(s)://user:pass@host:port

    # 最初なら、環境変数あるか、名前が大文字か小文字か調べる
    if first:
        if 'https_proxy' in os.environ:
            envname = 'https_proxy'
        elif 'HTTPS_PROXY' in os.environ:
            envname = 'HTTPS_PROXY'
        if envname:
            # パターン1
            if ptn_hp.search(os.environ[envname]):
                flg = 1  # host, port だけ設定されてる
            # パターン2
            elif ptn_hpup.search(os.environ[envname]):
                print('[err] fix environment variable "{0}".'.format(envname))
                return 9, envname  # 書式あってるけど通ってない -> err
            else:
                print('[err] fix environment variable "{0}".'.format(envname))
                return 9, envname  # 書式不正
        else:  # 環境変数設定なし
            envname = 'https_proxy'
            # host名, port番号 入力求めて、まずパターン1で作る
            scheme = input('proxy scheme ("https" or "http") >> ')
            host = input('proxy host name or ip address >> ')
            port = input('proxy port no >> ')
            os.environ[envname] = '{0}://{1}:{2}'.format(scheme, host, port)
            return 1, envname  # 1で戻してもう一度実行させる

    # 今、パターン1だったら、user, pass 入力求めてパターン2に編集する
    if flg == 1:
        mob_hp = ptn_hp.search(os.environ[envname])
        user = urllib.parse.quote(input('proxy user >> '))
        psw = urllib.parse.quote(getpass('proxy password >> '))
        os.environ[envname] = '{0}{1}:{2}@{3}'.format(mob_hp.group(1), user, psw, mob_hp.group(2))
        return 2, envname  # 2で戻してもう一度実行させる

    # 今、パターン2だったら、入力させた host, port, user, pass どれか間違ってる
    if flg == 2:
        print('[err] proxy input err.')
        return 9, envname

    if flg == 9:  # ここには来ないはずだけど念のため
        print('[err] script logical err.')
        return 9, envname

def try_translate(text, try_span=10, try_times=5):
    tt = None
    e1_cnt, env_first, env_now, envname = 0, 1, 0, None
    while True:
        try:
            tt = translator.translate(text, dest='ja')
        except json.decoder.JSONDecodeError:
            e1_cnt += 1
            if e1_cnt > try_times:
                break
            print('[warn] sleep {0}sec (try {1}/{2})...'.format(try_span, e1_cnt, try_times))
            time.sleep(try_span)
        except requests.exceptions.ConnectionError:
            env_now, envname = set_env_proxy(env_first, env_now, envname)
            env_first = 0
            if env_now == 9:
                break
        except:
            print('[err] unknown..')
            break
        else:
            break
    if tt:
        return tt
    return

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infname', help='input file name.')
    args = psr.parse_args()
    infname = args.infname

    translator = Translator()

    with open(infname, 'r', encoding='utf-8') as inf:
        #lines = [l.strip() for l in inf.readlines()]
        alllines = inf.read()

    """
    def try_translate(text):
        try:
            tt = translator.translate(text, dest='ja')
        except json.decoder.JSONDecodeError:
            return
        return tt
    """
    span = 10
    times = 3

    tt = try_translate(alllines, try_span=span, try_times=times)
    if tt:
        print(tt)
    else:
        print('[err] cannnot translate.')

    """
    for cnt in range(times):
        tt = try_translate(alllines)
        if tt:
            break
        print('[warn] sleep {0}min...'.format(span))
        time.sleep(span)
    if not tt:
        print('[err] cannot translate.')
    else:
        print(tt.text)
    """

    """
    for i, l in enumerate(lines):
        for cnt in range(times):
            tt = try_translate(l)
            if tt:
                break
            print('[warn] block:{0} sleep {1}min...'.format(i+1, span))
            time.sleep(span)
        if not tt:
            print('[err] cannot translate block:{0}.'.format(i+1))
            continue

        print(tt.text)
    """