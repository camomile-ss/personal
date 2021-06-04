#!/bin/bash

fixdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/splitコピー元/11_新幹線_v2
oldsplitdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/11_新幹線_parent1way_v1
newsplitdirn=../20201124_tohoku/output/cv-editor_data/04_curve生成/11_新幹線_parent1way_v2
conffn=../20201124_tohoku/output/cv-editor_data/04_curve生成/copy_curve_lines_shinkansen_v2.txt

python copy_curve_func.py ${fixdirn} ${oldsplitdirn} ${newsplitdirn} ${conffn}

orgdirn=../20201124_tohoku/output/cv-editor_data/03_公開時刻表/11_新幹線_v3

#mergedirn=${newsplitdirn}_merge

#python merge.py ${newsplitdirn} ${mergedirn} -o ${orgdirn}

alldirn=${newsplitdirn}_allchild

python parent1wayToAll.py ${orgdirn} ${newsplitdirn} ${alldirn}
