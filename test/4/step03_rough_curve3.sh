#!/bin/bash
# curve 生成（omsとのずれが気になる所）(3)
# 新幹線 片道カーブ生成データから、復路作成

srcdirn=../mkdata_from_ekidata.jp
dirn=output/cv-editor_data/02_curve生成（大まか）

indirn=${dirn}/14_新幹線_片道_curve生成
outdirn=${dirn}/15_新幹線_往復

python ${srcdirn}/cvdata_add_reverse.py ${indirn} ${outdirn}
