#!/bin/bash

indir=$1
outdir=$2

ls -1 ${indir} | while read line
do
    cat ${indir}/${line} | grep -E "^4" > ${outdir}/${line}
done
