"""
Agent Graph CRUD SDK의 메인 클라이언트
"""

import requests
import json
from typing import Optional, Dict, Any, Union
from adxp_sdk.auth import BaseCredentials
from .graph_schemas import (
    AgentGraphCreateRequest,
    AgentGraphTemplateRequest,
    AgentGraphResponse,
    GraphRequestBody,
    InputBody,
)
from adxp_sdk.auth import BaseCredentials


class AgentGraphClient:
    """Agent Graph CRUD 클라이언트"""

    def __init__(
        self,
        credentials: BaseCredentials,
        api_key: Optional[str] = None,
    ):
        """
        Agent Graph 클라이언트 초기화

        Args:
            credentials: 인증 정보 (BaseCredentials)
            api_key: API 키 (deprecated, use credentials instead)
        """
        self.credentials = credentials
        self.base_url = credentials.base_url
        self.session = requests.Session()
        self.session.headers.update(credentials.get_headers())

    def create_from_template(
        self, name: str, description: str, template_id: str
    ) -> AgentGraphResponse:
        """
        템플릿을 사용하여 Agent Graph 생성

        Args:
            name: 생성할 그래프 이름
            description: 그래프 설명
            template_id: 사용할 템플릿 ID

        Returns:
            AgentGraphResponse: 생성된 그래프 정보

        Raises:
            requests.RequestException: API 요청 실패 시
        """
        url = f"{self.base_url}/api/v1/agent/agents/graphs/templates"

        payload = {"name": name, "description": description, "template_id": template_id}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            print(f"DEBUG: Template API 응답 데이터: {data}")

            # API 응답이 data 필드로 감싸져 있는 경우 처리
            if "data" in data and data["data"] is not None:
                graph_data = data["data"]
                return AgentGraphResponse(**graph_data)
            else:
                return AgentGraphResponse(**data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"템플릿으로 Agent Graph 생성 실패: {e}")

    def create_direct(
        self, name: str, description: str, graph_data: Dict[str, Any]
    ) -> AgentGraphResponse:
        """
        직접 정의하여 Agent Graph 생성

        Args:
            name: 생성할 그래프 이름
            description: 그래프 설명
            graph_data: 그래프 구조 데이터

        Returns:
            AgentGraphResponse: 생성된 그래프 정보

        Raises:
            requests.RequestException: API 요청 실패 시
        """
        url = f"{self.base_url}/api/v1/agent/agents/graphs"

        payload = {"name": name, "description": description, "graph": graph_data}

        try:
            print(f"DEBUG: 전송할 페이로드: {payload}")
            response = self.session.post(url, json=payload)
            print(f"DEBUG: 응답 상태 코드: {response.status_code}")
            print(f"DEBUG: 응답 내용: {response.text}")
            response.raise_for_status()

            data = response.json()

            # API 응답이 data 필드 안에 실제 그래프 정보를 포함하고 있음
            if "data" in data and data["data"] is not None:
                graph_data = data["data"]
                return AgentGraphResponse(**graph_data)
            else:
                # 기존 형식으로 응답이 오는 경우
                return AgentGraphResponse(**data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"직접 정의로 Agent Graph 생성 실패: {e}")

    def create(
        self,
        name: str,
        description: str,
        graph_data: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None,
    ) -> AgentGraphResponse:
        """
        Agent Graph 생성 (통합 메서드)

        Args:
            name: 생성할 그래프 이름
            description: 그래프 설명
            graph_data: 직접 정의할 그래프 데이터 (선택사항)
            template_id: 사용할 템플릿 ID (선택사항)

        Returns:
            AgentGraphResponse: 생성된 그래프 정보

        Raises:
            ValueError: graph_data와 template_id가 모두 없거나 모두 있는 경우
            requests.RequestException: API 요청 실패 시
        """
        if graph_data and template_id:
            raise ValueError("graph_data와 template_id 중 하나만 제공해야 합니다")

        if not graph_data and not template_id:
            raise ValueError(
                "graph_data 또는 template_id 중 하나는 반드시 제공해야 합니다"
            )

        if template_id:
            return self.create_from_template(name, description, template_id)
        else:
            return self.create_direct(name, description, graph_data)

    def read(self, graph_id: str) -> AgentGraphResponse:
        """
        Agent Graph 조회 (ID로 단일 그래프 조회)

        Args:
            graph_id: 조회할 그래프 ID

        Returns:
            AgentGraphResponse: 그래프 정보

        Raises:
            requests.RequestException: API 요청 실패 시
        """
        url = f"{self.base_url}/api/v1/agent/agents/graphs/{graph_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()

            # API 응답이 data 필드 안에 실제 그래프 정보를 포함하고 있음
            if "data" in data and data["data"] is not None:
                graph_data = data["data"]
                return AgentGraphResponse(**graph_data)
            else:
                # 기존 형식으로 응답이 오는 경우
                return AgentGraphResponse(**data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Agent Graph 조회 실패: {e}")

    def update(
        self, graph_id: str, name: str, description: str, graph_data: Dict[str, Any]
    ) -> AgentGraphResponse:
        """
        Agent Graph 수정

        Args:
            graph_id: 수정할 그래프 ID
            name: 그래프 이름
            description: 그래프 설명
            graph_data: 전체 그래프 구조 데이터

        Returns:
            AgentGraphResponse: 수정된 그래프 정보

        Raises:
            requests.RequestException: API 요청 실패 시
        """
        url = f"{self.base_url}/api/v1/agent/agents/graphs/{graph_id}"

        payload = {"name": name, "description": description, "graph": graph_data}

        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()

            data = response.json()
            print(f"DEBUG: Update API 응답 데이터: {data}")

            # API 응답이 data 필드로 감싸져 있는 경우 처리
            if "data" in data and data["data"] is not None:
                graph_data = data["data"]
                return AgentGraphResponse(**graph_data)
            else:
                return AgentGraphResponse(**data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Agent Graph 수정 실패: {e}")

    def delete(self, graph_id: str) -> bool:
        """
        Agent Graph 삭제 (ID로 그래프 삭제)

        Args:
            graph_id: 삭제할 그래프 ID

        Returns:
            bool: 삭제 성공 여부 (True: 성공, False: 실패)

        Raises:
            requests.RequestException: API 요청 실패 시
        """
        url = f"{self.base_url}/api/v1/agent/agents/graphs/{graph_id}"

        try:
            response = self.session.delete(url)
            print(f"DEBUG: Delete API 응답 상태 코드: {response.status_code}")
            print(f"DEBUG: Delete API 응답 내용: {response.text}")

            response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Delete API 오류: {e}")
            raise Exception(f"Agent Graph 삭제 실패: {e}")

    def validate(self, request_data: dict) -> bool:
        """
        그래프 요청 데이터 유효성 검사
        """
        try:
            GraphRequestBody(**request_data)
            return True
        except Exception as e:
            raise ValueError(
                f"[RequestBody Invalidated] 요청 데이터 형식이 잘못되었습니다: {e}"
            )

    def invoke(
        self,
        graph_id: str,
        inputs: InputBody | dict,
        config: dict | None = None,
    ) -> Dict[str, Any]:
        """
        그래프를 실행하고 답변을 받는 메서드

        Args:
            request_data: 실행 요청 데이터
                {
                    "graph_id": "graph_id",
                    "input_data": {
                        "messages": [
                            {"content": "안녕하세요", "type": "human"}
                        ]
                    }
                }

        Returns:
            정리된 실행 결과 딕셔너리
        """
        if isinstance(inputs, dict):
            try:
                inputs = InputBody(**inputs)

            except Exception as e:
                raise ValueError(
                    f"[Validation Error] inputs 형식이 잘못되었습니다: {e}"
                )

        request_data = GraphRequestBody(
            graph_id=graph_id, input_data=inputs, config=config
        ).model_dump()

        url = f"{self.base_url}/api/v1/agent/agents/graphs/query"

        try:
            print(f"DEBUG: Execute Graph API 요청 URL: {url}")
            print(
                f"DEBUG: Execute Graph API 요청 데이터: {json.dumps(request_data, indent=2, ensure_ascii=False)}"
            )

            response = self.session.post(url, json=request_data)
            print(f"DEBUG: Execute Graph API 응답 상태 코드: {response.status_code}")
            print(f"DEBUG: Execute Graph API 응답 내용: {response.text}")

            response.raise_for_status()

            raw_response = response.json()
            return self._format_graph_response(raw_response)

        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Execute Graph API 오류: {e}")
            raise Exception(f"Agent Graph 실행 실패: {e}")

    def _format_graph_response(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        그래프 실행 응답을 사용자 친화적으로 정리하는 메서드

        Args:
            raw_response: 원본 API 응답

        Returns:
            정리된 응답 딕셔너리
        """
        try:
            output = raw_response.get("output", {})
            content = output.get("content", "")

            # 정리된 응답 구성
            formatted_response = {
                "content": content,
                "run_id": raw_response.get("config", {}).get("run_id"),
                "success": True,
            }

            # 메시지가 있는 경우 추가
            messages = output.get("messages", [])
            if messages:
                formatted_response["messages"] = messages

            return formatted_response

        except Exception as e:
            print(f"DEBUG: 응답 포맷팅 오류: {e}")
            # 포맷팅 실패 시 원본 응답 반환
            return raw_response

    def stream(
        self, graph_id: str, inputs: InputBody | dict, config: dict | None = None
    ) -> Dict[str, Any]:
        # TODO: output이 Iterator여야 합니다.
        """
        그래프를 스트리밍으로 실행하고 답변을 받는 메서드

        Args:
            request_data: 실행 요청 데이터
                {
                    "graph_id": "graph_id",
                    "input_data": {
                        "messages": [
                            {"content": "안녕하세요", "type": "human"}
                        ]
                    }
                }

        Returns:
            정리된 스트리밍 실행 결과 딕셔너리

        # TODO: output이 Iterator여야 합니다.
        사용 예시
            for chunk in client.stream(
                {"messages": [{"content": "2024년 한국의 GDP 찾아줘", "type": "human"}]}
            ):
                if chunk.get("progress"):
                    # 실행 시작한 노드의 description
                    print("🍎", chunk)
                elif chunk.get("llm"):
                    # LLM 응답
                    print("🍌", chunk)
                elif chunk.get("updates"):
                    # 노드별 실행 결과
                    print("💨", chunk)
                elif chunk.get("tool_calls"):
                    # 툴 호출 결과
                    print("🍓", chunk)
                elif chunk.get("tool"):
                    # 툴 실행 결과
                    print("🍇", chunk)
                elif chunk.get("final_result"):
                    # 최종 결과
                    print("⭐️", chunk)
                elif chunk.get("error"):
                    # 에러메세지
                    print("💥", chunk)
        """
        if isinstance(inputs, dict):
            inputs = InputBody(**inputs)

        request_data = GraphRequestBody(
            graph_id=graph_id, input_data=inputs, config=config
        ).model_dump()
        url = f"{self.base_url}/api/v1/agent/agents/graphs/stream"

        try:
            print(f"DEBUG: Stream Graph API 요청 URL: {url}")
            print(
                f"DEBUG: Stream Graph API 요청 데이터: {json.dumps(request_data, indent=2, ensure_ascii=False)}"
            )

            response = self.session.post(url, json=request_data, stream=True)
            print(f"DEBUG: Stream Graph API 응답 상태 코드: {response.status_code}")

            response.raise_for_status()

            # 스트리밍 응답 처리
            return self._process_stream_response(response)

        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Stream Graph API 오류: {e}")
            raise Exception(f"Agent Graph 스트리밍 실행 실패: {e}")

    def _process_stream_response(self, response) -> Dict[str, Any]:
        """
        스트리밍 응답을 처리하는 메서드

        Args:
            response: requests Response 객체

        Returns:
            정리된 응답 딕셔너리
        """
        try:
            content_parts = []
            run_id = None

            # 스트리밍 응답 처리
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"DEBUG: Stream 라인: {line}")

                    # Server-Sent Events 형식 처리
                    # TODO: startswith로 처리하면 종종 에러가 발생. (응답이 오래걸리는경우 ping 날리게 되는데 그때 에러나는것으로 추정중)
                    # 다른 프로젝트(A.Biz)에서 이런 방식으로 Agent B/E 호출해서 사용하고있는데 connection이 불안정하고, parsing이 잘 안되는 문제를 겪고있음.
                    # 아래 코드 참고하여 sse client 연결 및 파싱에 대한 로직 추가 필요
                    # https://github.com/langchain-ai/langserve/blob/main/langserve/client.py#L520
                    if line.startswith("data: "):
                        data_line = line[6:]  # 'data: ' 제거
                        if data_line.strip() and data_line != "[DONE]":
                            try:
                                data = json.loads(data_line)
                                if "content" in data:
                                    content_parts.append(data["content"])
                                if "run_id" in data:
                                    run_id = data["run_id"]
                            except json.JSONDecodeError:
                                # JSON이 아닌 경우 그대로 추가
                                content_parts.append(data_line)

                    # 일반 텍스트 응답 처리
                    elif not line.startswith("event:"):
                        try:
                            data = json.loads(line)
                            if "content" in data:
                                content_parts.append(data["content"])
                            if "run_id" in data:
                                run_id = data["run_id"]
                        except json.JSONDecodeError:
                            # JSON이 아닌 경우 그대로 추가
                            content_parts.append(line)

            # 최종 응답 구성
            final_content = "".join(content_parts)

            return {"content": final_content, "run_id": run_id, "success": True}

        except Exception as e:
            print(f"DEBUG: 스트리밍 응답 처리 오류: {e}")
            # 오류 발생 시 빈 응답 반환
            return {"content": "", "run_id": None, "success": False, "error": str(e)}
