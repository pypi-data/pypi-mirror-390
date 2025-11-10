import requests
import time
from typing import Dict, Any
from adxp_sdk.auth import BaseCredentials
from requests.exceptions import RequestException

class AXKnowledgeHub:
    """SDK for managing Knowledges"""

    def __init__(self, headers: Dict[str, str] = None, base_url: str = None, credentials: BaseCredentials = None):

        if credentials is not None:
            self.credentials = credentials
            self.base_url = credentials.base_url
            self.headers = credentials.get_headers()
        elif headers is not None and base_url is not None:
            self.credentials = None
            self.base_url = base_url
            self.headers = headers
        else:
            raise ValueError("Either credentials or (headers and base_url) must be provided")
        
    def list_knowledge(self, is_active: bool, page: int, size: int, sort: str, filter: str, search: str) -> Dict[str, Any]:
        
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos"
            params = {
                "is_active" : is_active,
                "page": page, 
                "size": size,
                "sort": sort,
                "filter": filter,
                "search": search
                }
            
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to list knowledges: {str(e)}")
        
    def create_knowledge(self, name: str, description: str, datasource_id: str, embedding_model_name: str, 
                         loader: str, splitter: str, vector_db_id: str, chunk_size: int, chunk_overlap: int, separator: str, project_id: str) -> Dict[str, Any]:
        
        try:

            # 1. 기존 데이터소스 ID가 없으면 데이터소스 ID 생성
            if datasource_id is None:
                url = f"{self.base_url}/api/v1/datasources"
                datasource_name = f"datasource_{name}_{int(time.time())}"
                payload = {
                    "project_id": project_id,
                    "name": datasource_name
                }
                resp = requests.post(url, headers=self.headers, json=payload)
                resp.raise_for_status()
                datasource_id = resp.json().get("id")
            
            # 2. Knowledge 리포지토리 생성
            url = f"{self.base_url}/api/v1/knowledge/repos"
            
            payload = {
                "name": name,
                "description": description,
                "datasource_id": datasource_id,
                "embedding_model_name": embedding_model_name,
                "loader": loader,
                "splitter": splitter,
                "vector_db_id": vector_db_id,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "separator": separator,
            }
            
            # 3. None 값인 항목 제거
            payload = {k: v for k, v in payload.items() if v is not None}   
            
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            
            return resp.json()
            
        except requests.exceptions.RequestException as e:
           raise RequestException(f"Failed to create knowledge: {str(e)}")

    def update_knowledge(self, repo_id: str, name: str, description: str, loader: str, 
                         splitter: str, chunk_size: int, chunk_overlap: int, separator: str) -> Dict[str, Any]:
        
        try:

            # 1. 기존 데이터 가져오기
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            current_data = response.json()
            
            # 2. 파라미터 값이 있으면 파라미터 값, 없으면 기존 데이터 값으로 payload 생성
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}/edit"
            payload = {
                "name": name if name is not None else current_data.get("name"),
                "description": description if description is not None else current_data.get("description"),
                "loader": loader if loader is not None else current_data.get("loader"),
                "splitter": splitter if splitter is not None else current_data.get("splitter"),
                "chunk_size": chunk_size if chunk_size is not None else current_data.get("chunk_size"),
                "chunk_overlap": chunk_overlap if chunk_overlap is not None else current_data.get("chunk_overlap"),
                "separator": separator if separator is not None else current_data.get("separator")
            }

            resp = requests.put(url, json=payload, headers=self.headers)
            resp.raise_for_status()

            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                # 빈 응답 처리
                return {"message": "Successfully updated knowledge", "repo_id": repo_id}

        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update knowledge: {str(e)}")

    def delete_knowledge(self, repo_id: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"
            
            resp = requests.delete(url, headers=self.headers)
            resp.raise_for_status()
            
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"repo_id": repo_id}
                
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to delete knowledge: {str(e)}")
    

    def upload_knowledge_file(self, repo_id: str, datasource_id: str, file_path: str) -> Dict[str, Any]:
        
        try:
            
            # 1. 파일 업로드
            uploadResult = self.upload_file(
                file_path=file_path
            )
            
            # 2. 업로드 된 파일 ID 추출
            getIdResult = self.get_by_fileId(
                datasource_id=datasource_id,
                file_name=uploadResult["data"][0]["file_name"],
            )
            
            # 3. 데이터소스 업데이트
            dataSourceResult = self.update_datasource(
                datasource_id=datasource_id,
                file_id=getIdResult["file_id"],
                file_name=uploadResult["data"][0]["file_name"],
                temp_file_path=uploadResult["data"][0]["temp_file_path"],
            )
            
            # 4. Knowledge 리포지토리 파일 List 업데이트
            KnowledgeResult = self.update_knowledge_datasource(
                repo_id=repo_id
            )

            # 5. Knowledge 리포지토리 파일 인덱싱 실행
            indexResult = self.indexing_knowledge_file(
                repo_id=repo_id,
                target_step="embedding_and_indexing"
            )            

            return {
                    "repo_id": repo_id, 
                    "datasource_id": datasource_id, 
                    "file_path": file_path
            }    
                    
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to upload knowledge file: {str(e)}")

    def upload_file(self, file_path: str) -> Dict[str, Any]:

        try:
            
            # 1. 파일 업로드
            url = f"{self.base_url}/api/v1/datasources/upload/files"

            with open(file_path, 'rb') as file:
                files = {'files': file}
                headers = {"Authorization": self.headers["Authorization"] }
                response = requests.post(url, files=files, headers=headers)
                response.raise_for_status()

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully Upload File", "file_path": file_path}
        except Exception as e:
            raise Exception(f"Failed to Upload File: {e}")
        
    def get_by_fileId(self, datasource_id: str, file_name: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/datasources/{datasource_id}/files/queries/name"
            params = {
                "file_name": file_name
            }
            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully retrieved file by Id", "datasource_id": datasource_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to retrieve file by Id : {str(e)}")
    
    def update_datasource(self, datasource_id: str, file_id: str, file_name: str, temp_file_path: str) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/api/v1/datasources/{datasource_id}"
            
            payload = {
                "id": datasource_id,
                "type": "file",
                "modified_files": [
                    {
                        "file_id" : file_id,
                        "file_name" : file_name,
                        "temp_file_path" : temp_file_path,
                        "status" : "added"
                    }
                ]
            }          

            resp = requests.put(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully updated datasource", "datasource_id": datasource_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update datasource: {str(e)}")
        
    def update_knowledge_datasource(self, repo_id: str) -> Dict[str, Any]:
        
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}"
            payload = {
                "update_mode": "append_modified_docs"
            }
            resp = requests.put(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully updated knowledge datasource", "repo_id": repo_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to update knowledge datasource: {str(e)}")

    def indexing_knowledge_file(self, repo_id: str,target_step: str) -> Dict[str, Any]:
        
        try:
            url = f"{self.base_url}/api/v1/knowledge/repos/{repo_id}/indexing"
            
            payload = {
                "target_step": target_step
            }
            resp = requests.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            try:
                return resp.json()
            except requests.exceptions.JSONDecodeError:
                return {"message": "Successfully started indexing knowledge file", "repo_id": repo_id}
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to start indexing knowledge file: {str(e)}")
