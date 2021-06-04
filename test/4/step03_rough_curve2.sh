#!/bin/bash
# curve 生成（omsとのずれが気になる所）(2)
# 在来線片道分割カーブ生成データをマージ, 復路作成

srcdirn=../mkdata_from_ekidata.jp
dirn=output/cv-editor_data/02_curve生成（大まか）

# マージ
indirn=${dirn}/03_在来線_片道_分割_curve生成
mrgdirn=${dirn}/04_在来線_片道_curve生成_マージ

python ${srcdirn}/cvdata_merge.py ${indirn} ${mrgdirn}

# 復路作成
outdirn=${dirn}/05_在来線_curve生成_往復

python ${srcdirn}/cvdata_add_reverse.py ${mrgdirn} ${outdirn}
