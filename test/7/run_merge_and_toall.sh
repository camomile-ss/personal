#!/bin/bash

orgdirn=../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v15

splitdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v3
mergedirn=${splitdirn}_merge

python merge.py ${splitdirn} ${mergedirn} -o ${orgdirn}

alldirn=${mergedirn}_allchild

python parent1wayToAll.py ${orgdirn} ${mergedirn} ${alldirn}
