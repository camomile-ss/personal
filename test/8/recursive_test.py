#!/usr/bin/python
# coding: utf-8



def rec(tlist):

    result = [[k] + rec(v) for k, v in tlist.items() if type(v) is dict]

    return result

if __name__ == '__main__':

    testlist = {'a1': {'b1': {'c1': {}, 'c2': {}}, 'b2': {'c3': {}, 'c4':{}}, 'a2': {'b3':{}, 'b4':{}}}}

    rec(testlist)
