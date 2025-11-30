'''from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CLIENT_SECRET_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=8888)
    service = build('drive', 'v3', credentials=creds)
    return service
'''

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

current_dir = os.path.dirname(__file__)
CLIENT_SECRET_FILE = os.path.join(current_dir, '..', 'credentials', 'client_secrets.json')

# Проверка, что файл существует
if not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"Файл не найден: {CLIENT_SECRET_FILE}")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

TOKEN_FILE = os.path.join(current_dir, '..', 'credentials', 'token.pickle')

def authorize():
    creds = None
    # Загружаем токен из файла, если он существует
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # Если нет токена или он просрочен, проходим авторизацию
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8888)
        # Сохраняем токен для последующих запусков
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    return service

