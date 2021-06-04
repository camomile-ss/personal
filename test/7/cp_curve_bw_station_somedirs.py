#!/usr/bin/python
# coding: utf-8

import argparse
import os
import sys
from cp_curve_bw_station import backup, mk_org_curve, read_data, cp_curve, write_data

def read_conf(confn):

    with open(confn, 'r', encoding='utf-8') as f:
        dat = [x.strip() for x in f]

    epd, ed, od, ls, rev, nomid = '[edit parent dir]', '[edit dir]', '[orginal dir]', \
                                  '[linenames]', '[rev]', '[nomid]'

    edit_parent_dir = dat[dat.index(epd) + 1] if epd in dat else '.'
    edit_dirs = dat[dat.index(ed) + 1: dat.index(od)]
    edit_dirs = [edit_parent_dir + '/' + x for x in edit_dirs]
    org_dir = dat[dat.index(od) + 1]
    linenames = dat[dat.index(ls) + 1: dat.index(rev)]
    rev = int(dat[dat.index(rev) + 1])
    nomid = int(dat[dat.index(nomid) + 1])

    return edit_dirs, org_dir, linenames, rev, nomid

def main():

    psr = argparse.ArgumentParser()
    psr.add_argument('-c', '--confname', default='./cp_curve_bw_station_somedirs.conf')
    args = psr.parse_args()
    confn = args.confname

    edit_dirs, org_dir, linenames, rev, nomid = read_conf(confn)
    orgfn = os.path.join(org_dir, 'curve_master.txt')
    org_curve_bw_station = mk_org_curve(orgfn, linenames, nomid)
    for ed in edit_dirs:
        backup(ed)
        editfn = os.path.join(ed, 'curve_master.txt')
        indata = read_data(editfn)
        outdata = cp_curve(indata, org_curve_bw_station, rev)
        write_data(editfn, outdata)

if __name__ == '__main__':

    main()

