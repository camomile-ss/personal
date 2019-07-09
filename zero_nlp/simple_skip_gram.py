# coding: utf-8
import numpy as np
from layers import MatMul, SoftmaxWithLoss

class SimpleSkipGram:
    def __init__(self, vocab_size, hidden_size):
        # おもみ
        w_in = 0.01 * np.random.randn(vocab_size, hidden_size).astype('f')
        w_out = 0.01 * np.random.randn(hidden_size, vocab_size).astype('f')

        # layers
        self.in_layer = MatMul(w_in)
        self.out_layer = MatMul(w_out)

        # おもみ、勾配 まとめ
        layers = [self.in_layer, self.out_layer]
        self.params, self.grads = [], []
        for l in layers:
            self.params += l.params
            self.grads += l.grads

        # loss
        self.loss_layer0 = SoftmaxWithLoss()
        self.loss_layer1 = SoftmaxWithLoss()
        # 極限でコンテキストの各単語の確率 0.5。
        # softmax->*2->lossでも一律ln2引くようだから同じたぶん。

        # 単語の分散表現
        self.word_vecs = w_in

    def forward(self, contexts, target):
        h = self.in_layer.forward(target)
        s = self.out_layer.forward(h)
        l0 = self.loss_layer0.forward(s, contexts[:, 0])
        l1 = self.loss_layer1.forward(s, contexts[:, 1])
        loss = l0 + l1
        return loss

    def backward(self, dl=1):
        ds0 = self.loss_layer0.backward(dl)
        ds1 = self.loss_layer1.backward(dl)
        ds = ds0 + ds1
        dh = self.out_layer.backward(ds)
        self.in_layer.backward(dh)
