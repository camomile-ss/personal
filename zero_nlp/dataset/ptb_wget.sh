#!/bin/bash
# PTB corpus download

indir=https://raw.githubusercontent.com/tomsercu/lstm/master/data/
outdir=ptb/

for type in train test valid
do
    fname=ptb.${type}.txt
    wget ${indir}/${fname} -O ${outdir}/${fname}
done
