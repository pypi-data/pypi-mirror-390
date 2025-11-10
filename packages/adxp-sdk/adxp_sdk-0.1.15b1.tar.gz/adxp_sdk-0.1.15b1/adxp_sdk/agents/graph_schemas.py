"""
Agent Graph CRUD SDK의 스키마 정의
실제 서버 스키마와 동일하게 구현
"""

from typing import List, Optional, Dict, Any, Union, Literal, Type
from pydantic import BaseModel, Field, ConfigDict, model_validator, ValidationError
from enum import Enum
from langchain_core.runnables import RunnableConfig


class Position(str, Enum):
    """노드 연결 위치"""

    LEFT = "left"
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"


class XYPosition(BaseModel):
    """노드 위치 좌표"""

    x: int
    y: int


class InputKey(BaseModel):
    """입력 키"""

    name: str
    required: bool = True
    description: str = ""
    fixed_value: Optional[str] = None
    keytable_id: Optional[str] = Field(default=None)


class InputKeyRequired(InputKey):
    """필수 입력 키"""

    required: bool = True


class OutputKey(BaseModel):
    """출력 키"""

    name: str
    keytable_id: Optional[str] = Field(default=None)


class MCPCatalog(BaseModel):
    """MCP 카탈로그"""

    catalog_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    tools: Optional[List[str]] = None


class IntentCategory(BaseModel):
    """의도 카테고리"""

    id: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ConditionInfo(BaseModel):
    """조건 정보"""

    id: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Dict[str, Any]] = None
    operator: Optional[str] = None
    input_key: Optional[Dict[str, Any]] = None


class RetrievalKnowledge(BaseModel):
    """지식 검색 설정"""

    repo_id: str
    project_id: Optional[str] = None
    embedding_info: Optional[Any] = None
    knowledge_info: Optional[Any] = None
    retrieval_options: Optional[Dict[str, Any]] = None
    vectordb_conn_info: Optional[Any] = None
    active_collection_id: Optional[str] = ""

    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "24aa2047-0648-4fdb-9411-330bf0d54a7b",
                "project_id": "default",
                "retrieval_options": {
                    "top_k": 5,
                    "filter": None,
                    "keywords": [],
                    "order_by": None,
                    "threshold": 0.3,
                    "retrieval_mode": "dense",
                    "doc_format_metafieds": [],
                },
            }
        }


class RetrievalKnowledgeRequired(RetrievalKnowledge):
    """필수 지식 검색 설정"""

    project_id: str


class QueryRewriter(BaseModel):
    """쿼리 리라이터"""

    llm_chain: Optional[Dict[str, Any]] = None
    rewrite_type: Optional[str] = None
    max_queries: Optional[int] = None


class QueryRewriterRequired(QueryRewriter):
    """필수 쿼리 리라이터"""

    pass


class ContextRefiner(BaseModel):
    """컨텍스트 리파이너"""

    llm_chain: Dict[str, Any] = Field(description="LLM 체인 설정")

    class Config:
        json_schema_extra = {
            "example": {
                "llm_chain": {
                    "prompt": "",
                    "llm_config": {"api_key": "", "serving_name": "GIP/gpt-4o-mini"},
                }
            }
        }


class ContextRefinerRequired(ContextRefiner):
    """필수 컨텍스트 리파이너"""

    pass


class ContextReranker(BaseModel):
    """컨텍스트 리랭커"""

    rerank_cnf: Dict[str, Any] = Field(description="리랭킹 설정")

    class Config:
        json_schema_extra = {
            "example": {
                "rerank_cnf": {
                    "model_name": "rerank-model",
                    "top_k": 5,
                    "threshold": 0.7,
                }
            }
        }


class ContextRerankerRequired(ContextReranker):
    """필수 컨텍스트 리랭커"""

    pass


# ==================== 노드 데이터 스키마 ====================


