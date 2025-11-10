"""
프롬프트 관련 스키마 정의
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PromptMessage(BaseModel):
    """프롬프트 메시지"""

    message: str = Field(..., description="메시지 내용")
    mtype: int = Field(
        ..., description="메시지 타입 (1: System, 2: User, 3: Assistant)"
    )


class PromptTag(BaseModel):
    """프롬프트 태그"""

    tag: str = Field(..., description="태그명")


class PromptVariable(BaseModel):
    """프롬프트 변수"""

    variable: str = Field(..., description="변수명 (예: {{variable_name}})")
    token_limit: int = Field(0, description="토큰 제한")
    token_limit_flag: bool = Field(False, description="토큰 제한 사용 여부")
    validation: str = Field("", description="유효성 검사 정규식")
    validation_flag: bool = Field(False, description="유효성 검사 사용 여부")


class PromptCreateRequest(BaseModel):
    """프롬프트 생성 요청"""

    name: str = Field(..., description="프롬프트 이름")
    desc: Optional[str] = Field(None, description="프롬프트 설명")
    project_id: str = Field(..., description="프로젝트 ID")
    messages: List[PromptMessage] = Field(..., description="프롬프트 메시지 목록")
    tags: Optional[List[PromptTag]] = Field(None, description="태그 목록")
    variables: Optional[List[PromptVariable]] = Field(None, description="변수 목록")
    release: bool = Field(False, description="릴리즈 여부")


class PromptUpdateRequest(BaseModel):
    """프롬프트 수정 요청"""

    new_name: Optional[str] = Field(None, description="프롬프트 이름", alias="name")
    desc: Optional[str] = Field(None, description="프롬프트 설명")
    messages: Optional[List[PromptMessage]] = Field(
        None, description="프롬프트 메시지 목록"
    )
    tags: Optional[List[PromptTag]] = Field(None, description="태그 목록")
    variables: Optional[List[PromptVariable]] = Field(None, description="변수 목록")
    release: Optional[bool] = Field(None, description="릴리즈 여부")


class PromptResponse(BaseModel):
    """프롬프트 응답"""

    id: str = Field(..., description="프롬프트 ID")
    name: str = Field(..., description="프롬프트 이름")
    desc: Optional[str] = Field(None, description="프롬프트 설명")
    project_id: str = Field(..., description="프로젝트 ID")
    messages: List[PromptMessage] = Field(..., description="프롬프트 메시지 목록")
    tags: Optional[List[PromptTag]] = Field(None, description="태그 목록")
    variables: Optional[List[PromptVariable]] = Field(None, description="변수 목록")
    release: bool = Field(False, description="릴리즈 여부")
    created_at: Optional[str] = Field(None, description="생성 시간")
    updated_at: Optional[str] = Field(None, description="수정 시간")
    created_by: Optional[str] = Field(None, description="생성자")
    version: Optional[int] = Field(1, description="버전")


class ApiResponse(BaseModel):
    """API 공통 응답 구조"""

    timestamp: int = Field(..., description="타임스탬프")
    code: int = Field(..., description="응답 코드")
    detail: str = Field(..., description="응답 메시지")
    traceId: Optional[str] = Field(None, description="추적 ID")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    payload: Optional[Dict[str, Any]] = Field(None, description="추가 페이로드")


class PromptCreateResponse(BaseModel):
    """프롬프트 생성 응답"""

    prompt_uuid: str = Field(..., description="생성된 프롬프트 UUID")


class PromptListResponse(BaseModel):
    """프롬프트 목록 응답"""

    success: bool = Field(..., description="성공 여부")
    data: List[PromptResponse] = Field(
        default_factory=list, description="프롬프트 목록"
    )
    total: int = Field(0, description="전체 개수")
    page: int = Field(1, description="현재 페이지")
    size: int = Field(10, description="페이지 크기")
    message: Optional[str] = Field(None, description="응답 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")
