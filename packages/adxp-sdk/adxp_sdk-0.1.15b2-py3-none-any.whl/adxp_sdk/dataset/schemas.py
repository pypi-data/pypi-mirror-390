"""
Dataset CRUD SDK - 데이터 모델 정의

Dataset 생성, 조회, 수정, 삭제를 위한 Pydantic 모델들
실제 API 스펙에 맞게 수정됨
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class DatasetType(str, Enum):
    """Dataset 타입 열거형"""
    UNSUPERVISED_FINETUNING = "unsupervised_finetuning"
    SUPERVISED_FINETUNING = "supervised_finetuning"
    MODEL_BENCHMARK = "model_benchmark"
    DPO_FINETUNING = "dpo_finetuning"
    CUSTOM = "custom"
    
    @classmethod
    def get_supported_extensions(cls, dataset_type: str) -> List[str]:
        """Dataset 타입별 지원 확장자 반환"""
        extension_map = {
            cls.UNSUPERVISED_FINETUNING: [".xlsx", ".csv"],
            cls.SUPERVISED_FINETUNING: [".xlsx", ".csv"],
            cls.DPO_FINETUNING: [".xlsx", ".csv"],
            cls.MODEL_BENCHMARK: [".zip", ".tar"],
            cls.CUSTOM: [".zip", ".tar"]
        }
        return extension_map.get(dataset_type, [])
    
    @classmethod
    def requires_processor(cls, dataset_type: str) -> bool:
        """Dataset 타입이 프로세서를 필요로 하는지 확인"""
        processor_required = [
            cls.UNSUPERVISED_FINETUNING,
            cls.SUPERVISED_FINETUNING,
            cls.DPO_FINETUNING
        ]
        return dataset_type in processor_required
    
    @classmethod
    def get_required_columns(cls, dataset_type: str) -> List[str]:
        """Dataset 타입별 필수 컬럼 반환"""
        column_map = {
            cls.UNSUPERVISED_FINETUNING: ["text"],
            cls.SUPERVISED_FINETUNING: ["system", "user(.N)", "assistant(.N)"],
            cls.DPO_FINETUNING: ["user", "chosen", "rejected"]
        }
        return column_map.get(dataset_type, [])


class DatasetStatus(str, Enum):
    """Dataset 상태 열거형"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class DatasetTag(BaseModel):
    """Dataset 태그 (실제 API 스펙에 맞춤)"""
    name: str = Field(..., description="태그명")


class DatasetFile(BaseModel):
    """Dataset 파일 정보"""
    file_name: str = Field(..., description="파일 이름")
    file_path: Optional[str] = Field(None, description="파일 경로")
    file_size: Optional[int] = Field(None, description="파일 크기")


class DatasetProcessor(BaseModel):
    """Dataset 데이터 프로세서 (실제 API 스펙에 맞춤)"""
    ids: List[str] = Field(default_factory=list, description="프로세서 ID 목록")
    duplicate_subset_columns: List[str] = Field(default_factory=list, description="중복 제거 대상 컬럼")
    regular_expression: List[str] = Field(default_factory=list, description="정규표현식 목록")


class DatasetPolicy(BaseModel):
    """Dataset 정책"""
    cascade: bool = Field(False, description="계단식 적용 여부")
    decision_strategy: str = Field("UNANIMOUS", description="결정 전략")
    logic: str = Field("POSITIVE", description="로직")
    policies: List[Dict[str, Any]] = Field(default_factory=list, description="정책 목록")
    scopes: List[str] = Field(default_factory=list, description="적용 범위")


class DatasetCreateRequest(BaseModel):
    """Dataset 생성 요청 (실제 API 스펙에 맞춤)"""
    name: str = Field(..., description="Dataset 이름")
    type: DatasetType = Field(..., description="Dataset 타입")
    description: Optional[str] = Field("", description="Dataset 설명")
    tags: Optional[List[DatasetTag]] = Field(None, description="태그 목록")
    status: DatasetStatus = Field(DatasetStatus.PROCESSING, description="Dataset 상태")
    project_id: str = Field(..., description="프로젝트 ID")
    is_deleted: bool = Field(False, description="삭제 여부")
    datasource_id: Optional[str] = Field(None, description="데이터 소스 ID")
    processor: Optional[DatasetProcessor] = Field(None, description="데이터 프로세서")
    created_by: Optional[str] = Field(None, description="생성자")
    updated_by: Optional[str] = Field(None, description="수정자")
    policy: Optional[List[DatasetPolicy]] = Field(None, description="정책 목록")


