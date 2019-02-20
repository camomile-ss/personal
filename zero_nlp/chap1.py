# coding: utf-8
import numpy as np
from layers import Affine, Sigmoid

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
    print(model.params)
    print()
    for i in range(len(model.layers)):
        print(i, model.layers[i].params)
        print()

    score = model.predict(x)
    print(score)

