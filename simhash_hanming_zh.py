#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from hashlib import md5
import sys
import jieba.analyse
from scipy.spatial import distance
import numpy as np
import time
class Token:

    def __init__(self, hash_list, weight):
        self.hash_list = hash_list
        self.weight = weight

def tokenize(doc):
    doc = filter(None, doc)
    return doc

def md5Hash(token):
    h = bin(int(md5(token.encode("utf-8")).hexdigest(), 16))
    return h[2:]

def hash_threshold(token_dict, fp_len):
    """
    Iterate through the token dictionary multiply the hash lists with the weights
    and apply the binary threshold
    """
    sum_hash = [0] * fp_len
    for _, token in token_dict.items():
        sum_hash = [ x + token.weight * y for x, y in zip(sum_hash, token.hash_list)]

    # apply binary threshold
    for i, ft in enumerate(sum_hash):
        if ft > 0:
            sum_hash[i] = 1
        else:
            sum_hash[i] = 0
    return sum_hash

def binconv(fp, fp_len):
    """
    Converts 0 to -1 in the tokens' hashes to facilitate
    merging of the tokens' hashes later on.
    input  : 1001...1
    output : [1,-1,-1, 1, ... , 1]
    """
    vec = [1] * fp_len
    for indx, b in enumerate(fp):
        if b == '0':
            vec[indx] = -1
    return vec


def calc_weights(terms, fp_len):
    """
    Calculates the weight of each one of the tokens. In this implementation
    these weights are equal to the term frequency within the document.

    :param tokens: A list of all the tokens (words) within the document
    :fp_len: The length of the Simhash values
    return dictionary "my_term": Token([-1,1,-1,1,..,-1], 5)
    """
    term_dict = {}
    for term in terms:
        # get weights
        if term not in term_dict:
            fp_hash = md5Hash(term).zfill(fp_len)
            fp_hash_list = binconv(fp_hash, fp_len)
            token = Token(fp_hash_list, 0)
            term_dict[term] = token
        term_dict[term].weight += 1
    return term_dict

def simhash(doc, fp_len=128):
    """
    :param doc: The document we want to generate the Simhash value
    :fp_len: The number of bits we want our hash to be consisted of.
                Since we are hashing each token of the document using
                md5 (which produces a 128 bit hash value) then this
                variable fp_len should be 128. Feel free to change
                this value if you use a different hash function for
                your tokens.
    :return The Simhash value of a document ex. '0000100001110'
    """
    tokens = tokenize(doc)
    token_dict = calc_weights(tokens, fp_len)
    fp_hash_list = hash_threshold(token_dict, fp_len)
    fp_hast_str =  ''.join(str(v) for v in fp_hash_list)
    return fp_hast_str

if __name__ == '__main__':
    start = time.time()
    filename = 'ceshi_zh1.txt'
    probename = 'probe.txt'
    with open(probename, 'r', encoding='utf-8') as file_to_read:
        probe_text = file_to_read.readline()
        probe_key = jieba.analyse.extract_tags(probe_text, 20)
        print(probe_key)
        probe_hash = simhash(probe_key)
    with open(filename, 'r',encoding='utf-8') as file_to_read:
        binary_hash = []
        while True:
            line = file_to_read.readline()  # 整行读取数据
            if not line:
                break
                pass
            line = jieba.analyse.extract_tags(line, 20)
            print(line)
            binary_hash.append(simhash(line))
    dis_list = []
    for i in range(len(binary_hash)):
        dis = 1-distance.cdist(np.array([list(binary_hash[i])]), np.array([list(probe_hash)]), 'hamming')
        dis_list.append(dis)   #dis = distance.cdist(np.array([list(binary_hash[0])]), np.array([list(binary_hash[1])]), 'hamming')
    print(dis_list)
    end = time.time()
    print(str(end - start))