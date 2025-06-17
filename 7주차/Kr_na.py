# -*- coding: utf-8 -*-

import networkx as nx
import itertools
import re

# 키위 형태소 분석기 사용
from kiwipiepy import Kiwi
from kiwipiepy.utils import Stopwords
kiwi = Kiwi()
stopwords = Stopwords()

# 사용자 정의 불용어를 키위 형태소 분석기의 불용어 사전에 추가하기
customized_stopwords = ['재테크','배포','금지', '기자', '페이스북']
for word in customized_stopwords:
    stopwords.add((word, 'NNG'))
    
# 전처리를 통해 명사 단어들 추출
def Kr_preprocessing(text):
    filtered_content = re.sub(r'[^\s\d\w]','',text)
    kiwi_tokens = kiwi.tokenize(filtered_content, stopwords=stopwords)
    Noun_words = []
    for token in kiwi_tokens:
        if 'NN' in token.tag:
            Noun_words.append(token.form)
    # 길이가 1인 단어 제거 하기
    final_Noun_words = []
    for word in Noun_words:
        if len(word)>1:
            final_Noun_words.append(word)
    return final_Noun_words

def add_ties(g, sentence):

#각 문장에 대해서, 각 문장에서 함께 사용되는 단어들 사이에 관계 형성하기

	if len(sentence) > 0 :

		selected_words=list(g.nodes())
		
		for pair in list(itertools.combinations(set(sentence), 2)):
			if pair[0] == pair[1]:
				continue
			if pair[0] in selected_words and pair[1] in selected_words:
				if pair in list(g.edges()) or (pair[1],pair[0]) in list(g.edges()): 
					g[pair[0]][pair[1]]['weight'] += 1
				else:
					g.add_edge(pair[0], pair[1], weight=1 )
		return g
	else:
		return g


def form_network(g, sentences):
#원본 데이터와 가장 많이 출현하는 명사 단어 x개를 사용해서 그 단어들 사이의 관계 형성하기
    for sentence in sentences:
        g = add_ties(g, sentence)
        
    return g

# 텍스트 데이터를 문장 단위로 분할하고, 각 문장에 대해서 전처리 수행
def get_sentences(content):
    text1 = re.sub(r'[^\.\?\!\s\w\d]', ' ', content)
    text1 = re.sub(r'([\.\?\!])',r'\1 ', text1)
    sentences = re.split(r'[\.\?\!]\s+', text1)
    sentences = [Kr_preprocessing(sentence) for sentence in sentences if len(sentence)>0]
    return sentences
    
def do_na(content, selected_words):
    G = nx.Graph()
    G.add_nodes_from(selected_words)
    sentences = get_sentences(content)
    G = form_network(G, sentences)
    
    return G