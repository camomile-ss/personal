#!/bin/bash

indirn=output_20201124/for_ev_editor_scd整理後/分割_mod_マージ
outdirn=output_20201124/for_ev_editor_scd整理後/分割_mod_マージ_往復

python cvdata_add_reverse.py ${indirn} ${outdirn}
