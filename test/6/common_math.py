# coding: utf-8
'''
Created on Mon Jan 28 16:00:15 2019

@author: otani
'''

import numpy as np

def dist_p_to_line2p(p, p1, p2):
    '''
    p1とp2を結ぶ直線と、点pの距離
    '''
    return np.linalg.norm(np.cross(p-p1, p2-p1))/np.linalg.norm(p2-p1)

if __name__ == '__main__':
    
    print(dist_p_to_line2p(np.array([4,5]), np.array([2,2]), np.array([6,4])))
    print(dist_p_to_line2p(np.array([1,1]), np.array([0,0]), np.array([0,2])))
    print(dist_p_to_line2p(np.array([0,1]), np.array([0,0]), np.array([1,1])))
    
    