#!/bin/bash

fixdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/splitコピー元/01_在来線_JRE_001-011_v3
olddirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v2
newdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v3
conffn=copy_curve_lines.txt

python copy_curve_func.py ${fixdirn} ${olddirn} ${newdirn} ${conffn}

