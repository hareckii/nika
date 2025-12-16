import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import nltk, string
from pymorphy3 import MorphAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

from sc_client.client import search_by_template, generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScLinkContentType, ScTemplate
from sc_kpm import ScAgentClassic, ScKeynodes, ScResult
from sc_kpm.sc_sets import ScSet
from sc_kpm.utils import (
    generate_role_relation,
    check_connector,
    erase_connectors,
    generate_connector,
    generate_non_role_relation,
    generate_node,
    generate_link,
    get_element_system_identifier,
    get_link_content_data,
    search_connector,
    search_element_by_non_role_relation,
)
from sc_kpm.utils.action_utils import (
    finish_action_with_status,
    generate_action_result,
    get_action_arguments,
)

import re
from collections import Counter

def clean_text(text):
    # Удалить все неалфавитно-цифровые символы, кроме пробелов
    # Заменяет любые символы, кроме букв, цифр, пробелов на пробел
    cleaned = re.sub(r'[^а-яА-Яa-zA-Z0-9ёЁ\s]', ' ', text)
    # Убирает лишние пробелы
    cleaned = ' '.join(cleaned.split())
    return cleaned

class SearchEngine:
    def __init__(self, ai_components):
        self.stop_words = ai_components.stop_words
        self.morph = MorphAnalyzer()
        self.vectorizer = TfidfVectorizer(stop_words=list(self.stop_words), norm='l2')
        
        self.make_vectorizer()
        
        self.extract_vectors()
        
        if not self.doc_vectors:
            print("Ошибка: doc_vectors пустой")
        else:
            print("doc_vectors не пустой")

        # Преобразуем в numpy массивы
        self.doc_ids = list(self.doc_vectors.keys())
        if self.doc_ids:
            self.doc_vectors_array = np.array([self.doc_vectors[doc_id] for doc_id in self.doc_ids])
        else:
            print("Ошибка: doc_ids пустой")
            self.doc_vectors_array = np.array([])



    def make_vectorizer(self):
        concept_drive_disk_info = ScKeynodes.resolve("concept_drive_disk_info", sc_type.CONST_NODE_CLASS)
        nrel_corpus = ScKeynodes.resolve("nrel_corpus", sc_type.CONST_NODE_ROLE)
        nrel_next = ScKeynodes.resolve("nrel_next", sc_type.CONST_NODE_ROLE)
        rrel_1 = ScKeynodes.resolve("rrel_1", sc_type.CONST_NODE_NON_ROLE)
        infoAlias = '_info'
        corpus_tupleAlias = '_corpus'
        # проверяем существует ли уже векторизованные документы из диска и удаляем их
        template = ScTemplate()
        template.triple(
            concept_drive_disk_info,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> infoAlias,
        )
        template.quintuple(
            infoAlias,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_TUPLE >> corpus_tupleAlias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_corpus,
        )
        search_results = search_by_template(template)
        result = search_results[0]
        if result:
            corpus_tuple = result.get(corpus_tupleAlias)
        else:
            return ScResult.OK

        corpus_list =[]
        
        first_rrelAlias = '_arc'
        first_linkAlias = '_link'
        template = ScTemplate()
        template.quintuple(
            corpus_tuple,
            sc_type.VAR_PERM_POS_ARC >> first_rrelAlias,
            sc_type.VAR_NODE_LINK >> first_linkAlias,
            sc_type.VAR_PERM_POS_ARC,
            rrel_1,
        )
        search_results = search_by_template(template)        
        result = search_results[0]

        content_link = result.get(first_linkAlias)
        content = get_link_content_data(content_link)        
        corpus_list.append(content)

        first_arc = result.get(first_rrelAlias)
        temp_arc = first_arc
        i = 0
        while True:
            i = i + 1
            rrelAlias = '_arc'
            linkAlias = '_link'
            template = ScTemplate()
            template.quintuple(
                temp_arc,
                sc_type.VAR_COMMON_ARC,
                sc_type.VAR_PERM_POS_ARC>>rrelAlias,
                sc_type.VAR_PERM_POS_ARC,
                nrel_next,
            )
            template.triple(
                corpus_tuple,
                rrelAlias,
                sc_type.VAR_NODE_LINK >> linkAlias,
            )
            search_results = search_by_template(template)
            if len(search_results):
                result = search_results[0]
                
                content_link = result.get(linkAlias)
                content = get_link_content_data(content_link)
                temp_arc = result.get(rrelAlias)
                corpus_list.append(content)
            else:
                break

        self.corpus = corpus_list
        self.vectorizer.fit(corpus_list)  # L2 нормализация здесь
        

    def extract_vectors(self):
        concept_drive_disk_info = ScKeynodes.resolve("concept_drive_disk_info", sc_type.CONST_NODE_CLASS)
        nrel_doc_vectors = ScKeynodes.resolve("nrel_doc_vectors", sc_type.CONST_NODE_ROLE)
        nrel_idtf = ScKeynodes.resolve("nrel_idtf", sc_type.CONST_NODE_ROLE)
        nrel_vectorized_doc = ScKeynodes.resolve("nrel_vectorized_doc", sc_type.CONST_NODE_ROLE)
        nrel_web_link = ScKeynodes.resolve("nrel_web_link", sc_type.CONST_NODE_ROLE)
        infoAlias = '_info'
        vectors_tupleAlias = '_corpus'
        # проверяем существует ли уже векторизованные документы из диска и удаляем их
        template = ScTemplate()
        template.triple(
            concept_drive_disk_info,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> infoAlias,
        )
        template.quintuple(
            infoAlias,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_TUPLE >> vectors_tupleAlias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_doc_vectors,
        )
        search_results = search_by_template(template)
        result = search_results[0]
        if result:
            vectors_tuple = result.get(vectors_tupleAlias)
        else:
            return ScResult.OK
        
        vectorAlias = '_vector'
        idtfAlias = '_idtf'
        vectorized_docAlias= '_vectorized_doc'
        webLinkAlias = '_webLink'

        template = ScTemplate()
        template.triple(
            vectors_tuple,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> vectorAlias,
        )        
        template.quintuple(
            vectorAlias,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK >> idtfAlias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_idtf
        )
        template.quintuple(
            vectorAlias,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK >> vectorized_docAlias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_vectorized_doc
        )
        template.quintuple(
            vectorAlias,
            sc_type.VAR_COMMON_ARC,
            sc_type.VAR_NODE_LINK >> webLinkAlias,
            sc_type.VAR_PERM_POS_ARC,
            nrel_web_link
        )
        search_get_from_set = search_by_template(template)

        self.doc_vectors = {}
        self.doc_links = {} 
        for result in search_get_from_set:
            idtf_link = result.get(idtfAlias)
            vectorized_doc_link = result.get(vectorized_docAlias)
            idtf = get_link_content_data(idtf_link)
            vectorized_doc = get_link_content_data(vectorized_doc_link)
            web_link_link = result.get(webLinkAlias)
            web_link = get_link_content_data(web_link_link)
            numbers = [float(x) for x in vectorized_doc.split()]
            self.doc_vectors[idtf] = numbers
            if web_link:
                self.doc_links[idtf] = web_link

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

    def save_info_in_KB(self, results, request):
        concept_request_answer = ScKeynodes.resolve("concept_request_answer", sc_type.CONST_NODE_CLASS)
        nrel_request = ScKeynodes.resolve("nrel_request", sc_type.CONST_NODE_NON_ROLE)
        nrel_docs = ScKeynodes.resolve("nrel_docs", sc_type.CONST_NODE_NON_ROLE)
        nrel_format = ScKeynodes.resolve("nrel_format", sc_type.CONST_NODE_NON_ROLE)
        format_html = ScKeynodes.resolve("format_html", sc_type.CONST_NODE)

        # Удаляем старые результаты
        template = ScTemplate()
        template.triple(
            concept_request_answer,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE,
        )
        search_results = search_by_template(template)
        for result in search_results:
            erase_connectors(result[0], result[2], sc_type.VAR_PERM_POS_ARC)

        # Создаём HTML со ссылками
        # Формируем HTML-строку с результатами
        html_parts = []
        for i, (doc_id, score) in enumerate(results):
            if score > 0:
                web_link = self.doc_links.get(doc_id)
                if web_link:
                    html_parts.append(f'<a href="{web_link}" target="_blank">{i+1}) {doc_id}</a>')
                else:
                    html_parts.append(f'{i+1}) {doc_id}')
        html_str = '<br>'.join(html_parts)
        html_link = generate_link(html_str, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK)


        # Добавляем файл с HTML и устанавливаем формат
        generate_non_role_relation(html_link, format_html, nrel_format)

        request_link = generate_link(request, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK)

        nodeAlias = '_node'
        template = ScTemplate()
        
        template.triple(
            concept_request_answer,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> nodeAlias,
        )
        template.quintuple(
            nodeAlias,
            sc_type.VAR_COMMON_ARC,
            html_link,
            sc_type.VAR_PERM_POS_ARC,
            nrel_docs,
        )
        template.quintuple(
            nodeAlias,
            sc_type.VAR_COMMON_ARC,
            request_link,
            sc_type.VAR_PERM_POS_ARC,
            nrel_request,
        )
        search_results = generate_by_template(template)
