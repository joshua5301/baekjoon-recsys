import math
import re

import numpy as np
import pandas as pd
import soynlp
from gensim.models.word2vec import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer

from .recsys import RecSys
from .. import utils

class ContentRecSys(RecSys):

    def __init__(self):
        self.model = None
        self.document_vectors = None
        self.id_to_vector_index = None

    def fit(self):
        # Load problem contents
        loader = utils.Loader()
        problem_df = loader.load_preproc_df('problem_info')
        problem_df = problem_df.set_index('problemId')
        document_series = problem_df[problem_df['language'] == 'ko']['content'].dropna()
        documents = document_series.to_list()
        id_to_index = {id: index for index, id in enumerate(document_series.index)}
        sentences = ' '.join(documents).split('. ')

        # Clean contents
        clean_string = lambda string: re.sub(r"[^가-힣a-z\s]", "", string.lower())
        sentences = [clean_string(sentence) for sentence in sentences]
        documents = [clean_string(document) for document in documents]

        # Create tokenizer
        extractor = soynlp.word.WordExtractor()
        extractor.train(sentences)
        composite_score = lambda score: score.cohesion_forward * math.exp(score.right_branching_entropy)
        word_to_score = extractor.extract()
        word_to_score = {word: composite_score(score) for word, score in word_to_score.items()}
        tokenizer = soynlp.tokenizer.LTokenizer(word_to_score)

        # Tokenize
        tokenized_sentences = []
        for sentence in sentences:
            tokens = tokenizer.tokenize(sentence)
            tokenized_sentences.append(tokens)
        tokenized_documents = [tokenizer.tokenize(document) for document in documents]

        # Train word2vec using tokenized sentences
        model = Word2Vec(sentences = tokenized_sentences)

        # Fit and transform tf-idf vectorizer
        space_tokenized_documents = [' '.join(tokenized_document) for tokenized_document in tokenized_documents]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(space_tokenized_documents).toarray()
        tfidf_features = tfidf_vectorizer.get_feature_names_out()

        # Create matrix that represents word vectors
        word_vectors = np.zeros((len(tfidf_features), model.wv.vector_size))
        for i, word in enumerate(tfidf_features):
            if word in model.wv:
                word_vectors[i] = model.wv[word]

        # Caculate document vectors 
        document_vectors = np.matmul(tfidf_matrix, word_vectors)

        self.model = model
        self.document_vectors = document_vectors
        self.id_to_vector_index = id_to_index

    def _get_similar_document_vectors(self, target_vector: np.ndarray, num: int) -> list[int]:
        cosine_sims = []
        def cosine_sim(vec1, vec2):
            norm_vec1, norm_vec2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0
            else:
                return np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)
        for index, document_vector in enumerate(self.document_vectors):
            cosine_sims.append((cosine_sim(document_vector, target_vector), index))
        
        cosine_sims.sort(reverse=True)
        vector_index_to_id = {vector_index: id for id, vector_index in self.id_to_vector_index.items()}
        similar_problems = [vector_index_to_id[vector_index] for sim, vector_index in cosine_sims[:num]]
        return similar_problems

    def get_recommendations(self, target_handle: str, num: int) -> list[int]:
        loader = utils.Loader()
        solved_df = loader.load_preproc_df('solved_info')
        solved_problems = list(solved_df[solved_df['handle'] == target_handle]['problemId'])
        if not solved_problems:
            raise KeyError
        document_vector_mean = np.zeros(len(self.document_vectors[0]))
        document_cnt = 0
        for problem_id in solved_problems:
            try:
                vector_index = self.id_to_vector_index[problem_id]
            except KeyError:
                continue
            document_vector_mean += self.document_vectors[vector_index]
            document_cnt += 1
        document_vector_mean /= document_cnt
        return self._get_similar_document_vectors(document_vector_mean, num)

    def get_similar_problems(self, problem_id: int, num: int) -> list[int]:
        vector_index = self.id_to_vector_index[problem_id]
        target_vector = self.document_vectors[vector_index]
        return self._get_similar_document_vectors(target_vector, num)