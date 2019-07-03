# coding: utf-8
import numpy as np
import collections
from layers import Embedding, SigmoidWithLoss
from config import GPU

class EmbeddingDot:
    def __init__(self, w):
        self.embed = Embedding(w)
        self.params = self.embed.params
        self.grads = self.embed.grads
        self.cache = None

    def forward(self, h, idx):
        w_idx = self.embed.forward(idx)
        s = np.sum(h * w_idx, axis=1)
        self.cache = (h, w_idx)
        return s

    def backward(self, ds):
        ds = ds.reshape(ds.shape[0], 1)  # ???
        h, w_idx = self.cache
        dw_idx = ds * h
        self.embed.backward(dw_idx)
        dh = ds * w_idx
        return dh

class UnigramSampler:
    def __init__(self, corpus, power, sample_size):
        self.sample_size = sample_size
        self.vocab_size = corpus.max() + 1  # 単語数
        # 確率分布 (x: word id)
        self.word_p = np.array([np.count_nonzero(corpus==x) for x in range(self.vocab_size)])
        self.word_p = np.power(self.word_p, power)
        self.word_p /= np.sum(self.word_p)

    def get_negative_sample(self, target):
        n = len(target)  # batch size

        negative_sample = np.zeros((n, self.sample_size), dtype=np.int32)
        for i in range(n):
            p = self.word_p.copy()
            p[target[i]] = 0  # targetの確率をゼロに
            p /= np.sum(p)
            negative_sample[i, :] = np.random.choice(self.vocab_size, size=self.sample_size, replace=False, p=p)

        return negative_sample

class UnigramSampler_text:
    ''' 著者さま提供のほう '''
    def __init__(self, corpus, power, sample_size):
        self.sample_size = sample_size
        self.vocab_size = None
        self.word_p = None

        counts = collections.Counter()
        for word_id in corpus:
            counts[word_id] += 1

        vocab_size = len(counts)
        self.vocab_size = vocab_size

        self.word_p = np.zeros(vocab_size)
        for i in range(vocab_size):
            self.word_p[i] = counts[i]

        self.word_p = np.power(self.word_p, power)
        self.word_p /= np.sum(self.word_p)

    def get_negative_sample(self, target):
        batch_size = target.shape[0]

        if not GPU:
            negative_sample = np.zeros((batch_size, self.sample_size), dtype=np.int32)

            for i in range(batch_size):
                p = self.word_p.copy()
                target_idx = target[i]
                p[target_idx] = 0
                p /= p.sum()
                negative_sample[i, :] = np.random.choice(self.vocab_size, size=self.sample_size, replace=False, p=p)
        else:
            # GPU(cupy）で計算するときは、速度を優先
            # 負例にターゲットが含まれるケースがある
            negative_sample = np.random.choice(self.vocab_size, size=(batch_size, self.sample_size),
                                               replace=True, p=self.word_p)

        return negative_sample

class NegativeSamplingLoss:
    def __init__(self, w, corpus, power=0.75, sample_size=5):
        self.sample_size = sample_size
        self.sampler = UnigramSampler(corpus, power, sample_size)
        self.loss_layers = [SigmoidWithLoss() for _ in range(sample_size + 1)]  # 正例1個, 負例指定数
        self.embed_dot_layers = [EmbeddingDot(w) for _ in range(sample_size + 1)]
        self.params, self.grads = [], []
        for layer in self.embed_dot_layers:
            self.params += layer.params
            self.grads += layer.grads

    def forward(self, h, target):
        negative_sample = self.sampler.get_negative_sample(target)

        # 正例
        positive_label = np.ones(len(target), dtype=np.int32)
        s = self.embed_dot_layers[0].forward(h, target)
        loss = self.loss_layers[0].forward(s, positive_label)

        # 負例
        negative_label = np.zeros(len(target), dtype=np.int32)
        for i in range(self.sample_size):
            s = self.embed_dot_layers[i+1].forward(h, negative_sample[:, i])
            loss += self.loss_layers[i+1].forward(s, negative_label)

        return loss

    def backward(self, dl):
        dh = 0
        for l0, l1 in zip(self.loss_layers, self.embed_dot_layers):
            ds = l0.backward(dl)
            dh += l1.backward(ds)
        return dh

if __name__ == '__main__':

    corpus = np.array([0,1,2,3,4,2,3,5,0,1,2])
    power=0.75
    sample_size=2

    w = np.random.randn(6,3)
    nsl_layer = NegativeSamplingLoss(w, corpus, power, sample_size)

    print(id(w))
    print(id(nsl_layer.embed_dot_layers[0].params))
    print(id(nsl_layer.embed_dot_layers[0].params[0]))
    print(id(nsl_layer.embed_dot_layers[1].params))
    print(id(nsl_layer.embed_dot_layers[1].params[0]))
    print(id(nsl_layer.embed_dot_layers[2].params))
    print(id(nsl_layer.embed_dot_layers[2].params[0]))

    """
    sampler = UnigramSampler(corpus, power, sample_size)
    sampler_text = UnigramSampler_text(corpus, power, sample_size)

    print(sampler.word_p)
    print(sampler_text.word_p)
    print(sampler.get_negative_sample(np.array([0,2,4])))
    print(sampler_text.get_negative_sample(np.array([0,2,4])))
    """