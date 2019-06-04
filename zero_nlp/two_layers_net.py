# coding: utf-8
import numpy as np
from layers import Affine, Sigmoid, SoftmaxWithLoss

class TwoLayersNet:
    def __init__(self, input_size, hidden_size, output_size):
        I, H, O = input_size, hidden_size, output_size

        w1 = np.random.randn(I, H) * 0.01
        b1 = np.zeros(H)  #np.random.randn(H)
        w2 = np.random.randn(H, O) * 0.01
        b2 = np.zeros(O)  #np.random.randn(O)

        self.layers = [
            Affine(w1, b1),
            Sigmoid(),
            Affine(w2, b2)
        ]
        self.loss_layer = SoftmaxWithLoss()

        self.params, self.grads = [], []
        for l in self.layers:
            self.params += l.params
            self.grads += l.grads  # 勾配まとめはこのときだけ。-> 各layerの勾配更新は参照場所を動かさないようにする。

    def predict(self, x):
        for l in self.layers:
            x = l.forward(x)
        return x

    def forward(self, x, t):
        score = self.predict(x)
        #print('t:', t)  # test
        #print('score:', score)  # test
        loss = self.loss_layer.forward(score, t)
        return loss

    def backward(self, dl):  # dl=1):
        dl = self.loss_layer.backward(dl)
        for l in self.layers[::-1]:
            dl = l.backward(dl)
        #return dl

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
