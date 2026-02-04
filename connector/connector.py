from __future__ import annotations

import os
from typing import Optional, List, Dict

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

GOOGLE_SHORTCUT_MIME = "application/vnd.google-apps.shortcut"

# Se o arquivo for Google Docs/Sheets/Slides, precisa exportar
EXPORT_MIME_BY_GOOGLE_TYPE = {
    "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",    # .xlsx
    "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    "application/vnd.google-apps.drawing": "image/png",
}

EXT_BY_EXPORT_MIME = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "image/png": ".png",
    "application/pdf": ".pdf",
}

def get_drive_service():
    creds: Optional[Credentials] = None

    # Obter diretório base do projeto (um nível acima de connector/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(base_dir, "secrets", "credentials.json")
    token_path = os.path.join(base_dir, "token.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def find_files_in_folder(service, filename: str, folder_id: str) -> List[Dict]:
    q = f"trashed = false and name = '{filename}' and '{folder_id}' in parents"
    resp = service.files().list(
        q=q,
        fields="files(id, name, mimeType, shortcutDetails)",
        pageSize=50,
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
    ).execute()
    return resp.get("files", [])

def resolve_shortcut(file_obj: Dict) -> str:
    if file_obj.get("mimeType") == GOOGLE_SHORTCUT_MIME:
        details = file_obj.get("shortcutDetails") or {}
        target_id = details.get("targetId")
        if not target_id:
            raise RuntimeError("Atalho encontrado, mas sem targetId.")
        return target_id
    return file_obj["id"]

def download_file(service, file_id: str, filename_hint: str, local_dir: str) -> str:
    os.makedirs(local_dir, exist_ok=True)

    meta = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType",
        supportsAllDrives=True,
    ).execute()

    mime_type = meta["mimeType"]
    drive_name = meta["name"]

    # Caso 1: Arquivo “normal” (PDF, XLSX, PNG, etc.) -> get_media
    if not mime_type.startswith("application/vnd.google-apps."):
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
        local_path = os.path.join(local_dir, drive_name)
        with open(local_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request, chunksize=1024 * 1024)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return local_path

    # Caso 2: Arquivo Google (Docs/Sheets/Slides) -> export_media
    export_mime = EXPORT_MIME_BY_GOOGLE_TYPE.get(mime_type, "application/pdf")
    ext = EXT_BY_EXPORT_MIME.get(export_mime, "")

    base_name = filename_hint or drive_name
    if ext and not base_name.lower().endswith(ext):
        base_name += ext

    request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    local_path = os.path.join(local_dir, base_name)

    with open(local_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request, chunksize=1024 * 1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    return local_path

def main():
    # ===== PARAMETROS =====
    SHARED_SOURCE_FOLDER_ID = "16xWfLokGgg_tSPdZtHgrhLZ1mSho0yQH"
    SOURCE_FILENAME = "meu_arquivo.xlsx"   # nome do arquivo no Drive (exato)
    LOCAL_DEST_DIR = "./downloads"         # pasta local de destino
    # ======================

    service = get_drive_service()

    try:
        matches = find_files_in_folder(service, SOURCE_FILENAME, SHARED_SOURCE_FOLDER_ID)
        if not matches:
            raise RuntimeError("Arquivo não encontrado na pasta compartilhada (valide nome e folderId).")

        if len(matches) > 1:
            print(f"Atenção: {len(matches)} itens com esse nome. Usando o primeiro.")

        file_obj = matches[0]
        real_id = resolve_shortcut(file_obj)

        local_path = download_file(
            service=service,
            file_id=real_id,
            filename_hint=SOURCE_FILENAME,
            local_dir=LOCAL_DEST_DIR,
        )

        print("Download concluído:")
        print(f"- local_path: {local_path}")

    except HttpError as e:
        raise RuntimeError(f"Erro na Drive API: {e}") from e

if __name__ == "__main__":
    main()
