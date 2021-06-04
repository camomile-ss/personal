fdate=$1

tmpfile=$(mktemp)

# 1207作成データと1220~作成データをくっつける
cat wk/bus_wk/20181127分/緯度経度データ.csv > ${tmpfile}
cat wk/bus_wk/20181219分/緯度経度データ_1219追記分.csv >> ${tmpfile}
#cat wk/bus_wk/緯度経度データ_${fdate}.csv >> ${tmpfile}

# ルート作成するrailstation.txt
rsfile=~/data/20181129~20181108_緯度経度/データ/作業依頼/バス_20181129/railstation_1220追記.txt

python bus_make_route.py ${tmpfile} ${rsfile}

rm ${tmpfile}
