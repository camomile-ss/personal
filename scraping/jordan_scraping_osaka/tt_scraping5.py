#!/usr/bin/python
# coding: utf-8

import argparse
import os
import pickle
from vehicle import Vehicle
from lines import Lines, Line_local, Line_rapid, ptn_no, sepID

if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('indir', help='tohoku/v1')
    psr.add_argument('outdir', help='tohoku/v2')
    args = psr.parse_args()
    indir, outdir = args.indir, args.outdir

    vehicle_pickle_fn = os.path.join(indir, 'pickle/vehicles.pickle')
    lines_pickle_fn = os.path.join(indir, 'pickle/lines.pickle')
    
    testfn = 'tohoku/tt_scraping5_test/input.txt'

    """
    vehicles = pickle.load(open(vehicle_pickle_fn, 'rb'))

    for line, v in vehicles.items():
        print(line)
        for direc, v2 in v.items():
            print('  ', direc)
            for i, vehi in v2.items():
                if not vehi.lineIDs:
                    print('    ', i, vehi.lineIDs)
    """

    lines = pickle.load(open(lines_pickle_fn, 'rb'))

    sorted_lines = sorted(lines.lines.values(), key=lambda x: (ptn_no(x.ID)))
    sorted_lines = sorted(sorted_lines, key=lambda x: x.parentID if x.__class__==Line_rapid else x.ID)
    #for l in sorted_lines:
    #    print(l.ID, l.name, l.parentID if l.__class__==Line_pass else l.ptn_cnt, l.reverseID or '-')

    with open(testfn, 'r') as f:
        indata = [[x.strip() for x in l.split('\t')] for l in f]

    done_list = []
    for l in indata:
        if l[0]=='setname':
            _, ID, name = l
            flg, v = lines.set_name(ID, name)
            if flg < 0:
                print('err {0} ID:{1} name:{2} return:{3}'.format(flg, ID, name, v))
        elif l[0]=='changeid':
            _, ID, newID = l
            if (ID, newID) in done_list:
                print('{0} -> {1} already changed'.format(ID, newID))
                continue
            flg, v = lines.change_ID(ID, newID)
            if flg < 0:
                print(v)
            if flg == 0:
                done_list.append(v)
        elif l[0]=='addnewline':
            _, ID, parentID, name, *stop_stations = l
            if ID == '':
                ID = None
            new_line = lines.add_line(ID, name, stop_stations, parentID=parentID)
            if type(new_line) is int:
                print('err {0} ID:{1} parentID:{2} name: {3}'.format(new_line, ID, parentID, name))
            else:
                print(new_line.stations)
                if new_line.__class__ == Line_rapid:
                    print(new_line.stop_stations)
                    print(new_line.pass_stations)

    sorted_lines = sorted(lines.lines.values(), key=lambda x: (ptn_no(x.ID)))
    sorted_lines = sorted(sorted_lines, key=lambda x: x.parentID if x.__class__==Line_rapid else x.ID)
    for l in sorted_lines:
        print(l.ID, l.name, l.parentID if l.__class__==Line_rapid else l.ptn_cnt, l.reverseID or '-')
