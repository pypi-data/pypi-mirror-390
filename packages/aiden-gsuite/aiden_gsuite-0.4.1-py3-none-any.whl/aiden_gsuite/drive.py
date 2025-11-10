from typing import Any, Dict, Optional
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials

from aiden_gsuite.credential import MCP_AGENT, Credential

def _build_drive_list_params(
    query: str,
    page_size: int,
    drive_id: Optional[str] = None,
    include_items_from_all_drives: bool = True,
    corpora: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Helper function to build common list parameters for Drive API calls.

    Args:
        query: The search query string
        page_size: Maximum number of items to return
        drive_id: Optional shared drive ID
        include_items_from_all_drives: Whether to include items from all drives
        corpora: Optional corpus specification

    Returns:
        Dictionary of parameters for Drive API list calls
    """
    list_params = {
        "q": query,
        "pageSize": page_size,
        "fields": "nextPageToken, files(id, name, mimeType, webViewLink, iconLink, modifiedTime, size)",
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": include_items_from_all_drives,
    }

    if drive_id:
        list_params["driveId"] = drive_id
        if corpora:
            list_params["corpora"] = corpora
        else:
            list_params["corpora"] = "drive"
    elif corpora:
        list_params["corpora"] = corpora

    return list_params

class DriveService:
    def __init__(self, credential: Credential):
        credentials = AccessTokenCredentials(credential.token, MCP_AGENT)
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = build("drive", "v3", http=http)

    def search_files(self, query: str):
        list_params = _build_drive_list_params(query, 100)
        results = self.service.files().list(**list_params).execute()
        return results.get("files", [])
    
    def get_file_by_id(self, file_id: str):
        return self.service.files().get(fileId=file_id).execute()
    
    def create_folder(self, folder_name: str, parent_folder_id: str):
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_folder_id]
        }
        file = self.service.files().create(body=file_metadata, fields="id").execute()
        return file.get("id")
    
    def create_file(self, file_name: str, folder_id: str):
        file_metadata = {
            "name": file_name,
            "parents": [folder_id]
        }
        file = self.service.files().create(body=file_metadata, fields="id").execute()
        return file.get("id")
    
    def rename_file(self, file_id: str, new_name: str):
        file_metadata = {
            "name": new_name
        }
        file = self.service.files().update(fileId=file_id, body=file_metadata).execute()
        return file.get("id")

    def move_file(self, file_id: str, new_parent_folder_id: str):
        file_metadata = {
            "parents": [new_parent_folder_id]
        }
        file = self.service.files().update(fileId=file_id, body=file_metadata).execute()
        return file.get("id")
    
    def copy_file(self, file_id: str, new_parent_folder_id: str):
        file_metadata = {
            "parents": [new_parent_folder_id]
        }
        file = self.service.files().copy(fileId=file_id, body=file_metadata).execute()
        return file.get("id")
    
    def trash_file_or_folder(self, file_id: str):
        self.service.files().trash(fileId=file_id).execute()
    
    def restore_file_or_folder(self, file_id: str):
        self.service.files().untrash(fileId=file_id).execute()
    
    def empty_trash(self):
        self.service.files().emptyTrash().execute()
    
    def list_trash(self):
        results = self.service.files().list(q="trashed = true").execute()
        return results.get("files", [])
    
    def read_file(self, file_id: str):
        content_bytes = self.service.files().export(fileId=file_id, mimeType="text/plain").execute()
        return content_bytes.decode("utf-8")
    
    def list_files(self, folder_id: str):
        results = self.service.files().list(q=f"parents = '{folder_id}' and trashed = false").execute()
        return results.get("files", [])
    
    def list_root_files(self, page_size: int = 100):
        """List files from the root directory of Google Drive."""
        list_params = _build_drive_list_params(
            query="'root' in parents",
            page_size=page_size
        )
        results = self.service.files().list(**list_params).execute()
        return results.get("files", [])