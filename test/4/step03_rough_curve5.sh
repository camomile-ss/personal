#/bin/bash

# curve 生成（omsとのずれが気になる所）(5)
# 在来線+新幹線 

zaidirn=output/cv-editor_data/02_curve生成（大まか）/06_在来線_curve生成_往復+仮時刻表
shidirn=output/cv-editor_data/02_curve生成（大まか）/16_新幹線_往復+仮時刻表
outdirn=output/cv-editor_data/02_curve生成（大まか）/20_在来線+新幹線

sh zairai_plus_shinkansen.sh ${zaidirn} ${shidirn} ${outdirn}
