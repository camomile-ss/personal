# coding: utf-8
'''
'''
import numpy as np
from layers import MatMul, SoftmaxWithLoss

if __name__ == '__main__':

    c0 = np.array([[1, 0, 0, 0, 0, 0, 0]])
    c1 = np.array([[1, 0, 1, 0, 0, 0, 0]])

    w_in = np.random.randn(7, 3)
    w_out = np.random.randn(3, 7)

    in_layer0 = MatMul(w_in)
    in_layer1 = MatMul(w_in)
    out_layer = MatMul(w_out)

    h0 = in_layer0.forward(c0)
    h1 = in_layer1.forward(c1)
    h = 0.5 * (h0 + h1)
    s = out_layer.forward(h)

    print(s)

    t = np.array([[0, 1, 0, 0, 0, 0, 0]])

    loss_layer = SoftmaxWithLoss()
    loss = loss_layer.forward(s, t)

    print(loss)