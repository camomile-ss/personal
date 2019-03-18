# coding: utf-8

from util import create_co_matrix, ppmi, ppmi_text, most_similar
from dataset import ptb
from sklearn.utils.extmath import randomized_svd

if __name__ == '__main__':

    # ハイパパラメータ
    window_size = 2
    vec_size = 100

    # データload
    corpus, word_to_id, id_to_word = ptb.load_data()

    print('vocab size: {0}'.format(len(word_to_id)))
    print('corpus size: {0}'.format(len(corpus)))

    # 共起行列
    print('counting co_occurence..')
    c = create_co_matrix(corpus, vocab_size=len(word_to_id), window_size=window_size)

    # ppmi
    print('calculating ppmi (t) ..')
    m_t = ppmi_text(c, verbose=True)

    print('calculating ppmi (self) ..')
    m = ppmi(c)

    # 次元削減 SVD
    print('calculating svd..')
    U, S, V = randomized_svd(m, n_components=vec_size)

    U_t, S_t, V_t = randomized_svd(m_t, n_components=vec_size)

    # ひょうか
    querys = ['you', 'year', 'car', 'toyota']
    for q in querys:
        print('SVD (self ppmi)')
        most_similar(q, word_to_id, id_to_word, U)
        print('SVD (t ppmi)')
        most_similar(q, word_to_id, id_to_word, U_t)