class InputNodeDataSchema(BaseModel):
    """Input Basic 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(description="Node의 이름")
    description: Optional[str] = Field(default="", description="description of node")
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: Optional[List[OutputKey]] = Field(
        default=None, description="node에서 생성할 output_keys."
    )


class OutputKeysDataSchema(BaseModel):
    """Output Keys 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(description="Node의 이름")
    description: Optional[str] = Field(default=None, description="description of node")
    input_keys: List[InputKey] = Field(description="최종 답변에 쓸 Key의 List")


class OutputChatDataSchema(BaseModel):
    """Output Chat 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(description="Node의 이름")
    description: Optional[str] = Field(default=None, description="description of node")
    format_string: Optional[str] = Field(
        default=None, description="최종 답변을 만들 포맷 형식"
    )


class OutputChatRequired(OutputChatDataSchema):
    """필수 Output Chat 노드 데이터"""

    format_string: str


class GeneratorDataSchema(BaseModel):
    """Generator 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    serving_name: Optional[str] = Field(
        default=None, description="Model Gateway 호출할 때 사용할 Model의 serving_name"
    )
    serving_model: Optional[str] = Field(
        default=None, description="LLM Model의 이름(타입)"
    )
    prompt_id: Optional[str] = Field(default=None, description="ID of Prompt")
    fewshot_id: Optional[str] = Field(default=None, description="ID of fewshot")
    tool_ids: Optional[List[str]] = Field(
        default=[], description="Function Call, ReACT agent에서 사용할 tool ids"
    )
    mcp_catalogs: Optional[List[MCPCatalog]] = Field(
        default=[], description="MCP Catalog 목록"
    )
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")


class GeneratorRequired(GeneratorDataSchema):
    """필수 Generator 노드 데이터"""

    serving_name: str
    input_keys: List[InputKeyRequired] = Field(
        description="node에서 사용할 input_keys."
    )


class CoderDataSchema(BaseModel):
    """Coder 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    code: str = Field(default=None, description="Code for Execute")
    input_keys: Optional[List[InputKey]] = Field(
        default=[], description="node에서 사용할 input_keys."
    )
    output_keys: Optional[List[OutputKey]] = Field(
        default=[], description="node에서 사용할 output_keys."
    )


class CategorizerDataSchema(BaseModel):
    """Categorizer 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    serving_name: Optional[str] = Field(
        default=None, description="Model Gateway 호출할 때 사용할 Model의 serving_name"
    )
    serving_model: Optional[str] = Field(
        default=None, description="LLM Model의 이름(타입)"
    )
    prompt_id: Optional[str] = Field(default=None, description="ID of Prompt")
    categories: Optional[List[IntentCategory]] = Field(
        default=None, description="분류할 categories"
    )
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")


class CategorizerRequired(CategorizerDataSchema):
    """필수 Categorizer 노드 데이터"""

    serving_name: str
    input_keys: List[InputKeyRequired] = Field(
        description="node에서 사용할 input_keys."
    )


class AgentAppDataSchema(BaseModel):
    """Agent App 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    agent_app_id: Optional[str] = Field(default=None, description="Agent App의 id")
    api_key: Optional[str] = Field(default=None, description="API Key")
    input_keys: List[InputKey] = Field(
        default=[], description="node에서 사용할 input_keys."
    )
    output_keys: List[OutputKey] = Field(
        default=[], description="node에서 사용할 output_keys."
    )


class AgentAppRequired(AgentAppDataSchema):
    """필수 Agent App 노드 데이터"""

    agent_app_id: str
    input_keys: List[InputKey]
    api_key: str


class ConditionDataSchema(BaseModel):
    """Condition 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    conditions: Optional[List[ConditionInfo]] = Field(
        default=None, description="조건에 대한 정보"
    )
    default_condition: str = Field(
        default="condition-else", description="조건이 만족하지 않을 때 실행될 기본 조건"
    )
    input_keys: Optional[List[InputKey]] = Field(
        default=None, description="node에서 사용할 input_keys."
    )
    output_keys: List[OutputKey] = Field(
        default=[], description="node에서 사용할 output_keys."
    )


class ConditionRequired(ConditionDataSchema):
    """필수 Condition 노드 데이터"""

    input_keys: List[InputKey]
    conditions: List[ConditionInfo]


