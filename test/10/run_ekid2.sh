#!/bin/bash

indir=input_20201124
outdir=output_20201124/
extdir=${outdir}station_ext/
infname=${extdir}station_ext_mod.csv
scfname=${outdir}STATION_CODE.txt
outfname=${extdir}station_ext_mod2_stname.csv

python ekid2_sc.py ${indir} ${infname} ${scfname} ${outfname}
