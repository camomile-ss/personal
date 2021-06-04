#!/bin/bash
# curve 生成（omsとのずれが気になる所）(1)
# 在来線片道データを分割

srcdirn=../mkdata_from_ekidata.jp
dirn=output/cv-editor_data/02_curve生成（大まか）


# 片道分割データ作成 -------------------------------------------------##
compfn=input/company_conv.csv
indirn=${dirn}/01_在来線_片道
outdirn=${dirn}/02_在来線_片道_分割

# 会社ごとに分割
python ${srcdirn}/cvdata_bunkatsu.py ${compfn} ${indirn} ${outdirn}

# JR東日本は 10路線ずつ分割
python ${srcdirn}/cvdata_bunkatsu_jre.py ${outdirn}/002_JR東日本

