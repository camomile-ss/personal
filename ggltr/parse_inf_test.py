# coding: utf-8
'''
Created on Thu Feb 21 15:37:57 2019

@author: otani
'''
import sys
import argparse
import re
import cchardet

def parse_pdf_pages(pdfname):
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
    from io import StringIO

    p_txts = []
    rsrcmgr = PDFResourceManager()

    with open(pdfname, 'rb') as pdff:
        try:
            for p in PDFPage.get_pages(pdff):
                with StringIO() as strio, \
                     TextConverter(rsrcmgr, strio, codec='utf-8', laparams=LAParams()) as device:
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    interpreter.process_page(p)
                    p_txts.append(strio.getvalue())
        except PDFTextExtractionNotAllowed:
            print('[err] PDF {0} text extraction not allowed.'.format(infname))
            sys.exit()
        except Exception as e:
            print('[err]: {0}'.format(type(e)))
            print('e: {0}'.format(e))
            print('e.args: {0}'.format(e.args))
            sys.exit()

    return p_txts

def parse_pdf(infname):

    pages = parse_pdf_pages(infname)

    # 各ページ
    for i in range(len(pages)):
        #print('[page]: {0}'.format(i+1))
        pages[i] = pages[i].strip()  # 改ページ入ってるのでstrip()
        pages[i] = re.sub(r'\n*\d*$', '\n', pages[i])  # ページを取る
        pages[i] = re.sub(r'\.\n$', '\.\n\n', pages[i])  # ピリオドで終わってたら空行入れる

    # つなげる
    pdf_text = ''.join(pages)

    return pdf_text

def read_text(infname):

    # 文字コード判定
    with open(infname, 'rb') as f:
        cd = cchardet.detect(f.read())
    with open(infname, 'r', encoding=cd['encoding']) as f:
        text = f.read()

    return text

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infname')
    args = psr.parse_args()
    infname = args.infname

    # pdf
    mob = re.search(r'([^\/]*)\.[pP][dD][fF]$', infname)
    if mob:
        raw_text = parse_pdf(infname)
        # ファイルに書き出す
        pfname = '{0}_parse_pdf.txt'.format(mob.group(1))
        with open(pfname, 'w', encoding='utf-8') as pf:
            pf.write(raw_text)
    # テキストファイル
    else:
        raw_text = read_text(infname)

    print(raw_text)


