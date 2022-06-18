from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from collections import Counter
from num2words import num2words

import nltk
import os
import string
import numpy as np
import copy
import pandas as pd
import pickle
import re
import math
import json
from hunspell import Hunspell
import warnings
warnings.filterwarnings('ignore')

# %load_ext autotime


class MainProcess():
    def __init__(self):
        self.data = pd.read_csv('metadata/final_1.csv')
        self.filenames = self.data['filename'].to_list()
        self.years = self.data['filename'].to_list()
        self.titles = self.data['title'].to_list()

        with open('extracted_data/processed_text.data', 'rb') as f:
            self.processed_text = pickle.load(f)
        with open('extracted_data/processed_title.data', 'rb') as f:
            self.processed_title = pickle.load(f)
        with open('extracted_data/all_docs_info.json', 'r') as f:
            self.DF_tmp = json.load(f).get('DF')
        with open("extracted_data/tf_idf_scores.json", 'r', encoding="utf8") as j:
            self.TF_IDF = json.loads(j.read())
        self.vectorized_array = np.load('extracted_data/tf_idf_vectorized.npy')

    def convert_lower_case(self, data):
        return np.char.lower(data)

    def remove_stop_words(self, data):
        stop_words = stopwords.words('english')
        words = word_tokenize(str(data))
        new_text = ""
        for w in words:
            if w not in stop_words and len(w) > 1:
                new_text = new_text + " " + w
        return new_text

    def remove_punctuation(self, data):
        symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
        for i in range(len(symbols)):
            data = np.char.replace(data, symbols[i], ' ')
            data = np.char.replace(data, "  ", " ")
        data = np.char.replace(data, ',', '')
        return data

    def remove_apostrophe(self, data):
        return np.char.replace(data, "'", "")

    def stemming(self, data):
        stemmer = SnowballStemmer(language='english')

        tokens = word_tokenize(str(data))
        new_text = ""
        for w in tokens:
            new_text = new_text + " " + stemmer.stem(w)
        return new_text

    def stemming2(self, data):
        hobj = Hunspell('en_US')
        tokens = word_tokenize(str(data))
        new_text = ""
        for w in tokens:
            if len(hobj.stem(w)) > 0:
                new_text = new_text + " " + hobj.stem(w)[0]
            else:
                new_text = new_text + " " + w
        return new_text

    def convert_numbers(self, data):
        tokens = word_tokenize(str(data))
        new_text = ""
        for w in tokens:
            try:
                w = num2words(int(w))
            except:
                a = 0
            new_text = new_text + " " + w
        new_text = np.char.replace(new_text, "-", " ")
        return new_text

    def preprocess(self, data):
        data = self.convert_lower_case(data)
        data = self.remove_punctuation(data)  # remove comma seperately
        data = self.remove_apostrophe(data)
        data = self.remove_stop_words(data)
        data = self.convert_numbers(data)
        data = self.stemming2(data)
        data = self.remove_punctuation(data)
        data = self.convert_numbers(data)
        # needed again as we need to stem the words
        data = self.stemming2(data)
        # needed again as num2word is giving few hypens and commas fourty-one
        data = self.remove_punctuation(data)
        # needed again as num2word is giving stop words 101 - one hundred and one
        data = self.remove_stop_words(data)
        return data

    def cosine_sim(self, a, b):
        cos_sim = np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))
        return cos_sim

    def get_doc_freg_for_vector(self, token):
        try:
            c = self.DF_tmp[token]
        except:
            c = 0
        return c

    def gen_vector(self, tokens):
        total_vocab = [x for x in self.DF_tmp]
        Q = np.zeros((len(total_vocab)))

        counter = Counter(tokens)
        words_count = len(tokens)

        for token in np.unique(tokens):

            tf = counter[token]/words_count
            df = self.get_doc_freg_for_vector(token)
            idf = math.log((len(self.processed_text)+1)/(df+1))

            try:
                ind = total_vocab.index(token)
                Q[ind] = tf*idf
            except:
                pass
        return Q

    def matching_score(self, k, query):
        preprocessed_query = self.preprocess(query)
        tokens = word_tokenize(str(preprocessed_query))
        result = []
        query_weights = {}

        for idx, file in enumerate(self.TF_IDF):
            scores = file.get('scores')
            for key in scores:
                if key in tokens:
                    try:
                        query_weights[idx] += scores[key]
                    except:
                        query_weights[idx] = scores[key]

        query_weights = sorted(query_weights.items(),
                               key=lambda x: x[1], reverse=True)
        for i in query_weights[:k]:
            result.append(
                [self.filenames[i[0]], self.titles[i[0]], '%.3f' % (round(i[1], 5)*100)])
        return result

    def cosine_similarity(self, k, query):
        preprocessed_query = self.preprocess(query)
        tokens = word_tokenize(str(preprocessed_query))
        d_cosines = []
        result = []
        query_vector = self.gen_vector(tokens)

        for d in self.vectorized_array:
            d_cosines.append(self.cosine_sim(query_vector, d))
        out = np.array(d_cosines).argsort()[-k:][::-1]
        for idx in out:
            result.append([self.filenames[idx], self.titles[idx],
'%.3f' % (round(d_cosines[idx], 5)*100)])
            # print(self.filenames[idx], end=" ")
        return result


if __name__ == "__main__":
    process = MainProcess()
    # process.matching_score(10, "Ho Chi Minh the Greatest General")

    process.cosine_similarity(10, "Ho Chi Minh the Greatest General")
