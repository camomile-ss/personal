
#!/bin/bash
# バス確認マップ作成用
# halfw.csv（不完全データ）からrouteprefを含む路線名だけ抜き出してマップ作成

filedate=$1
no=$2
routepref=$3
zoom=$4
wkdir=wk/bus_wk/
#halffname=緯度経度データ_halfw.csv
llfname=緯度経度データ_${filedate}.csv
mapdir=${wkdir}/routes/

python draw_route.py ${wkdir}/${llfname} ${mapdir}/${no}_${routepref}.html ${routepref} ${zoom} 2 1
python draw_route.py ${wkdir}/${llfname} ${mapdir}/${no}_${routepref}_中間点マーカあり.html ${routepref} ${zoom} 1 1
