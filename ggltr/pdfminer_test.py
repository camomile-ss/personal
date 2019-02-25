# coding: utf-8
'''
Created on Thu Feb 21 15:37:57 2019

@author: otani
'''
import sys
import argparse

def parse_pdf_pages(pdfname):
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from io import StringIO

    p_txts = []
    rsrcmgr = PDFResourceManager()

    with open(pdfname, 'rb') as pdff:
        for p in PDFPage.get_pages(pdff):
            with StringIO() as strio, \
                 TextConverter(rsrcmgr, strio, codec='utf-8', laparams=LAParams()) as device:
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(p)
                p_txts.append(strio.getvalue())

    return p_txts

if __name__ == '__main__':

    psr = argparse.ArgumentParser()
    psr.add_argument('infname')
    args = psr.parse_args()
    infname = args.infname

    texts = parse_pdf_pages(infname)
    #print(len(texts))
    #print(texts[0])
    #print(texts[-1])

    for i, t in enumerate(texts):
        print('*** page:', i)
        print([t.strip()], '\n')