class DatasetUpdateRequest(BaseModel):
    """Dataset 수정 요청 (API 스펙에 맞춤 - description, project_id, tags만 수정 가능)"""
    description: Optional[str] = Field(None, description="Dataset 설명")
    project_id: Optional[str] = Field(None, description="프로젝트 ID")
    tags: Optional[List[DatasetTag]] = Field(None, description="태그 목록")


class DatasetResponse(BaseModel):
    """Dataset 응답 (API 스펙에 맞춤)"""
    id: str = Field(..., description="Dataset ID")
    name: str = Field(..., description="Dataset 이름")
    type: DatasetType = Field(..., description="Dataset 타입")
    description: Optional[str] = Field(None, description="Dataset 설명")
    tags: List[DatasetTag] = Field(default_factory=list, description="태그 목록")
    status: str = Field(..., description="Dataset 상태")
    project_id: str = Field(..., description="프로젝트 ID")
    is_deleted: bool = Field(False, description="삭제 여부")
    created_at: Optional[str] = Field(None, description="생성 시간")
    updated_at: Optional[str] = Field(None, description="수정 시간")
    created_by: Optional[str] = Field(None, description="생성자")
    updated_by: Optional[str] = Field(None, description="수정자")
    datasource_id: Optional[str] = Field(None, description="데이터 소스 ID")
    datasource_files: List[str] = Field(default_factory=list, description="데이터 소스 파일 목록")
    processor: Optional[Dict[str, Any]] = Field(None, description="데이터 프로세서")
    file_path: Optional[str] = Field(None, description="파일 경로")


class DatasetListResponse(BaseModel):
    """Dataset 목록 응답"""
    success: bool = Field(..., description="성공 여부")
    data: List[DatasetResponse] = Field(default_factory=list, description="Dataset 목록")
    total: int = Field(0, description="전체 개수")
    page: int = Field(1, description="현재 페이지")
    size: int = Field(10, description="페이지 크기")
    message: Optional[str] = Field(None, description="응답 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")


class DatasetCreateResponse(BaseModel):
    """Dataset 생성 응답"""
    dataset_id: str = Field(..., description="생성된 Dataset ID")


class ApiResponse(BaseModel):
    """API 공통 응답 구조"""
    timestamp: int = Field(..., description="타임스탬프")
    code: int = Field(..., description="응답 코드")
    detail: str = Field(..., description="응답 메시지")
    traceId: Optional[str] = Field(None, description="추적 ID")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    payload: Optional[Dict[str, Any]] = Field(None, description="추가 페이로드")


class DatasetFilter(BaseModel):
    """Dataset 필터 (실제 API 스펙에 맞춤)"""
    type: Optional[DatasetType] = Field(None, description="Dataset 타입 필터")
    status: Optional[DatasetStatus] = Field(None, description="상태 필터")
    tags: Optional[List[str]] = Field(None, description="태그 필터")
    search: Optional[str] = Field(None, description="검색어")


class DatasetListRequest(BaseModel):
    """Dataset 목록 조회 요청 (실제 API 스펙에 맞춤)"""
    project_id: str = Field(..., description="프로젝트 ID")
    page: int = Field(1, description="페이지 번호")
    size: int = Field(10, description="페이지 크기")
    sort: Optional[str] = Field(None, description="정렬 기준")
    filter: Optional[DatasetFilter] = Field(None, description="필터 조건")
    search: Optional[str] = Field(None, description="검색어")


class DatasourceFile(BaseModel):
    """데이터소스 파일 정보"""
    id: str = Field(..., description="파일 ID")
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기 (바이트)")
    file_type: str = Field(..., description="파일 타입")
    created_at: str = Field(..., description="생성일시")
    updated_at: str = Field(..., description="수정일시")
    temp_file_path: Optional[str] = Field(None, description="임시 파일 경로")
    file_metadata: Optional[Dict[str, Any]] = Field(None, description="파일 메타데이터")


class DatasourceFilesResponse(BaseModel):
    """데이터소스 파일 목록 응답"""
    data: List[DatasourceFile] = Field(..., description="파일 목록")
    total: int = Field(..., description="전체 파일 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total_pages: int = Field(..., description="전체 페이지 수")