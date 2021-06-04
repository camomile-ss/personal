#!/bin/bash

dirn=output_20201124
outdirn=${dirn}/for_ev-editor

if [ ! -d ${outdirn} ]; then
    mkdir ${outdirn}
fi

stin=${dirn}/STATION_CODE.txt
stout=${outdirn}/station_master.txt
rwin=${dirn}/RAILWAY.txt
rwout=${outdirn}/railway_master.txt
rsin=${dirn}/railstation.txt
rsout=${outdirn}/railstation_master.txt

cp ${stin} ${stout}
cp ${rwin} ${rwout}
cp ${rsin} ${rsout}
