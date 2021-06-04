# coding: utf-8
''' 文字列変換、文字コード判定、など '''

import cchardet

def fullwidth(char):
    ''' 受け取った文字列中の半角数字を全角に '''    
    fw_num = ['０', '１', '２', '３', '４', '５', '６', '７', '８', '９']
    r_char = ''
    for i in range(len(char)):
        if char[i] in '0123456789':
            r_char += fw_num[int(char[i])] 
        else:
            r_char += char[i]
    return r_char

def kanji_to_num(char):
    ''' 漢数字を半角数字に（ひとケタだけ）'''
    kanji_num = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    if len(char) != 1:
        print(char)
        print('char length not 1')
        return char
    if char in kanji_num:
        return kanji_num.index(char)
    else:
        print('char is not kan-suji')
        return char

def enc_detect(filename):
    ''' ファイルの文字コード判定して返す '''
    with open(filename, 'rb') as inf:
        cd = cchardet.detect(inf.read())
    return cd['encoding']
