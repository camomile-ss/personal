#!/bin/bash

indir=$1
outf=$2

ls -1 ${indir} | while read line
do
    cat ${indir}/${line} >> ${outf}
done
