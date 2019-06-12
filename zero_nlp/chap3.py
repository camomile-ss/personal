# coding: utf-8
from util import preprocess, create_contexts_target, convert_one_hot

if __name__ == '__main__':

    text = 'You say goodbye and I say hello.'
    corpus, word_to_id, id_to_word = preprocess(text)

    contexts, target = create_contexts_target(corpus)

    contexts = convert_one_hot(contexts, vocab_size=len(word_to_id))
    target = convert_one_hot(target, vocab_size=len(word_to_id))

    print(contexts)
    print(target)
