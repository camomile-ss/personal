#!/bin/bash

edir=駅データ/
#linef=${edir}line20190405free.csv
#staf=${edir}station20190405free.csv
#outdir=output/station_ext/
indir=input_20201124
linef=${edir}line20200619free.csv
staf=${edir}station20200619free.csv
outdir=output_20201124/station_ext/
outf=${outdir}station_ext.csv

if [ ! -d ${outdir} ]; then
    mkdir -p ${outdir}
fi

python ekid1_ext.py ${indir} ${staf} ${linef} ${outf}
