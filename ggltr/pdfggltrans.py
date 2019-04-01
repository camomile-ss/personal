# coding: utf-8
''' PDFを日本語に翻訳 '''
import sys
import argparse
import os
import re
import cchardet
import json
import time
import requests
import urllib.parse
from getpass import getpass
from googletrans import Translator

def parse_pdf_pages(pdffname):
    ''' PDFから各ページのテキスト抽出 '''

    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
    from io import StringIO

    p_txts = []
    rsrcmgr = PDFResourceManager()

    with open(pdffname, 'rb') as pdff:
        try:
            for p in PDFPage.get_pages(pdff):
                with StringIO() as strio, \
                     TextConverter(rsrcmgr, strio, codec='utf-8', laparams=LAParams()) as device:
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    interpreter.process_page(p)
                    p_txts.append(strio.getvalue())
        except PDFTextExtractionNotAllowed:
            print('[err] PDF {0} text extraction not allowed.'.format(pdffname))
            sys.exit()
        except Exception as e:
            print('[err]: {0}'.format(type(e)))
            print('e: {0}'.format(e))
            print('e.args: {0}'.format(e.args))
            sys.exit()

    return p_txts

def parse_pdf(pdffname):
    ''' PDFテキスト抽出 '''

    pages = parse_pdf_pages(pdffname)
    # 各ページ
    for i in range(len(pages)):
        pages[i] = pages[i].strip()  # 改ページ入ってるのでstrip()
        pages[i] = re.sub(r'\n*\d*$', '\n', pages[i])  # ページを取る
        pages[i] = re.sub(r'\.\n$', '\.\n\n', pages[i])  # ピリオドで終わってたら空行入れる
    # つなげる
    text = ''.join(pages)

    return text

def read_text(txtfname):
    ''' テキストファイルを読む '''

    # 文字コード判定
    with open(txtfname, 'rb') as f:
        cd = cchardet.detect(f.read())
    with open(txtfname, 'r', encoding=cd['encoding']) as f:
        text = f.read()

    return text

