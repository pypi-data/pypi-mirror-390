"""
Finetuning 관련 스키마 정의
기존 finetuning 기능을 기반으로 작성
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class FinetuningStatus(str, Enum):
    """파인튜닝 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Progress(BaseModel):
    """진행률"""
    percentage: Optional[float] = Field(None, description="진행률 (%)")


class Resource(BaseModel):
    """리소스 설정"""
    cpu_quota: int = Field(..., description="CPU 할당량")
    mem_quota: int = Field(..., description="메모리 할당량")
    gpu_quota: int = Field(..., description="GPU 할당량")
    gpu_type: str = Field(..., description="GPU 타입")


class TrainingConfig(BaseModel):
    """트레이닝 설정"""
    use_lora: bool = Field(False, description="LoRA 사용 여부")
    num_train_epochs: int = Field(1, description="훈련 에포크 수")
    validation_split: float = Field(0.2, description="검증 데이터 분할 비율")
    learning_rate: float = Field(0.0001, description="학습률")
    batch_size: int = Field(1, description="배치 크기")
    early_stopping: bool = Field(False, description="얼리 스토핑 사용 여부")
    early_stopping_patience: Optional[int] = Field(None, description="얼리 스토핑 인내심 (early_stopping이 True일 때만 유효)")
    
    class Config:
        # early_stopping이 False일 때 early_stopping_patience를 None으로 설정
        @validator('early_stopping_patience', always=True)
        def validate_early_stopping_patience(cls, v, values):
            if not values.get('early_stopping', False):
                return None
            return v


class FinetuningCreateRequest(BaseModel):
    """파인튜닝 생성 요청"""
    name: str = Field(..., description="파인튜닝 이름")
    description: Optional[str] = Field(None, description="설명")
    project_id: str = Field(..., description="프로젝트 ID")
    task_id: str = Field(..., description="태스크 ID")
    trainer_id: str = Field(..., description="트레이너 ID")
    dataset_ids: List[str] = Field(..., description="데이터셋 ID 목록")
    base_model_id: str = Field(..., description="베이스 모델 ID")
    params: str = Field(..., description="파라미터 (JSON 문자열)")
    envs: Optional[Dict[str, Any]] = Field(None, description="환경 변수")
    resource: Optional[Resource] = Field(None, description="리소스 설정")
    training_config: Optional[TrainingConfig] = Field(None, description="트레이닝 설정")
    backend_ai_image: str = Field(..., description="Compute Session 생성 시 사용할 이미지")


class FinetuningUpdateRequest(BaseModel):
    """파인튜닝 업데이트 요청"""
    name: Optional[str] = Field(None, description="파인튜닝 이름")
    description: Optional[str] = Field(None, description="설명")
    params: Optional[str] = Field(None, description="파라미터 (JSON 문자열)")
    envs: Optional[Dict[str, Any]] = Field(None, description="환경 변수")
    resource: Optional[Resource] = Field(None, description="리소스 설정")


class FinetuningResponse(BaseModel):
    """파인튜닝 응답"""
    id: str = Field(..., description="파인튜닝 ID")
    name: str = Field(..., description="파인튜닝 이름")
    description: Optional[str] = Field(None, description="설명")
    project_id: str = Field(..., description="프로젝트 ID")
    task_id: str = Field(..., description="태스크 ID")
    trainer_id: str = Field(..., description="트레이너 ID")
    status: FinetuningStatus = Field(..., description="상태")
    prev_status: Optional[str] = Field(None, description="이전 상태")
    progress: Progress = Field(..., description="진행률")
    resource: Resource = Field(..., description="리소스 설정")
    dataset_ids: List[str] = Field(..., description="데이터셋 ID 목록")
    base_model_id: str = Field(..., description="베이스 모델 ID")
    params: str = Field(..., description="파라미터")
    envs: Dict[str, Any] = Field(..., description="환경 변수")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="업데이트 시간")
