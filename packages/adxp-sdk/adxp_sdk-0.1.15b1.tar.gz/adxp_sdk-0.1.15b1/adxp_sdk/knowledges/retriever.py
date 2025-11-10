from typing import Optional, Dict, Any, List

import requests
from pydantic import ValidationError
from requests import Response

from adxp_sdk.auth import TokenCredentials, ApiKeyCredentials

from adxp_sdk.knowledges.constants import AX_ADVANCED_QUERY_WEB_URI, AX_SIMPLE_QUERY_WEB_URI, AX_SIMPLE_QUERY_URI, \
    AX_ADVANCED_QUERY_URI
from adxp_sdk.knowledges.schemas import RetrievalAdvancedQuery, RetrievalSimpleQuery, RetrievalResult, RetrievalResults


class AXKnowledgeRetriever:

    def __init__(
        self,
        credentials: TokenCredentials | ApiKeyCredentials,
        repo_id: str,
        timeout: float = 180.0,
        verify: bool = True,
    ) -> None:
        self.credentials = credentials
        self.repo_id = repo_id
        self.timeout = timeout
        self.verify = verify
        self.base_url = self.credentials.base_url
        # change endpoint according to credential type
        if isinstance(credentials, ApiKeyCredentials):
            self.uri_simple = AX_SIMPLE_QUERY_URI
            self.uri_advanced = AX_ADVANCED_QUERY_URI
        else:
            self.uri_simple = AX_SIMPLE_QUERY_WEB_URI
            self.uri_advanced = AX_ADVANCED_QUERY_WEB_URI

    def _endpoint(self, relative_uri) -> str:
        return f"{self.base_url}{relative_uri}"

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Credentials.get_headers() 기반 기본 헤더에 호출 시 전달한 extra 헤더를 병합.
        (Authorization, Content-Type, Accept 포함)
        """
        headers = self.credentials.get_headers()
        if extra:
            headers.update(extra)
        return headers

    def _post(self, uri: str, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Response:
        resp = requests.post(
            self._endpoint(uri),
            headers=self._headers(headers),
            json=body,
            verify=self.verify,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp

    @staticmethod
    def _parse_list(response: Response) -> List[RetrievalResult]:
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Invalid response: root is not an object")

        code = payload.get("code")
        if code != 1:
            detail = payload.get("detail")
            raise RuntimeError(f"Retrieval failed (code={code}): {detail}")

        raw_data = payload.get("data") or []
        try:
            validated = RetrievalResults.model_validate({"data": raw_data})
        except ValidationError as e:
            raise RuntimeError(f"Response validation failed: {e}") from e
        return validated.data

    def _build_body_simple(self, query: RetrievalSimpleQuery) -> Dict[str, Any]:
        return {
            "query_text": query.query_text,
            "repo_id": self.repo_id,
        }

    def _build_body_advanced(self, query: RetrievalAdvancedQuery) -> Dict[str, Any]:
        """
        요청 본문 구성. retrieval_options 는 pydantic 모델/일반 객체 모두 대응.
        """
        if hasattr(query, "retrieval_options") and query.retrieval_options is not None:
            ro = query.retrieval_options
            if hasattr(ro, "model_dump"):
                retrieval_options = ro.model_dump(exclude_none=True)
            elif hasattr(ro, "dict"):
                retrieval_options = ro.dict(exclude_none=True)
            else:
                retrieval_options = ro  # 이미 dict 라고 가정
        else:
            retrieval_options = None

        return {
            "query_text": query.query_text,
            "repo_id": self.repo_id,
            "retrieval_options": retrieval_options,
        }

    def _retrieval_simple(
            self,
            query: RetrievalSimpleQuery,
            headers: Optional[Dict[str, str]] = None,
    ) -> List[RetrievalResult]:
        body = self._build_body_simple(query)
        resp = self._post(self.uri_simple, body, headers=headers)
        return self._parse_list(resp)

    def _retrieval_advanced(
            self,
            query: RetrievalAdvancedQuery,
            headers: Optional[Dict[str, str]] = None,
    ) -> List[RetrievalResult]:
        body = self._build_body_advanced(query)
        resp = self._post(self.uri_advanced, body, headers=headers)
        return self._parse_list(resp)

    def get_relevant_documents(
            self,
            query: RetrievalSimpleQuery | RetrievalAdvancedQuery,
            headers: Optional[Dict[str, str]] = None,
    ) -> List[RetrievalResult]:
        if isinstance(query, RetrievalAdvancedQuery):
            return self._retrieval_advanced(query, headers=headers)
        elif isinstance(query, RetrievalSimpleQuery):
            return self._retrieval_simple(query, headers=headers)

        else:
            raise TypeError(
                f"Unsupported query type: {type(query).__name__}. "
                "Expected RetrievalSimpleQuery or RetrievalAdvancedQuery."
            )