def align_length(block):
    ''' blockの長さを5000文字以下に '''

    # 5000文字以下ならそのまま --------------------##
    if len(block) <= 5000:
        return [block]

    # 5000文字以下に分割 --------------------------##
    blocks_al = []
    num = -(-len(block) // 5000)  # 分割数
    blen = -(-len(block) // num)  # 均等に分割したときのblock長

    # ピリオド+空文字の位置のリスト
    idx_period = [im.end(0) for im in re.finditer(r'\.\s', block)]
    # 空文字の位置のリスト
    idx_space = [im.end(0) for im in re.finditer(r'\s', block)]

    b_start, b_end = 0, 0
    while b_end < len(block):
        # 残り5000文字切っていたら終わり
        if len(block) - b_end <= 5000:
            blocks_al.append(block[b_end: ])
            break

        # 均等分割長と5000の間のピリオド+空文字の位置を見つける
        idx_match = [x for x in idx_period if x >= blen and x < 5000]
        # 無いとき
        if len(idx_match) == 0:
            # 均等分割長未満で探す
            idx_match = [x for x in idx_period if x < blen][::-1]  # 長いほうを取るので逆に
            if len(idx_match) == 0:
                # それでもなければ空文字で分割
                idx_match = [x for x in idx_space if x >= blen and x < 5000]
                if len(idx_match) == 0:
                    idx_match = [x for x in idx_space if x < blen][::-1]
                    # 空文字もなければ、単純に均等分割長で分割
                    if len(idx_match) == 0:
                        idx_match = [b_start + blen]
        # block切り出し
        b_end = idx_match[0]
        blocks_al.append(block[b_start: b_end].strip())
        b_start = b_end

    return blocks_al

def format_text(raw_text):
    ''' 翻訳用に整形 '''

    # 改行2行でblockわけ
    blocks = raw_text.split('\n\n')
    # 1block5000文字以下に
    blocks_al = [x for b in blocks for x in align_length(b)]
    # 各block内の改行取る
    blocks_al = [re.sub(r'\s', ' ', b) for b in blocks_al]
    # 各blockを改行でつなげる
    f_text = '\n'.join(blocks_al) + '\n'

    return f_text

def set_env_proxy(first, flg, envname):
    '''
    環境変数https_proxyをセット
    return
      1個め: 今のos.environの設定状況。
        1: http(s)://host:port
        2: http(s)://user:password@host:port
        9: 書式不正 or 合っててもproxy通らなかった -> err
      2個め: 環境変数のなまえ（'https_proxy' or 'HTTPS_PROXY'）
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
    ''' 日本語に翻訳 '''

    translator = Translator()

    tt = None
    e1_cnt, env_first, env_now, envname = 0, 1, 0, None
    while True:
        try:
            tt = translator.translate(text, dest='ja')
        # proxy設定必要
        except requests.exceptions.ConnectionError:
            env_now, envname = set_env_proxy(env_first, env_now, envname)
            env_first = 0
            if env_now == 9:  # 書式あってないか、入力値間違ってる
                break
        # googleがブロック?
        except json.decoder.JSONDecodeError:
            e1_cnt += 1
            if e1_cnt > try_times:  # リトライ回数超えたら終わり
                break
            print('[warn] sleep {0}sec (try {1}/{2})...'.format(try_span, e1_cnt, try_times))
            time.sleep(try_span)  # リトライ間隔待つ
        except Exception as e:
            print('[err]: {0}'.format(type(e)))
            print('e.args: {0}'.format(e.args))
            print('e: {0}'.format(e))
            break
        else:
            break
    if tt:
        return tt
    return

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infname', help='入力ファイル名。pdfまたはテキストファイル。')
    psr.add_argument('-o', '--outdir', help='出力ディレクトリ。\
                     省略した場合はカレントディレクトリに出力されます。', default='./')
    psr.add_argument('-f', '--formatted', help='整形済み。\
                     余分な改行の削除などの整形が終わっているテキストファイルを入力する場合指定してください。',
                     action='store_true')
    psr.add_argument('-t', '--trytimes', help='google翻訳が返答しない場合にリトライする回数。default 5。',
                     type=int, default=5)
    psr.add_argument('-s', '--tryspan', help='google翻訳が返答しない場合にリトライする間隔(秒)。default 5。',
                     type=int, default=5)
    args = psr.parse_args()

    infbase, _ = os.path.splitext(os.path.basename(args.infname))

    # pdf
    mob = re.search(r'[^\/]*\.[pP][dD][fF]$', args.infname)
    if mob:

        if args.formatted:
            print('pdfではオプション -f (--formatted) は指定できません。', file=sys.stderr)
            sys.exit()

        # pdfからテキストに
        print('getting text from pdf..')
        raw_text = parse_pdf(args.infname)
        # 中間ファイルに書き出す
        ppfname = os.path.join(args.outdir, '{0}_parse_pdf.txt'.format(infbase))
        with open(ppfname, 'w', encoding='utf-8') as pf:
            pf.write(raw_text)

    # テキストファイル
    else:
        raw_text = read_text(args.infname)

    # 整形済みか
    if args.formatted:
        org_text = raw_text
    else:
        print('formatting..')
        org_text = format_text(raw_text)  # 整形処理
        # 中間ファイルに書き出す
        orgfname = os.path.join(args.outdir, '{0}_original.txt'.format(infbase))
        with open(orgfname, 'w', encoding='utf-8') as of:
            of.write(org_text)

    # 翻訳
    print('translating..')
    jp_text = []
    org_text = org_text.split('\n')
    for i, ot in enumerate(org_text):
        ttj = try_translate(ot, try_span=args.tryspan, try_times=args.trytimes)
        if ttj:
            jp_text.append(ttj.text)
        else:
            print('block {0} cannot translate.'.format(i+1))
        if (i + 1) % 100 == 0:
            print('{:.1f}%..'.format(i / len(org_text) * 100))
    print('100.0%.')

    # 翻訳文書き出す
    jp_text = '\n'.join(jp_text) + '\n'
    jpfname = os.path.join(args.outdir, '{0}_japanese.txt'.format(infbase))
    print('{0} writing..'.format(jpfname))
    with open(jpfname, 'w', encoding='utf-8') as jf:
        jf.write(jp_text)

    print('done.')
