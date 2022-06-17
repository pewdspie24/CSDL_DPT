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

def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(data, key=alphanum_key)

def print_doc(id):
    print(dataset[id])
    file = open(dataset[id][0], 'r', encoding='utf8')
    text = file.read().strip()
    file.close()
    print(text)

def convert_lower_case(data):
    return np.char.lower(data)

def remove_stop_words(data):
    stop_words = stopwords.words('english')
    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + " " + w
    return new_text

def remove_punctuation(data):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ',', '')
    return data

def remove_apostrophe(data):
    return np.char.replace(data, "'", "")

def stemming(data):
    stemmer= SnowballStemmer(language='english')
    
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        new_text = new_text + " " + stemmer.stem(w)
    return new_text

def stemming2(data):
    hobj = Hunspell('en_US')
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        if len(hobj.stem(w)) > 0:
            new_text = new_text + " " + hobj.stem(w)[0]
        else:
            new_text = new_text + " " + w
    return new_text

def convert_numbers(data):
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

def preprocess(data):
    data = convert_lower_case(data)
    data = remove_punctuation(data) #remove comma seperately
    data = remove_apostrophe(data)
    data = remove_stop_words(data)
    data = convert_numbers(data)
    data = stemming2(data)
    data = remove_punctuation(data)
    data = convert_numbers(data)
    data = stemming2(data) #needed again as we need to stem the words
    data = remove_punctuation(data) #needed again as num2word is giving few hypens and commas fourty-one
    data = remove_stop_words(data) #needed again as num2word is giving stop words 101 - one hundred and one
    return data

def get_doc_freq(word):
    try:
        c = DF[word]
    except:
        c = 0
    return c

if __name__ == "__main__":
    data = pd.read_csv('metadata/final_1.csv')
    filenames = data['filename'].to_list()
    years = data['filename'].to_list()
    titles = data['title'].to_list()
    dataset = []

    for filename in sorted_alphanumeric(os.listdir('txt')):
        dataset.append(('txt/'+filename, titles[int(filenames.index(filename))]))
    
    processed_text = []
    processed_title = []
    N = len (dataset)

    for i in dataset[:N]:
        file = open(i[0], 'r', encoding="utf8", errors='ignore')
        text = file.read().strip()
        file.close()

        processed_text.append(word_tokenize(str(preprocess(text))))
        processed_title.append(word_tokenize(str(preprocess(i[1]))))
    
    with open('extracted_data/processed_text.data', 'wb') as f:
        pickle.dump(processed_text, f)
    with open('extracted_data/processed_title.data', 'wb') as f:
        pickle.dump(processed_title, f)
    
    DF = {}
    for i in range(N):
        tokens = processed_text[i]
        for w in tokens:
            try:
                DF[w].add(i)
            except:
                DF[w] = {i}

        tokens = processed_title[i]
        for w in tokens:
            try:
                DF[w].add(i)
            except:
                DF[w] = {i}
    for i in DF:
        DF[i] = len(DF[i])
    
    total_vocab_size = len(DF)
    total_vocab = [x for x in DF]

    doc = 0
    TF_IDF = {}
    files_list = []
    total_count_all = 0
    idf_all = {}

    for i in range(N):
        tokens = processed_text[i]
        counter = Counter(tokens + processed_title[i])
        words_count = len(tokens + processed_title[i])
        tfs = {}
        counters = {}
        total_count = 0
        for token in np.unique(tokens):
            tf = counter[token]/words_count
            tfs.update({token:tf})
            counters.update({token:counter[token]})
            total_count += counter[token]
            df = get_doc_freq(token)
            idf = np.log((N+1)/(df+1))
            idf_all.update({token:idf})
            TF_IDF[doc, token] = tf*idf

        tmp_dict = {'name': filenames[i], "words_counting":counters, "total_count":total_count, "TF_scores":tfs}
        files_list.append(tmp_dict)
        total_count_all += total_count
        doc += 1    
    all_list = {'name': 'ALL_Documents', 'total_count': total_count_all, 'DF': DF, 'IDF_scores': idf_all}

    doc = 0
    TF_IDF_title = {}
    files_list_title = []
    total_count_all_title = 0
    idf_all_title = {}

    for i in range(N):
        tokens = processed_title[i]
        counter = Counter(tokens + processed_text[i])
        words_count = len(tokens + processed_text[i])
        tfs = {}
        counters = {}
        total_count = 0
        for token in np.unique(tokens):
            tf = counter[token]/words_count
            tfs.update({token:tf})
            counters.update({token:counter[token]})
            total_count += counter[token]
            df = get_doc_freq(token)
            idf = np.log((N+1)/(df+1)) #numerator is added 1 to avoid negative values
            TF_IDF_title[doc, token] = tf*idf
        tmp_dict = {'name': filenames[i], "words_counting":counters, "total_count":total_count, "TF_scores":tfs}
        files_list_title.append(tmp_dict)
        doc += 1

    with open('extracted_data/all_docs_info.json', 'w') as f:
        f.write(json.dumps(all_list, indent=4))
    with open('extracted_data/all_text_info.json', 'w') as f:
        f.write(json.dumps(files_list, indent=4))
    with open('extracted_data/all_title_info.json', 'w') as f:
        f.write(json.dumps(files_list_title, indent=4))

    tf_idf_tmp = copy.deepcopy(TF_IDF)
    tf_idf_title_tmp = copy.deepcopy(TF_IDF_title)
    TF_IDF = copy.deepcopy(tf_idf_tmp)
    TF_IDF_title = copy.deepcopy(tf_idf_title_tmp)

    alpha = 0.4
    for i in TF_IDF:
        TF_IDF[i] *= alpha
    for i in TF_IDF_title:
        try:
            TF_IDF[i] += TF_IDF_title[i] * (1-alpha)
        except KeyError:
            continue
    TF_IDF_tmp = copy.deepcopy(TF_IDF)

    vectorized_array = np.zeros((N, total_vocab_size))
    for i in TF_IDF_tmp:
        try:
            ind = total_vocab.index(i[1])
            vectorized_array[i[0]][ind] = TF_IDF_tmp[i]
        except:
            pass
    
    doc_id = 0
    score_dict = {}
    tmp_dict_tfidf = {}
    tfidf_list = []
    for i in TF_IDF:
        if i[0] != doc_id:
            tmp_dict_tfidf.update({"name": filenames[doc_id], "scores": score_dict})
            tfidf_list.append(tmp_dict_tfidf)
            doc_id = i[0]
            tmp_dict_tfidf = {}
            score_dict = {}
        doc_name = filenames[i[0]]
        token = i[1]
        score_dict.update({token:TF_IDF[i]})
    
    with open('extracted_data/tf_idf_scores.json', 'w') as f:
        f.write(json.dumps(tfidf_list, indent=4))
    with open('extracted_data/tf_idf_vectorized.npy', 'wb') as f:
        np.save(f, vectorized_array)