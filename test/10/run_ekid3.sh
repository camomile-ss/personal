#!/bin/bash

outdir=output_20201124/
inf=${outdir}station_ext/station_ext_mod2_stname.csv
scf=${outdir}STATION_CODE.txt
rwf=${outdir}RAILWAY.txt
rsf=${outdir}railstation.txt

python ekid3_rw.py ${inf} ${scf} ${rwf} ${rsf} -r n -l 2

#rwf=${outdir}RAILWAY_step1.txt
#rsf=${outdir}railstation_step1.txt

#python ekid3_rw.py ${inf} ${scf} ${rwf} ${rsf} -r n
