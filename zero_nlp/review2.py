# coding: utf-8
'''
Created on Tue Feb 12 16:23:47 2019

@author: otani
'''
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Relu:
    def __init__(self):
        self.params = []
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

class Sigmoid:
    def __init__(self):
        self.params = []
        self.y = None

    def forward(self, x):
        y = sigmoid(x)
        self.y = y
        return y

    def backward(self, dy):
        dx = self.y * (1 - self.y) * dy
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

