import spacy
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import json
import string
from collections import defaultdict
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

class AIComponents:
    def __init__(self, spacy_model_name: str):
        print("Загрузка NLP инструментов...")
        self._download_nltk_data()
        self.stemmer = SnowballStemmer("russian")
        self.stop_words = set(stopwords.words('russian'))
        self.stop_words.update(['или', 'не'])
        self.nlp_ner = spacy.load(spacy_model_name)
        print("Инструменты загружены.")

    def _download_nltk_data(self):
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')


from pymorphy3 import MorphAnalyzer
import math
import re
from collections import Counter

def clean_text(text):
    # Удалить все неалфавитно-цифровые символы, кроме пробелов
    # Заменяет любые символы, кроме букв, цифр, пробелов на пробел
    cleaned = re.sub(r'[^а-яА-Яa-zA-Z0-9ёЁ\s]', ' ', text)
    # Убирает лишние пробелы
    cleaned = ' '.join(cleaned.split())
    return cleaned


class Indexer:
    def __init__(self, ai_components):
        self.nlp_ner = ai_components.nlp_ner
        self.stop_words = ai_components.stop_words
        self.morph = MorphAnalyzer()
        self.vectorizer = TfidfVectorizer(stop_words=list(self.stop_words), norm='l2')
        self.documents = []
        self.doc_vectors = {}
        self.corpus = ''

    def add_document(self, doc_id, title, content):
        self.documents.append({'id': doc_id, 'title': title, 'content': content})

    def preprocess_document(self, doc):
        title = clean_text(doc['title'])
        content = clean_text(doc['content'])
        lemmatized_content = self.lemmatize(content)
        full_text = f"{title} {lemmatized_content}"
        return full_text

    def lemmatize(self, text):
        tokens = nltk.word_tokenize(text.lower(), language='russian')
        lemmas = []
        for token in tokens:
            if token not in string.punctuation and token not in self.stop_words and len(token) > 2:
                lemma = self.morph.normal_forms(token)[0]
                lemmas.append(lemma)
        return ' '.join(lemmas)

    def index_documents(self):
        if not self.documents:
            print("Нет документов для индексации.")
            return

        corpus = [self.preprocess_document(doc) for doc in self.documents]
        self.corpus = corpus
        tfidf_matrix = self.vectorizer.fit_transform(corpus)  # L2 нормализация здесь

        # Сохраняем векторы документов с нормализацией
        self.doc_vectors = {doc['title']: tfidf_matrix[idx].toarray()[0].tolist() for idx, doc in enumerate(self.documents)}

        print("Индексация завершена.")

    def save_info_in_KB(self):
        concept_drive_disk_info = ScKeynodes.resolve("concept_drive_disk_info", sc_type.CONST_NODE_CLASS)

        # проверяем существует ли уже векторизованные документы из диска и удаляем их
        template = ScTemplate()
        template.triple(
            concept_drive_disk_info,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE,
        )
        search_results = search_by_template(template)
        for result in search_results:
            erase_connectors(result[0], result[2], sc_type.VAR_PERM_POS_ARC)

        # извлекаем все необходимы keynodes
        nrel_corpus = ScKeynodes.resolve("nrel_corpus", sc_type.CONST_NODE_ROLE)
        nrel_doc_vectors = ScKeynodes.resolve("nrel_doc_vectors", sc_type.CONST_NODE_ROLE)
        nrel_idtf = ScKeynodes.resolve("nrel_idtf", sc_type.CONST_NODE_ROLE)
        nrel_next = ScKeynodes.resolve("nrel_next", sc_type.CONST_NODE_ROLE)
        nrel_vectorized_doc = ScKeynodes.resolve("nrel_vectorized_doc", sc_type.CONST_NODE_ROLE)

        # создаем объект корпуса текста
        corpus_tuple = generate_node(sc_type.CONST_NODE_TUPLE)
        first_corpus_link = generate_link(self.corpus[0], ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK,)
        first_rrel = generate_role_relation(corpus_tuple, first_corpus_link, ScKeynodes.rrel_index(1))

        temp_arc = first_rrel
        for corpus_one in self.corpus[1:]:
            corpus_link = generate_link(corpus_one, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK,)
            new_arc = generate_connector(sc_type.CONST_PERM_POS_ARC, corpus_tuple, corpus_link)
            generate_non_role_relation(temp_arc,new_arc,nrel_next)
            temp_arc = new_arc
        
        # создаем объект векторов документов
        '''vectors_tuple = generate_node(sc_type.CONST_NODE_TUPLE)
        for key, value in self.doc_vectors.items():

            import time
            start_time = time.perf_counter()

            
            vector = generate_node(sc_type.CONST_NODE)
            generate_connector(sc_type.CONST_PERM_POS_ARC, vectors_tuple, vector)
            title_link = generate_link(key, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK,)
            generate_non_role_relation(vector,title_link,nrel_idtf)

            first_vector_val_link = generate_link(value[0], ScLinkContentType.INT, link_type=sc_type.CONST_NODE_LINK,)
            first_rrel = generate_role_relation(vector, first_vector_val_link, ScKeynodes.rrel_index(1))

            temp_arc = first_rrel
            for vector_val_one in value[1:]:
                vector_val_link = generate_link(vector_val_one, ScLinkContentType.INT, link_type=sc_type.CONST_NODE_LINK,)
                new_arc = generate_connector(sc_type.CONST_PERM_POS_ARC, vector, vector_val_link)
                generate_non_role_relation(temp_arc,new_arc,nrel_next)
                temp_arc = new_arc      
            
            
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"Время выполнения: {elapsed_time:.4f} секунд")'''

        vectors_tuple = generate_node(sc_type.CONST_NODE_TUPLE)
        for key, value in self.doc_vectors.items():

            import time
            start_time = time.perf_counter()

            vector = generate_node(sc_type.CONST_NODE)
            generate_connector(sc_type.CONST_PERM_POS_ARC, vectors_tuple, vector)
            title_link = generate_link(key, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK,)
            generate_non_role_relation(vector,title_link,nrel_idtf)

            vectorized_doc_string = ' '.join(map(str, value))
            vectorized_doc_string_link = generate_link(vectorized_doc_string, ScLinkContentType.STRING, link_type=sc_type.CONST_NODE_LINK,)
            generate_non_role_relation(vector, vectorized_doc_string_link, nrel_vectorized_doc)


            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"Время выполнения: {elapsed_time:.4f} секунд")


        # генерация конечного шаблона
        template = ScTemplate()
        infoAlias = '_info'
        template.triple(
            concept_drive_disk_info,
            sc_type.VAR_PERM_POS_ARC,
            sc_type.VAR_NODE >> infoAlias,
        )
        template.quintuple(
            infoAlias,
            sc_type.VAR_COMMON_ARC,
            corpus_tuple,
            sc_type.VAR_PERM_POS_ARC,
            nrel_corpus,
        )

        template.quintuple(
            infoAlias,
            sc_type.VAR_COMMON_ARC,
            vectors_tuple,
            sc_type.VAR_PERM_POS_ARC,
            nrel_doc_vectors,
        )
        search_results = generate_by_template(template)
        
        # self.doc_vectors
        # self.corpus
        

        


