# coding: utf-8
import re
import numpy as np

def preprocess(text):

    text = text.lower()

    #words = re.split(r'(\W+)?', text)  # <- これだとだめ
    # 単語間のスペースもリストに残る。カッコついてるから。
    # 最後の.もマッチするから最後に空文字列が入る。
    # ほんとうは各文字間もマッチするから将来は1文字ずつ分割されるようになる(FutureWarning出る)。

    words = [w for wk in re.split(r'\s', text) for w in re.split(r'(\W+)', wk) if w != '']

    word_to_id = {}
    id_to_word = {}

    for w in words:
        if not w in word_to_id:
            new_id = len(word_to_id)
            word_to_id[w] = new_id
            id_to_word[new_id] = w

    corpus = np.array([word_to_id[w] for w in words])

    return corpus, word_to_id, id_to_word

def create_co_matrix(corpus, vocab_size, window_size):
    ''' 共起行列 '''
    co_matrix = np.zeros((vocab_size, vocab_size), dtype=np.int32)

    for idx, word_id in enumerate(corpus):
        for i in range(1, window_size+1):

            left_idx, right_idx = idx - i, idx + i

            if left_idx >= 0:
                co_matrix[word_id, corpus[left_idx]] += 1
            if right_idx < len(corpus):
                    co_matrix[word_id, corpus[right_idx]] += 1

    return co_matrix

def cos_similarity(x, y, eps=1e-8):
    ''' コサイン類似度 '''
    x_ = x / (np.sqrt(np.sum(x**2)) + eps)  # x / (np.linalg.norm(x) + eps)
    y_ = y / (np.sqrt(np.sum(y**2)) + eps)  # y / (np.linalg.norm(y) + eps)

    return np.dot(x_, y_)

def most_similar(query, word_to_id, id_to_word, word_matrix, top=5):
    '''
    類似度上位の単語を表示
        query: 基準の単語
    '''
    if not query in word_to_id:
        print('{0} is not found.'.format(query))
        return

    query_id = word_to_id[query]
    query_vec = word_matrix[query_id]

    # コサイン類似度
    simi = np.zeros(len(word_to_id))
    for i, vec in enumerate(word_matrix):
        simi[i] = cos_similarity(query_vec, vec)

    order = simi.argsort()[::-1]  # 大きい順

    # 上位表示
    print('[top {0}]  query: {1}'.format(top, query))
    cnt = 0
    for o in order:
        if o == query_id:
            continue

        cnt += 1
        print('({0}) {1:10} similarity: {2}'.format(cnt, id_to_word[o], simi[o]))

        if cnt >= top:
            return

if __name__ == '__main__':

    corpus, word_to_id, id_to_word = preprocess('You say goodbye and I say hello.')

    print(corpus)
    print(word_to_id)
    print(id_to_word)

    co_matrix = create_co_matrix(corpus, len(word_to_id), 1)

    print(co_matrix)

    print(cos_similarity(co_matrix[0], co_matrix[4]))

    most_similar('you', word_to_id, id_to_word, co_matrix)
