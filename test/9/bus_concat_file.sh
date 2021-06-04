#!/bin/bash

indir=wk/bus_wk/routes/
tdate=$(date +'%Y%m%d')
outf=wk/bus_wk/緯度経度データ_${tdate}.csv

if [ -f ${outf} ]; then
    echo [err] file exists.
else
    ls -1 ${indir} | grep ".csv" | while read line
    do
	cat ${indir}/${line} >> ${outf}
    done
    echo concat done.
fi
