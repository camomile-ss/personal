#!/bin/bash

#fixdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/splitコピー元/私鉄3_東武_v4
fixdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/splitコピー元/01_在来線_東武_v24
oldsplitdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v23
newsplitdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/01_在来線_v1_parent1way_split_v24
conffn=../20201124_tohoku/output/cv-editor_data/04_curve生成/copy_curve_lines.txt

python copy_curve_func.py ${fixdirn} ${oldsplitdirn} ${newsplitdirn} ${conffn}

orgdirn=../20201124_tohoku/output/cv-editor_data/03_公開時刻表/01_在来線_v15

mergedirn=${newsplitdirn}_merge

python merge.py ${newsplitdirn} ${mergedirn} -o ${orgdirn}

alldirn=${mergedirn}_allchild

python parent1wayToAll.py ${orgdirn} ${mergedirn} ${alldirn}
