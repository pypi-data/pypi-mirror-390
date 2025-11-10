from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional

from adxp_sdk.auth import BaseCredentials


AGENT_PREFIX = "/api/v1/agent"


class AgentApp:
    """Agent App 도메인 오브젝트. 자체에 편의 메서드 포함(RUD, 버전 제어, APIKey 관리)."""

    def __init__(self, client: "AgentAppClient", data: Dict[str, Any]):
        self._client = client
        self._data = data

    # ----------------------------
    # 기본 속성
    # ----------------------------
    @property
    def id(self) -> str:
        return self._data.get("id") or self._data.get("app_id")

    @property
    def name(self) -> Optional[str]:
        return self._data.get("name")

    @property
    def description(self) -> Optional[str]:
        return self._data.get("description")

    @property
    def endpoint(self) -> Optional[str]:
        if not self.id:
            return None
        return f"{self._client.base_url}/api/v1/agent_gateway/{self.id}"

    @property
    def apikeys(self) -> List[str]:
        return self._data.get("apikeys", [])

    # ----------------------------
    # 갱신/제어 메서드
    # ----------------------------
    def refresh(self) -> "AgentApp":
        app = self._client.get_by_id(self.id)
        self._data = app._data
        return self

    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> "AgentApp":
        self._data = self._client.update(self.id, name=name, description=description)
        return self

    def start(self, version: Optional[int] = None) -> None:
        self._client.start(self.id, version)

    def stop(self, version: Optional[int] = None) -> None:
        self._client.stop(self.id, version)

    def delete(self) -> None:
        self._client.delete(app_id=self.id)

    def get_versions(self) -> List[Dict[str, Any]]:
        data = self._client.get_by_id(self.id).raw["deployments"]
        return data

    # API Key
    def create_apikey(self) -> str:
        return self._client.create_apikey(self.id)

    def regen_apikey(self, index: int = 0) -> str:
        keys = self._client.list_apikeys(self.id)
        target = keys[index]
        return self._client.regenerate_apikey(self.id, target)

    def delete_apikey(self, index: int = 0) -> None:
        keys = self._client.list_apikeys(self.id)
        target = keys[index]
        self._client.delete_apikey(self.id, target)

    # 내부용
    @property
    def raw(self) -> Dict[str, Any]:
        return self._data


