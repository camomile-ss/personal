# coding: utf-8
''' 住所整形の関数 '''

import re
from common_character import fullwidth, kanji_to_num

def banchi_fullwidth(addr):
    ''' 住所の番地を全角アラビア数字にする '''
    ptn = re.compile(r'(.)(([一二三四五六七八九十])丁目)')  # Ｘ丁目 (漢数字)
    
    mob = ptn.search(addr)
    if mob:
        if mob.group(1) in '一二三四五六七八九十':
            print('kan-suji more than 1-order')  # 丁目二ケタ以上:対応してない
        chome = str(kanji_to_num(mob.group(3))) + '丁目'
        addr = addr.replace(mob.group(2), chome)
    
    addr = fullwidth(addr)  # 半角数字は全角に

    return addr


if __name__ == '__main__':
    
    char1 = '埼玉県さいたま市桜区下大久保255'
    print(char1)
    print(banchi_fullwidth(char1))
    print()
    char2 = '東京都江東区豊洲四丁目1-1'
    print(char2)
    print(banchi_fullwidth(char2))
    print()
    char3 = '千葉県流山市西初石六丁目'
    print(char3)
    print(banchi_fullwidth(char3))
    print()
    char4 = '埼玉県和光市本町4-6'
    print(char4)
    print(banchi_fullwidth(char4))
    print()
    char5 = '千葉県流山市西初石六十三丁目'
    print(char5)
    print(banchi_fullwidth(char5))
    print()
    