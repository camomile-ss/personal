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

def ppmi(c, eps=1e-8):
    '''
    正の相互情報量 positive pointwise mutual information
    c: 共起行列()
    '''
    c = c.astype(np.float32)
    n = np.sum(c)
    cx = np.sum(c, axis=1, keepdims=True)
    cy = np.sum(c, axis=0, keepdims=True)
    pmi = np.log2(n * c / (cx * cy) + eps, dtype=np.float32)
    m = np.maximum(pmi, 0)

    return m

def ppmi_debug(c, eps=1e-8):
    '''
    正の相互情報量 positive pointwise mutual information
    c: 共起行列()
    *** debug 用 ***
    '''
    debug_dir = 'chap2_debug_100/'

    c = c.astype(np.uint)  # uintだとptbデータMemory Error。float32がよさそう。
    n = np.sum(c)  #, dtype=np.int32)
    cx = np.sum(c, axis=1, keepdims=True)  #, dtype=np.int32)
    cy = np.sum(c, axis=0, keepdims=True)  #, dtype=np.int32)
    print('c; {0}, n: {1}, cx: {2}, cy: {3}'.format(c.dtype, n.dtype, cx.dtype, cy.dtype))

    np.savetxt(debug_dir + 'cx.tsv', cx, delimiter='\t')  #, fmt='%.3e')
    np.savetxt(debug_dir + 'cy.tsv', cy, delimiter='\t')  #, fmt='%.3e')

    wk1 = n * c  # cをastypeしないとint32になりあふれてマイナスになる
    wk2 = wk1 / cx
    wk3 = wk2 / cy
    wk4 = wk3 + eps
    print('n*c: {0}, n*c/cx: {1}, n*c/cx/cy: {2}, n*c/cx/cy+eps: {3}'.format(wk1.dtype, wk2.dtype, wk3.dtype, wk4.dtype))
    np.savetxt(debug_dir + 'wk1.tsv', wk1, delimiter='\t')  #, fmt='%.3e')
    np.savetxt(debug_dir + 'wk2.tsv', wk2, delimiter='\t')  #, fmt='%.3e')
    np.savetxt(debug_dir + 'wk3.tsv', wk3, delimiter='\t')  #, fmt='%.3e')
    np.savetxt(debug_dir + 'wk4.tsv', wk4, delimiter='\t')  #, fmt='%.3e')
    wk5 = n * c / (cx * cy) + eps
    print('n*c/(cx*cy)+eps: {0}'.format(wk5.dtype))
    np.savetxt(debug_dir + 'wk5.tsv', wk5, delimiter='\t')  #, fmt='%.3e')

    cx_cy = cx * cy
    np.savetxt(debug_dir + 'cx_cy.tsv', cx_cy, delimiter='\t')  #, fmt='%.3e')
    wk_ = n * c / cx_cy + eps
    np.savetxt(debug_dir + 'wk_.tsv', wk_, delimiter='\t')  #, fmt='%.3e')

    wk = n * c / cx / cy + eps
    #np.savetxt(debug_dir + 'wk.tsv', wk, delimiter='\t')  #, fmt='%.3e')
    print(np.isinf(wk).any())
    print(np.isnan(wk).any())
    pmi = np.log2(wk5, dtype=np.float32)
    #np.savetxt(debug_dir + 'pmi.tsv', pmi, delimiter='\t')  #, fmt='%.3e')

    #pmi = np.log2(n * c / cx / cy + eps, dtype=np.float32)
    m = np.maximum(pmi, 0)
    print('pmi: {0}, ppmi: {1}'.format(pmi.dtype, m.dtype))

    return m

