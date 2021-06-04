#!/bin/bash

inf=wk_20181220viewer/curve_data_20190125_2.txt
outf=wk_20181220viewer/curve_data_20190125_3.txt
route=[京成]本線_0  # コピー元

python reverse.py ${inf} ${outf} ${route}


