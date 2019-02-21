# coding: utf-8
import sys
from trainers import Trainer
from two_layers_net import TwoLayersNet
from optimizers import SGD
from dataset import spiral

if __name__ == '__main__':

    max_epoch = 300
    batch_size = 30
    hidden_size = 10
    learning_rate = 1.0

    # データ, モデル, optimizer
    x, t = spiral.load_data()
    model = TwoLayersNet(input_size=2, hidden_size=hidden_size, output_size=3)
    opt = SGD(learning_rate)

    # 学習
    trainer = Trainer(model, opt)
    trainer.fit(x, t, max_epoch, batch_size, eval_interval=10)

    # plot
    trainer.plot('chap1.png')
