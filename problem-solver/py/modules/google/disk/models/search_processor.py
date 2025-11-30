import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import nltk, string
from indexer import clean_text
from pymorphy3 import MorphAnalyzer


class SearchEngine:
    def __init__(self, ai_components, vectorizer_file, vectors_file):
        self.stop_words = ai_components.stop_words
        self.morph = MorphAnalyzer()
        self.vectorizer = joblib.load(vectorizer_file)
        with open(vectors_file, 'r', encoding='utf-8') as f:
            self.doc_vectors = json.load(f)
        # Преобразуем в numpy массивы
        self.doc_ids = list(self.doc_vectors.keys())
        self.doc_vectors_array = np.array([self.doc_vectors[doc_id] for doc_id in self.doc_ids])

    def lemmatize(self, text):
        tokens = nltk.word_tokenize(text.lower(), language='russian')
        lemmas = []
        for token in tokens:
            if token not in string.punctuation and token not in self.stop_words and len(token) > 2:
                lemma = self.morph.normal_forms(token)[0]
                lemmas.append(lemma)
        return ' '.join(lemmas)

    def search(self, query):
        # Очистка и лемматизация запроса
        cleaned_query = clean_text(query)
        lemmatized_query = self.lemmatize(cleaned_query)
        # Векторизация запроса
        query_vector = self.vectorizer.transform([lemmatized_query]).toarray()[0]
        # Косинусное сходство
        similarities = cosine_similarity([query_vector], self.doc_vectors_array)[0]
        # Сортировка по убыванию сходства
        ranked = sorted(zip(self.doc_ids, similarities), key=lambda x: x[1], reverse=True)
        return ranked
