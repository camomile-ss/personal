# coding: utf-8
'''
Created on Thu Jan 31 15:11:34 2019

@author: otani
'''

import numpy as np

class Sigmoid:
    def __init__(self):
        self.params = []
        
    def forward(self, x):
        return 1 / (1 + np.exp(-x))
    
class Affine:
    ''' 全結合層 '''
    def __init__(self, w, b):
        self.params = [w, b]
        
    def forward(self, x):
        w, b = self.params
        return np.dot(x, w) + b

class TwoLayersNet:
    def __init__(self, input_size, hidden_size, output_size):
        i, h, o = input_size, hidden_size, output_size
        
        w1 = np.random.randn(i, h)
        b1 = np.random.randn(h)
        w2 = np.random.randn(h, o)
        b2 = np.random.randn(o)

        self.layers = [
            Affine(w1, b1),
            Sigmoid(),
            Affine(w2, b2)
        ]        
        
        self.params = []
        for l in self.layers:
            self.params += l.params

    def predict(self, x):
        for l in self.layers:
            x = l.forward(x)
        return x

if __name__=='__main__':

    x = np.random.randn(10, 2)
    model = TwoLayersNet(2, 4, 3)
    result = model.predict(x)
    print(result)
    