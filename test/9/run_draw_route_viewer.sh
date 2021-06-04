#!/bin/bash
# 可視化ビューワ向けcurve_data改修作業用

no=$1
routepref=$2
zoom=$3
filedate=$4
wkdir=wk_20181220viewer/
llfname=${wkdir}/curve_data_${filedate}.txt
mapdir=${wkdir}/map/

python draw_route.py ${llfname} ${mapdir}/${no}_${routepref}.html ${routepref} -z ${zoom} -m 2 -b 1 -s t
python draw_route.py ${llfname} ${mapdir}/${no}_${routepref}_中間点マーカあり.html ${routepref} -z ${zoom} -m 1 -b 1 -s t
