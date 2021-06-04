#!/bin/bash
orgdirn=../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v15
indirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v5
outdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_split_roundtrip_v5

if [ ! -d ${outdirn} ]; then
    mkdir ${outdirn}
fi

ls ${indirn} | while read line
do
    echo ${line}
    python parent1wayToRoundtrip.py ${orgdirn} ${indirn}/${line} ${outdirn}/${line}
done
