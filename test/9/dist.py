# coding: utf-8
'''
Created on Tue Jan 29 14:20:27 2019

@author: otani
'''
import sys
import numpy as np
from thin_out import approx_coord
#sys.path.append('../common')
#from common_linalg import dist_p_to_line2p

a = [35.7310181174,139.7958379984]
b = [35.7310573093,139.7958272696]
#a = [35.6958874538,139.744720459]  # 東京
#b = [34.697131568,135.4957580566]  # 大阪

a_ = approx_coord(a)
b_ = approx_coord(b)

d = np.linalg.norm(a_ - b_)

print(d)
