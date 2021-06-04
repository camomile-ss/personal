#!/bin/bash

indirn=output_20201124/for_ev_editor_新幹線/中間点なし_片道
outdirn=output_20201124/for_ev_editor_新幹線/中間点なし_往復

python cvdata_add_reverse.py ${indirn} ${outdirn}