def ppmi_text(c, verbose=False, eps=1e-8):
    ''' 著者さま提供のほう '''
    n = np.sum(c)
    cx = np.sum(c, axis=1)
    cy = np.sum(c, axis=0)
    if verbose:
        total = c.shape[0] * c.shape[1]
        print_span = -(-total // 100)

    m = np.zeros_like(c, dtype=np.float32)
    for i in range(c.shape[0]):
        for j in range(c.shape[1]):
            pmi = np.log2(n * c[i, j] / (cx[i] * cy[j]) + eps)
            m[i, j] = max(0, pmi)

            if verbose:
                cnt = i * c.shape[0] + j + 1
                if cnt % print_span == 0:
                    print('{0:.1f}% done'.format(cnt / total * 100))

    return m

def create_contexts_target(corpus, window_size=1):
    ''' corpus から contexts, target さくせい '''

    target = corpus[window_size: -window_size]
    contexts = []
    corpus = corpus.tolist()
    for i in range(window_size, len(corpus) - window_size):
        contexts.append(corpus[i-window_size: i] + corpus[i+1: i+1+window_size])

    return np.array(contexts), target

def create_contexts_target_text(corpus, window_size=1):
    ''' 著者さま提供のほう '''

    target = corpus[window_size: -window_size]
    contexts = []
    for i in range(window_size, len(corpus) - window_size):
        cs = []
        for t in range(-window_size, window_size + 1):
            if t ==0:
                continue
            cs.append(corpus[i+t])
        contexts.append(cs)

    return np.array(contexts), np.array(target)

def convert_one_hot(word_id, vocab_size):
    ''' 単語IDからone-hot表現に変換 '''

    one_hot_shape = word_id.shape + (vocab_size, )  # 変換後のshape
    word_id = word_id.reshape(-1)  # ひらたくする
    one_hot = [[1 if j==word_id[i] else 0 for j in range(vocab_size)]
               for i in range(len(word_id))]

    return np.array(one_hot, dtype=np.int32).reshape(one_hot_shape)

def convert_one_hot_text(corpus, vocab_size):
    '''one-hot表現への変換  ##著者さま提供のほう

    :param corpus: 単語IDのリスト（1次元もしくは2次元のNumPy配列）
    :param vocab_size: 語彙数
    :return: one-hot表現（2次元もしくは3次元のNumPy配列）
    '''
    N = corpus.shape[0]

    if corpus.ndim == 1:
        one_hot = np.zeros((N, vocab_size), dtype=np.int32)
        for idx, word_id in enumerate(corpus):
            one_hot[idx, word_id] = 1

    elif corpus.ndim == 2:
        C = corpus.shape[1]
        one_hot = np.zeros((N, C, vocab_size), dtype=np.int32)
        for idx_0, word_ids in enumerate(corpus):
            for idx_1, word_id in enumerate(word_ids):
                one_hot[idx_0, idx_1, word_id] = 1

    return one_hot

if __name__ == '__main__':

    corpus, word_to_id, id_to_word = preprocess('You say goodbye and I say hello.')
    #corpus, word_to_id, id_to_word = preprocess('ok')

    print(corpus)
    #print(word_to_id)
    #print(id_to_word)

    con, tar = create_contexts_target(corpus)
    #con_t, tar_t = create_contexts_target_text(corpus)

    print(con)
    print(type(con))
    print(tar)
    print(type(tar))
    #print('')
    #print(con_t)
    #print(type(con_t))
    #print(tar_t)
    #print(type(tar_t))

    con_o = convert_one_hot(con, len(word_to_id))
    tar_o = convert_one_hot(tar, len(word_to_id))
    con_t = convert_one_hot_text(con, len(word_to_id))
    tar_t = convert_one_hot_text(tar, len(word_to_id))

    print(con_o)
    print(tar_o)
    print(con_t)
    print(tar_t)

    """
    co_matrix = create_co_matrix(corpus, len(word_to_id), 1)

    print(co_matrix)

    print(cos_similarity(co_matrix[0], co_matrix[4]))

    m = ppmi(co_matrix)
    print(m)
    print(ppmi_text(co_matrix, verbose=True))

    # 時間比較
    import timeit
    number = 10000
    t1 = timeit.timeit('ppmi(co_matrix)', globals=globals(), number=number)
    t2 = timeit.timeit('ppmi_text(co_matrix)', globals=globals(), number=number)
    print(t1)  # 0.2701249169986113
    print(t2)  # 1.5738809940012288

    # SVD
    U, S, V = np.linalg.svd(m)

    print(U)
    print(S)
    print(V)

    # plot
    import matplotlib.pyplot as plt
    for word, word_id in word_to_id.items():
        plt.annotate(word, (U[word_id, 0], U[word_id, 1]))
    plt.scatter(U[:,0], U[:,1], alpha=0.5)
    plt.savefig('print/chap2_plt.png')

    m_ = U[:,:2]

    print('co_matrix')
    most_similar('you', word_to_id, id_to_word, co_matrix)
    print('ppmi')
    most_similar('you', word_to_id, id_to_word, m)
    print('svd')
    most_similar('you', word_to_id, id_to_word, m_)
    """