#!/bin/bash
# 固定値時刻表生成 (3)
# 新幹線 time_table_param_input.json, timetable_master.txt 作成

scriptdirn=../mkdata_from_ekidata.jp

infn=input/time_table_param_wk.txt
indirn=output/cv-editor_data/01_仮時刻表（固定間隔）/12_新幹線_往復

python ${scriptdirn}/cvdata_mk_timetableparam.py ${infn} ${indirn}

trainno=3982

python ${scriptdirn}/cvdata_timetable_from_param.py ${indirn} -t ${trainno}