import os
from docx import Document
from PyPDF2 import PdfReader
import os
import io
from googleapiclient.http import MediaIoBaseDownload
import tempfile

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def read_pdf(file_path):
    text = []
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)

def get_path_to_root(service, file_id, path_names=None):
    if path_names is None:
        path_names = []
    try:
        file = service.files().get(fileId=file_id, fields='id, name, parents').execute()
        path_names.insert(0, file['name'])
        if file.get('parents'):
            parent_id = file['parents'][0]
            if parent_id != 'root':  # 'root' — это корневая папка
                get_path_to_root(service, parent_id, path_names)
    except Exception as e:
        pass
    return path_names

class IndexerWithFiles(Indexer):
    def download_file(self, service, file_id, file_name):
        """Скачивает файл с Google Drive по file_id и сохраняет как file_name"""
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Скачано {int(status.progress() * 100)}% файла {file_name}")
        fh.close()

    def index_files(self, service, files_list):
        for idx, file_info in enumerate(files_list, start=1):
            try:
                # Создаём временный файл с оригинальным именем
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_info['name'])[1]) as tmp_file:
                    temp_file_path = tmp_file.name
                print(f"Обработка файла #{idx}: {file_info['name']}")
                
                # Скачиваем файл с Drive во временный файл
                self.download_file(service, file_info['id'], temp_file_path)
                
                ext = os.path.splitext(temp_file_path)[1].lower()
                if ext == '.txt':
                    content = read_txt(temp_file_path)
                elif ext == '.docx':
                    content = read_docx(temp_file_path)
                elif ext == '.pdf':
                    content = read_pdf(temp_file_path)
                else:
                    print(f"Пропуск файла с неподдерживаемым форматом: {file_info['name']}")
                    os.remove(temp_file_path)
                    continue
                
                path = get_path_to_root(service, file_info['id'])        
                title =  f"{'/'.join(path)}"

                self.add_document(idx, title, content)
                
                # Удаляем временный файл
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Ошибка при обработке {file_info['name']}: {e}")
        self.index_documents()