class UnionDataSchema(BaseModel):
    """Union 노드 데이터"""

    type: Optional[str] = "union"
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    format_string: str = Field(
        default="", description="새 변수에 할당할 문자열 포맷 형식"
    )
    input_keys: List[InputKey] = Field(
        default=[], description="node에서 사용할 input_keys."
    )
    output_keys: List[OutputKey] = Field(
        default=[], description="node에서 사용할 output_keys."
    )


class ReviewerDataSchema(BaseModel):
    """Reviewer 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    serving_name: Optional[str] = Field(
        default=None, description="Model Gateway 호출할 때 사용할 Model의 serving_name"
    )
    serving_model: Optional[str] = Field(
        default=None, description="LLM Model의 이름(타입)"
    )
    prompt_id: Optional[str] = Field(default=None, description="ID of Prompt")
    max_review_attempts: Optional[int] = Field(
        default=3, description="Maximum number of review attempts"
    )
    input_keys: List[InputKey] = Field(
        default=[], description="node에서 사용할 input_keys."
    )
    output_keys: List[OutputKey] = Field(
        default=[], description="node에서 사용할 output_keys."
    )


class ReviewerRequired(ReviewerDataSchema):
    """필수 Reviewer 노드 데이터"""

    serving_name: str
    input_keys: List[InputKeyRequired]


class RetrieverDataSchema(BaseModel):
    """Retriever Knowledge 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: str = Field(description="Node의 이름")
    description: Optional[str] = Field(default=None, description="description of node")
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")
    knowledge_retriever: RetrievalKnowledge


class RetrieverRequired(RetrieverDataSchema):
    """필수 Retriever Knowledge 노드 데이터"""

    knowledge_retriever: RetrievalKnowledgeRequired
    input_keys: List[InputKeyRequired]


class QueryRewriterDataSchema(BaseModel):
    """Query Rewriter 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default=None, description="description of node")
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")
    query_rewriter: QueryRewriter


class QueryRewriterRequired(QueryRewriterDataSchema):
    """필수 Query Rewriter 노드 데이터"""

    query_rewriter: QueryRewriterRequired
    input_keys: List[InputKeyRequired]


class ContextRefinerDataSchema(BaseModel):
    """Context Refiner 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default=None, description="description of node")
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")
    context_refiner: ContextRefiner


class ContextRefinerRequired(ContextRefinerDataSchema):
    """필수 Context Refiner 노드 데이터"""

    context_refiner: ContextRefinerRequired
    input_keys: List[InputKeyRequired]


