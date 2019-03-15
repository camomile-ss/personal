# coding: utf-8

from util import create_co_matrix, ppmi, ppmi_text
from dataset import ptb
from sklearn.utils.extmath import randomized_svd
import numpy as np

if __name__ == '__main__':

    # ハイパパラメータ
    window_size = 2
    vec_size = 100

    # データload
    corpus, word_to_id, id_to_word = ptb.load_data()
    print(len(word_to_id))

    # 共起行列
    print('counting co_occurence..')
    c = create_co_matrix(corpus, vocab_size=len(word_to_id), window_size=window_size)
    print(c.shape)
    print(c)
    print(np.min(c))
    print(np.isinf(c).any())
    print(np.isnan(c).any())

    # ppmi
    print('calculating ppmi..')
    m = ppmi(c)
    #m = ppmi_text(c, verbose=True)
    print(m)
    print(np.isinf(m).any())
    print(np.isnan(m).any())

    # 次元削減 SVD
    print('calculating svd..')
    U, S, V = randomized_svd(m, n_components=vec_size)

    print(U.shape)

    # ひょうか


