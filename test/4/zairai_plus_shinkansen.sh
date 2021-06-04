#!/bin/bash

zaidirn=$1
shidirn=$2
outdirn=$3

if [ ! -d ${outdirn} ]; then
    mkdir ${outdirn}
fi

trfn=transporter_master.txt
stfn=station_master.txt
rwfn=railway_master.txt
rtfn=railtransporter_master.txt
rsfn=railstation_master.txt
cvfn=curve_master.txt
ttfn=timetable_master.txt

tempfn=${outdirn}/temp.txt

# transporter
fn=${trfn}
tr -d "\r" <${zaidirn}/${fn} > ${tempfn}
tr -d "\r" <${shidirn}/${fn} >> ${tempfn}
sort -k 1 -t \t -n ${tempfn} | uniq > ${outdirn}/${fn}

# station
fn=${stfn}
tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
tr -d "\r" <${shidirn}/${fn} > ${tempfn}
tail -n +2 ${tempfn} >> ${outdirn}/${fn}  # 後半はヘッダ飛ばす 

# railway
fn=${rwfn}
tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
tr -d "\r" <${shidirn}/${fn} >> ${outdirn}/${fn}

# railtransporter
fn=${rtfn}
tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
tr -d "\r" <${shidirn}/${fn} >> ${outdirn}/${fn}

# railstation
fn=${rsfn}
tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
tr -d "\r" <${shidirn}/${fn} >> ${outdirn}/${fn}

# curve
fn=${cvfn}
if [ -f ${zaidirn}/${fn} ]; then
    tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
    if [ -f ${shidirn}/${fn} ]; then
        tr -d "\r" <${shidirn}/${fn} >> ${outdirn}/${fn}
    fi
elif [ -f ${shidirn}/${fn} ]; then
    tr -d "\r" <${shidirn}/${fn} > ${outdirn}/${fn}
fi

# timetable
fn=${ttfn}
if [ -f ${zaidirn}/${fn} ]; then
    tr -d "\r" <${zaidirn}/${fn} > ${outdirn}/${fn}
    if [ -f ${shidirn}/${fn} ]; then
        tr -d "\r" <${shidirn}/${fn} >> ${outdirn}/${fn}
    fi
elif [ -f ${shidirn}/${fn} ]; then
    tr -d "\r" <${shidirn}/${fn} > ${outdirn}/${fn}
fi

rm ${tempfn}
