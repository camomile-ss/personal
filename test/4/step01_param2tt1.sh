#!/bin/bash
# 固定間隔時刻表生成 (1)
# 在来線 分割データと往復データを作成

srcdirn=../mkdata_from_ekidata.jp
dirn=output/cv-editor_data/01_仮時刻表（固定間隔）


# 片道分割データ作成 -------------------------------------------------##
compfn=input/company_conv.csv
indirn=${dirn}/01_在来線_片道
outdirn=${dirn}/09_在来線_片道_分割

# 会社ごとに分割
python ${srcdirn}/cvdata_bunkatsu.py ${compfn} ${indirn} ${outdirn}

# JR東日本は 10路線ずつ分割
python ${srcdirn}/cvdata_bunkatsu_jre.py ${outdirn}/002_JR東日本


# 往復データ作成 ------------------------------------------------------##
outdirn=${dirn}/02_在来線_往復

python ${srcdirn}/cvdata_add_reverse.py ${indirn} ${outdirn}
