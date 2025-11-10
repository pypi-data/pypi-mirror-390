from pydantic import BaseModel, Field

from .enums import RetrievalMode


class RetrievalOptions(BaseModel):
    retrieval_mode: str | None = Field(
        default=RetrievalMode.DENSE,
        title="검색 모드",
        description=("검색 시 사용할 모드입니다. 주의: `semantic`은 Azure AI Search 검색 시에만 사용할 수 있습니다."),
        example=RetrievalMode.DENSE,
    )
    top_k: int | None = Field(
        default=3,
        title="검색 상위 K개",
        description="가장 유사한 결과 중 상위 K개를 반환합니다.",
        example=3,
    )
    filter: str | None = Field(
        default=None,
        title="필터",
        description="검색 결과를 필터링할 조건입니다."
        "예> 'view_count gt 25'로 파일 ID 기준으로 오름차순 정렬을 수행합니다.",
        example="view_count gt 25'",
    )
    file_ids: list[str] | None = Field(
        default=None,
        title="검색 대상 file id 리스트",
        description="검색 대상 file id 리스트에 해당하는 문서만 검색합니다.",
    )
    hybrid_dense_ratio: float | None = Field(
        default=None,
        title="hybrid 검색 시 dense store 적용 비율",
        description="hybrid 검색 시 dense store 적용 비율, ratio 값은 0 보다 크고 1보다 작은 값이어야 합니다."
                    "검색 모드가 hybrid 인 경우에만 사용되는 값으로, 전달되지 않으면 기본값으로 정의된 비율로 조회시 적용됩니다.",
        example=0.6,
    )
    query_keywords: str | None = Field(
        default=None,
        title="키워드 기반 질의",
        description="원문 질의(query_text)에서 핵심 단어만 추출하여 구성한 간결한 질의. sparse, hybrid검색 시 전달되면 정확도 개선에 도움이 됨.",
        example="개인퇴직연금 중도해지 조건",
    )
    order_by: str | None = Field(
        default=None,
        title="정렬",
        description="검색 결과를 정렬할 조건입니다. 예: 'view_count desc'",
        example="view_count desc",
    )
    semantic_configuration_name: str | None = Field(
        None,
        title="Semantic Configuration Name(Azure AI Search Only)",
        description=(
            "Azure AI Search 인덱스 생성 시 정의된 semantic configuration의 이름입니다. "
            "이 설정은 **Semantic Search** 모드에서 의미 기반 유사성에 따라 "
            "검색 결과를 반환할 때 사용됩니다. 그 외 검색 모드에서는 입력하지 마세요."
        ),
        example="defaultSemanticConfig",
    )
    scoring_profile: str | None = Field(
        None,
        title="Scoring Profile(Azure AI Search Only)",
        description=(
            "Azure AI Search 인덱스 생성 시, 정의된 스코어링 프로파일입니다. "
            "이 프로파일은 **Full-Text/Hybrid Search** 모드에서 사용되며, "
            "검색 결과의 정렬 기준을 동적으로 조정합니다. 그 외 검색모드에서는 입력하지 마세요."
        ),
        example="productSearchProfile",
    )
    scoring_parameters: dict[str, str] | None = Field(
        None,
        title="Scoring Parameters(Azure AI Search Only)",
        description=(
            "스코어링 프로파일에 전달되는 매개변수입니다. "
            "예를 들어 특정 필드의 가중치를 동적으로 조정할 때 사용됩니다."
        ),
        example={"boostingField": "popularity", "region": "APAC"},
    )


class RetrievalSimpleQuery(BaseModel):
    query_text: str = Field(
        ...,
        title="사용자 질의",
        min_length=1,
        description="사용자 질의 내용은 최소 1글자 이상 입력해주세요.",
        example="개인형퇴직연금 중도해지 조건 알려줘.",
    )


class RetrievalAdvancedQuery(RetrievalSimpleQuery):
    retrieval_options: RetrievalOptions | None = Field(
        default=None,
        title="검색 옵션",
        description="벡터DB 종류 따라 지원되는 검색 옵션 차이가 있습니다. 자세한 내용은 가이드 문서 참고 부탁 드립니다.",
    )


class RetrievalResult(BaseModel):
    content: str = Field(
        ...,
        title="검색된 본문 내용",
        description="검색 쿼리에 대응하는 문서의 본문 내용 조각입니다.",
    )

    metadata: dict = Field(
        ...,
        title="문서 메타데이터",
        description="검색된 문서와 관련된 메타데이터입니다. 예를 들어, 문서 위치, 문서명, 문서 포맷 등이 포함됩니다.",
    )

    score: float = Field(
        ...,
        title="검색 점수",
        description="검색 쿼리와의 일치도를 나타내는 점수입니다. 높은 점수는 더 높은 관련성을 의미합니다.",
    )


class RetrievalResults(BaseModel):
    data: list[RetrievalResult] = Field(
        default_factory=list,
        title="검색 결과",
        description="검색 결과 리스트",
    )