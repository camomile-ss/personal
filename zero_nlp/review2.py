# coding: utf-8
'''
Created on Tue Feb 12 16:23:47 2019

@author: otani
'''
import numpy as np

class Relu:
    def __init__(self):
        self.mask = None

    def forward(self, x):
        self.mask = (x <= 0)  # 0以下->Trueを保持
        y = x.copy()
        y[self.mask] = 0  # 0以下は0
        return y

    def backward(self, dy):
        dx = dy.copy()
        dx[self.mask] = 0  # 0以下は0
        return dx

if __name__ == '__main__':

    x = np.random.randn(10,3)
    print(x)

    relu_layer = Relu()

    y = relu_layer.forward(x)
    print(y)

    dy = np.ones((10,3))

    dx = relu_layer.backward(dy)
    print(dx)