class ContextRerankerDataSchema(BaseModel):
    """Context Reranker 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = Field(default=None, description="description of node")
    input_keys: List[InputKey] = Field(description="node에서 사용할 input_keys.")
    output_keys: List[OutputKey] = Field(description="node에서 사용할 output_keys.")
    context_refiner: ContextReranker


class ContextRerankerRequired(ContextRerankerDataSchema):
    """필수 Context Reranker 노드 데이터"""

    context_refiner: ContextRerankerRequired
    input_keys: List[InputKeyRequired]


class ToolDataSchema(BaseModel):
    """Tool 노드 데이터"""

    type: Optional[str] = None
    id: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")
    name: Optional[str] = None
    tool_id: str = Field(description="선택된 Tool id")
    input_keys: Optional[List[InputKey]] = Field(
        default=None, description="Tool에서 사용 될 Parameter 목록"
    )
    output_keys: Optional[List[OutputKey]] = Field(
        default=None, description="Tool Node 실행 후의 결과가 담길 key의 목록"
    )


class ToolRequired(ToolDataSchema):
    """필수 Tool 노드 데이터"""

    input_keys: List[InputKeyRequired]


class NoteDataSchema(BaseModel):
    """Note 노드 데이터"""

    name: Optional[str] = None
    description: Optional[str] = Field(default="", description="description of node")


# ==================== 노드 스키마 ====================


class NodeType(Enum):
    AGENT__GENERATOR = "agent__generator"
    AGENT__CODER = "agent__coder"
    AGENT__CATEGORIZER = "agent__categorizer"
    AGENT__APP = "agent__app"
    TOOL = "tool"
    MCP = "mcp"
    INPUT__BASIC = "input__basic"
    OUTPUT__CHAT = "output__chat"
    OUTPUT__KEYS = "output__keys"
    RETRIEVER__KNOWLEDGE = "retriever__knowledge"
    RETRIEVER__REWRITER_HYDE = "retriever__rewriter_hyde"
    RETRIEVER__REWRITER_MULTYQUERY = "retriever__rewriter_multiquery"
    RETRIEVER__DOC_RERANKER = "retriever__doc_reranker"
    RETRIEVER__DOC_FUSION = "retriever__doc_fusion"
    RETRIEVER__DOC_COMPRESSOR = "retriever__doc_compressor"
    RETRIEVER__DOC_FILTER = "retriever__doc_filter"
    CONDITION = "condition"
    UNION = "union"
    AGENT__REVIEWER = "agent__reviewer"
    # only for internal use. not used in schema
    _MCP_CLIENT = "_tool__mcp_client"
    PROMPT = "prompt"
    LLM = "llm"
    # will be deprecated
    MERGER = "merger"
    AGENT = "agent"


class NodeSchema(BaseModel):
    """노드 스키마"""

    id: str
    type: Optional[str] = None
    position: Optional[XYPosition] = None
    source_position: Optional[Position] = None
    target_position: Optional[Position] = None
    style: Optional[Dict[str, Any]] = None
    data: Union[
        InputNodeDataSchema,
        OutputKeysDataSchema,
        OutputChatDataSchema,
        RetrieverDataSchema,
        QueryRewriterDataSchema,
        ContextRefinerDataSchema,
        ContextRerankerDataSchema,
        GeneratorDataSchema,
        CoderDataSchema,
        CategorizerDataSchema,
        AgentAppDataSchema,
        ToolDataSchema,
        NoteDataSchema,
        ConditionDataSchema,
        UnionDataSchema,
        ReviewerDataSchema,
    ]

    @model_validator(mode="before")
    def validate_schema(cls, values: dict) -> dict:
        """Node의 id를 data의 id로 자동 설정하고 type에 따라 data의 schema를 지정"""
        non_runnable_schema = {"note": NoteDataSchema}
        type_to_schema: dict[str, Type[BaseModel]] = {
            NodeType.TOOL.value: ToolDataSchema,
            NodeType.AGENT__GENERATOR.value: GeneratorDataSchema,
            NodeType.AGENT__CODER.value: CoderDataSchema,
            NodeType.AGENT__CATEGORIZER.value: CategorizerDataSchema,
            NodeType.AGENT__APP.value: AgentAppDataSchema,
            NodeType.INPUT__BASIC.value: InputNodeDataSchema,
            NodeType.OUTPUT__KEYS.value: OutputKeysDataSchema,
            NodeType.OUTPUT__CHAT.value: OutputChatDataSchema,
            NodeType.RETRIEVER__REWRITER_HYDE.value: QueryRewriterDataSchema,
            NodeType.RETRIEVER__REWRITER_MULTYQUERY.value: QueryRewriterDataSchema,
            NodeType.RETRIEVER__KNOWLEDGE.value: RetrieverDataSchema,
            NodeType.RETRIEVER__DOC_RERANKER.value: ContextRerankerDataSchema,
            NodeType.RETRIEVER__DOC_COMPRESSOR.value: ContextRefinerDataSchema,
            NodeType.RETRIEVER__DOC_FILTER.value: ContextRefinerDataSchema,
            NodeType.CONDITION.value: ConditionDataSchema,
            NodeType.UNION.value: UnionDataSchema,
            NodeType.AGENT__REVIEWER.value: ReviewerDataSchema,
        }

        node_type = values["type"]
        if node_type in non_runnable_schema:
            data = values.get("data")
            values["data"] = non_runnable_schema[node_type](**data)

        elif node_type in type_to_schema:
            schema = type_to_schema[node_type]
            try:
                # values["data"]가 이미 스키마 객체인지 확인
                if isinstance(values["data"], schema):
                    # 이미 올바른 스키마 객체인 경우
                    values["data"].id = values["id"]
                    values["data"].type = node_type
                else:
                    # 딕셔너리인 경우 스키마 객체로 변환
                    values["data"] = schema(**values["data"])
                    values["data"].id = values["id"]
                    values["data"].type = node_type
            except ValidationError as e:
                raise ValueError(
                    f"Invalid data for type {node_type}: {e}",
                )

        else:
            raise ValueError(
                f"Invalid type: {node_type}. Node type must be one of {type_to_schema.keys()}",
            )

        return values


# ==================== 엣지 스키마 ====================


class EdgeGraphSchema(BaseModel):
    """엣지 스키마"""

    id: str = Field(description="edge의 id")
    type: Optional[str] = Field(
        default=None, description="edge의 type 종류: none -> 기본, case -> 조건분기"
    )
    source: Optional[str] = Field(default=None, description="edge의 시작 node의 id")
    target: Optional[str] = Field(default=None, description="edge의 끝 node의 id")
    source_handle: Optional[str] = Field(
        default=None, description="edge의 시작 node의 핸들러"
    )
    target_handle: Optional[str] = Field(
        default=None, description="edge의 끝 node의 핸들러"
    )
    sourceHandle: Optional[str] = Field(
        default=None, description="edge의 시작 node의 핸들러 (camelCase)"
    )
    targetHandle: Optional[str] = Field(
        default=None, description="edge의 끝 node의 핸들러 (camelCase)"
    )
    marker_start: Optional[Any] = Field(default=None, description="edge의 시작 마커")
    marker_end: Optional[Any] = Field(default=None, description="edge의 끝 마커")
    reconnectable: Optional[str] = None
    condition_label: Optional[str] = Field(
        default=None, description="type이 case일때 사용하는 조건값"
    )


# ==================== 그래프 스키마 ====================


class GraphSchema(BaseModel):
    """그래프 스키마"""

    nodes: List[NodeSchema] = []
    edges: List[EdgeGraphSchema] = []


# ==================== 요청/응답 스키마 ====================


class AgentGraphCreateRequest(BaseModel):
    """Agent Graph 생성 요청 (직접 정의)"""

    name: str
    description: str
    graph: GraphSchema


class AgentGraphTemplateRequest(BaseModel):
    """Agent Graph 템플릿 생성 요청"""

    name: str
    description: str
    template_id: str


class AgentGraphResponse(BaseModel):
    """Agent Graph 응답"""

    id: str
    name: str
    description: str
    edges: List[EdgeGraphSchema] = []
    nodes: List[NodeSchema] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: Optional[str] = "active"
    project_id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @property
    def graph(self) -> GraphSchema:
        """graph 속성을 동적으로 생성"""
        return GraphSchema(nodes=self.nodes, edges=self.edges)


# ==================== 기존 호환성을 위한 별칭 ====================

# 기존 코드와의 호환성을 위해 별칭 제공
InputKeyData = InputKey
OutputKeyData = OutputKey
NodeData = NodeSchema
EdgeData = EdgeGraphSchema
GraphData = GraphSchema


class Message(BaseModel):
    content: str
    type: Literal["human", "ai"]
    model_config = ConfigDict(extra="allow")


class InputBody(BaseModel):
    messages: list[Message]
    additional_kwargs: dict = {}
    model_config = ConfigDict(extra="allow")
    # langraph에서 extra=allow가 허용이 안되기 때문에 additional_kwargs 추가


class GraphRequestBody(BaseModel):
    graph_id: str
    input_data: InputBody
    config: dict | None = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "graph_id": "9deaa8f7-32af-47e7-aa58-d59bc8f047c3",
                    "input_data": {
                        "messages": [
                            {"content": "내 이름은 HANI야", "type": "human"},
                            {"content": "안녕하세요 HANI", "type": "ai"},
                            {"content": "내 이름이 뭐게?", "type": "human"},
                        ]
                    },
                }
            ]
        }
    }
