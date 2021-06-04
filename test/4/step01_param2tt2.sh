#!/bin/bash
# 固定間隔時刻表生成 (2)
# 在来線 time_table_param_input.txt, timetable_master.txt を作成

scriptdirn=../mkdata_from_ekidata.jp

infn=input/time_table_param_wk.txt
indirn=output/cv-editor_data/01_仮時刻表（固定間隔）/02_在来線_往復

python ${scriptdirn}/cvdata_mk_timetableparam.py ${infn} ${indirn}

python ${scriptdirn}/cvdata_timetable_from_param.py ${indirn}
