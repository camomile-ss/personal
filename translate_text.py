#!/usr/bin/python

import six
from google.cloud import translate_v2 as translate
import argparse

psr = argparse.ArgumentParser()
psr.add_argument('infname')
psr.add_argument('outfname')
args = psr.parse_args()
infn = args.infname
outfn = args.outfname

translate_client = translate.Client()

with open(infn, 'r') as f:
    texts = f.readlines()

#translated_texts = []
with open(outfn, 'w') as outf:
    for l in texts:
        if l:
            result = translate_client.translate(l, target_language='ja')
            l_ = result['translatedText']
        else:
            l_ = ''
        outf.write(l_ + '\n')
        #translated_texts.append(l_)

#with open(outfn, 'w') as outf:
#    outf.write('\n'.join(translated_texts) + '\n')

