def crawl_drive(service):
    files = []
    page_token = None
    query_files = "(mimeType='application/pdf' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType='text/plain') and 'me' in owners and trashed = false"
    page_token = None
    while True:
        response = service.files().list(
            q=query_files,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break

    return files