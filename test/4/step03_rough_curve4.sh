#!/bin/bash

# curve 生成（omsとのずれが気になる所）(4)
# 仮時刻表作り直し（路線修正があったため）

srcdirn=../mkdata_from_ekidata.jp
dirn=output/cv-editor_data/02_curve生成（大まか）

infn=input/time_table_param_wk_step03.txt
indirn=${dirn}/06_在来線_curve生成_往復+仮時刻表

python ${srcdirn}/cvdata_mk_timetableparam.py ${infn} ${indirn}

python ${srcdirn}/cvdata_timetable_from_param.py ${indirn}

