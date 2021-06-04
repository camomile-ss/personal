#!/bin/bash

indirn=output_20201124/for_ev_editor_scd整理後/分割_mod
outdirn=output_20201124/for_ev_editor_scd整理後/分割_mod_マージ

python cvdata_merge.py ${indirn} ${outdirn}