class AgentAppClient:
    """Agent App CRUD/제어 클라이언트. Builder에서 배포에도 사용."""

    def __init__(self, credentials: BaseCredentials):
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.headers = credentials.get_headers()

    # ----------------------------
    # 배포 (Create)
    # ----------------------------
    def deploy(
        self,
        *,
        target_id: str,
        name: str,
        description: str = "",
        target_type: str = "agent_graph",
        serving_type: str = "shared",
        version_description: Optional[str] = None,
        cpu_request: Optional[int] = None,
        cpu_limit: Optional[int] = None,
        mem_request: Optional[int] = None,
        mem_limit: Optional[int] = None,
        min_replicas: Optional[int] = None,
        max_replicas: Optional[int] = None,
        workers_per_core: Optional[int] = None,
    ) -> AgentApp:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps"
        body: Dict[str, Any] = {
            "target_id": target_id,
            "target_type": target_type,
            "serving_type": serving_type,
            "name": name,
            "description": description,
        }
        if version_description is not None:
            body["version_description"] = version_description
        # 리소스 선택 파라미터(옵션)
        opt_fields = {
            "cpu_request": cpu_request,
            "cpu_limit": cpu_limit,
            "mem_request": mem_request,
            "mem_limit": mem_limit,
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "workers_per_core": workers_per_core,
        }
        for k, v in opt_fields.items():
            if v is not None:
                body[k] = v

        # 타임아웃 설정 및 재시도 로직
        max_retries = 3
        timeout = 60  # 60초로 증가 (배포는 시간이 오래 걸림)
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 배포 시도 {attempt + 1}/{max_retries}...")
                res = requests.post(url, headers=self.headers, json=body, timeout=timeout)
                
                if res.status_code == 200:
                    data = res.json().get("data") or {}
                    # 상세 조회로 정규화
                    app = self.get_by_id(data.get("app_id") or data.get("id"))
                    print("✅ 배포 성공!")
                    return app
                elif res.status_code == 500:
                    print(f"⚠️  서버 에러 (500) - 시도 {attempt + 1}/{max_retries}")
                    try:
                        error_detail = res.json().get("message", "서버 내부 오류")
                        print(f"   에러 상세: {error_detail}")
                    except:
                        print(f"   응답 내용: {res.text[:200]}...")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2, 4, 6초 대기
                        print(f"⏳ {wait_time}초 후 재시도...")
                        import time
                        time.sleep(wait_time)
                        continue
                else:
                    res.raise_for_status()
                    
            except requests.exceptions.Timeout:
                print(f"⏰ 타임아웃 ({timeout}초) - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 5초 후 재시도...")
                    import time
                    time.sleep(5)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ 네트워크 에러: {e} - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 3초 후 재시도...")
                    import time
                    time.sleep(3)
                    continue
        
        # 모든 재시도 실패 시 에러 발생
        print("❌ 모든 재시도 실패")
        raise Exception(f"배포 실패: 타임아웃 또는 네트워크 문제 - {max_retries}회 재시도 후 실패")

    # ----------------------------
    # 조회
    # ----------------------------
    def get_list(
        self,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None,
        desc: bool = False,
        search: Optional[str] = None,
    ) -> List[AgentApp]:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps"
        params: Dict[str, Any] = {"page": page, "size": size, "target_type": "agent_graph"}
        if sort:
            params["sort"] = sort
            params["desc"] = str(desc).lower()
        if search:
            params["search"] = search
        
        # 타임아웃 증가 및 재시도 로직
        max_retries = 3
        timeout = 30  # 30초로 증가
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 앱 목록 조회 시도 {attempt + 1}/{max_retries}...")
                res = requests.get(url, headers=self.headers, params=params, timeout=timeout)
                res.raise_for_status()
                items = res.json().get("data", [])
                print("✅ 앱 목록 조회 성공!")
                return [AgentApp(self, item) for item in items]
                
            except requests.exceptions.Timeout:
                print(f"⏰ 타임아웃 ({timeout}초) - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9초 대기
                    print(f"⏳ {wait_time}초 후 재시도...")
                    import time
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ 네트워크 에러: {e} - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 5초 후 재시도...")
                    import time
                    time.sleep(5)
                    continue
        
        # 모든 재시도 실패 시 빈 리스트 반환
        print("❌ 모든 재시도 실패 - 빈 목록 반환")
        return []

    def get_by_id(self, app_id: str) -> AgentApp:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
        
        # 타임아웃 증가 및 재시도 로직
        max_retries = 3
        timeout = 30  # 30초로 증가
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 앱 상세 조회 시도 {attempt + 1}/{max_retries}...")
                res = requests.get(url, headers=self.headers, timeout=timeout)
                res.raise_for_status()
                data = res.json().get("data", {})
                # apikey 목록 병합
                try:
                    apikeys = self.list_apikeys(app_id)
                    data["apikeys"] = apikeys
                except Exception:
                    pass
                print("✅ 앱 상세 조회 성공!")
                return AgentApp(self, data)
                
            except requests.exceptions.Timeout:
                print(f"⏰ 타임아웃 ({timeout}초) - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9초 대기
                    print(f"⏳ {wait_time}초 후 재시도...")
                    import time
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ 네트워크 에러: {e} - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 5초 후 재시도...")
                    import time
                    time.sleep(5)
                    continue
        
        # 모든 재시도 실패 시 에러 발생
        print("❌ 모든 재시도 실패")
        raise Exception(f"앱 상세 조회 실패: app_id={app_id}")

    # ----------------------------
    # 수정/삭제
    # ----------------------------
    def update(self, app_id: str, *, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
        payload: Dict[str, Any] = {"name": name, "description": description}
        
        # 타임아웃 증가 및 재시도 로직
        max_retries = 3
        timeout = 30  # 30초로 증가
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 앱 업데이트 시도 {attempt + 1}/{max_retries}...")
                res = requests.put(url, headers=self.headers, json=payload, timeout=timeout)
                res.raise_for_status()
                data = res.json().get("data", {})
                print("✅ 앱 업데이트 성공!")
                return data
                
            except requests.exceptions.Timeout:
                print(f"⏰ 타임아웃 ({timeout}초) - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9초 대기
                    print(f"⏳ {wait_time}초 후 재시도...")
                    import time
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ 네트워크 에러: {e} - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 5초 후 재시도...")
                    import time
                    time.sleep(5)
                    continue
        
        # 모든 재시도 실패 시 에러 발생
        print("❌ 모든 재시도 실패")
        raise Exception(f"앱 업데이트 실패: app_id={app_id}")

    def delete(self, *, app_id: Optional[str] = None, deployment_id: Optional[str] = None) -> None:
        if app_id:
            url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}"
        elif deployment_id:
            url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/deployments/{deployment_id}"
        else:
            raise ValueError("app_id or deployment_id must be provided")
        
        # 타임아웃 증가 및 재시도 로직
        max_retries = 3
        timeout = 30  # 30초로 증가
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 앱 삭제 시도 {attempt + 1}/{max_retries}...")
                res = requests.delete(url, headers=self.headers, timeout=timeout)
                if res.status_code not in (200, 204):
                    res.raise_for_status()
                print("✅ 앱 삭제 성공!")
                return
                
            except requests.exceptions.Timeout:
                print(f"⏰ 타임아웃 ({timeout}초) - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 3, 6, 9초 대기
                    print(f"⏳ {wait_time}초 후 재시도...")
                    import time
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ 네트워크 에러: {e} - 시도 {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("⏳ 5초 후 재시도...")
                    import time
                    time.sleep(5)
                    continue
        
        # 모든 재시도 실패 시 에러 발생
        print("❌ 모든 재시도 실패")
        raise Exception(f"앱 삭제 실패: app_id={app_id or deployment_id}")

    # ----------------------------
    # 시작/중지 (앱 혹은 특정 버전)
    # ----------------------------
    def start(self, app_id: str, version: Optional[int] = None) -> None:
        # 한 번만 앱 정보 조회
        info = self.get_by_id(app_id).raw
        deployments = info.get("deployments", [])
        if not deployments:
            return
            
        if version is None:
            # 최신 배포 재시작
            deployment_id = deployments[0].get("id")
        else:
            # 특정 버전 id 찾기
            target = next((d for d in deployments if d.get("version") == version), None)
            deployment_id = target.get("id") if target else None
            
        if not deployment_id:
            raise ValueError("deployment not found")
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/deployments/restart/{deployment_id}"
        res = requests.post(url, headers=self.headers, timeout=30)
        res.raise_for_status()

    def stop(self, app_id: str, version: Optional[int] = None) -> None:
        # 한 번만 앱 정보 조회
        info = self.get_by_id(app_id).raw
        deployments = info.get("deployments", [])
        if not deployments:
            return
            
        if version is None:
            deployment_id = deployments[0].get("id")
        else:
            target = next((d for d in deployments if d.get("version") == version), None)
            deployment_id = target.get("id") if target else None
            
        if not deployment_id:
            raise ValueError("deployment not found")
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/deployments/stop/{deployment_id}"
        res = requests.post(url, headers=self.headers, timeout=30)
        res.raise_for_status()

    # ----------------------------
    # API Key
    # ----------------------------
    def list_apikeys(self, app_id: str) -> List[str]:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys"
        res = requests.get(url, headers=self.headers, timeout=30)
        res.raise_for_status()
        return res.json().get("data", [])

    def create_apikey(self, app_id: str) -> str:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys"
        res = requests.post(url, headers=self.headers, timeout=30)
        res.raise_for_status()
        return res.json().get("data", {}).get("api_key", "")

    def regenerate_apikey(self, app_id: str, apikey: str) -> str:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys/{apikey}/regenerate"
        res = requests.get(url, headers=self.headers, timeout=30)
        res.raise_for_status()
        return res.json().get("data", {}).get("api_key", "")

    def delete_apikey(self, app_id: str, apikey: str) -> None:
        url = f"{self.base_url}{AGENT_PREFIX}/agents/apps/{app_id}/apikeys/{apikey}"
        res = requests.delete(url, headers=self.headers, timeout=30)
        if res.status_code not in (200, 204):
            res.raise_for_status()


