"""
Agent Graph Builder - 사용자가 노드와 엣지를 추가하여 그래프를 구성할 수 있는 빌더 클래스
"""

from typing import Dict, Any, List, Optional, Union
import os
from .graph_client import AgentGraphClient
from .app_client import AgentAppClient, AgentApp
from .graph_schemas import (
    AgentGraphResponse,
    InputKey,
    OutputKey,
    XYPosition,
    Position,
    RetrievalKnowledge,
    NodeSchema,
    InputNodeDataSchema,
    OutputKeysDataSchema,
    OutputChatDataSchema,
    GeneratorDataSchema,
    CoderDataSchema,
    CategorizerDataSchema,
    AgentAppDataSchema,
    ToolDataSchema,
    NoteDataSchema,
    ConditionDataSchema,
    UnionDataSchema,
    ReviewerDataSchema,
    RetrieverDataSchema,
    QueryRewriterDataSchema,
    IntentCategory,
    ContextRefinerDataSchema,
    ContextRerankerDataSchema,
    EdgeGraphSchema,
    QueryRewriter,
    ContextReranker,
    ContextRefiner,
    InputBody,
    GraphRequestBody,
)
from langchain_core.runnables import RunnableConfig


class AgentGraphBuilder:
    """
    Agent Graph를 프로그래밍 방식으로 구성할 수 있는 빌더 클래스

    사용 예시:
        # 새 그래프 생성
        builder = AgentGraphBuilder("research_flow", "search from wikipedia and create answer")
        builder.add_input_node("input", "inputnode_id")
        builder.add_generator_node("Researcher", "agent_id",
                                 serving_name="GIP/gpt-4o",
                                 serving_model="gpt-4o",
                                 input_keys=[{"keytable_id": "query_inputnode_id", "name": "query", "required": "true"}],
                                 output_keys=[{"keytable_id": "content_agent_id", "name": "content"}])
        builder.add_output_chat_node("output", "outputnode_id", "{{content_agent_id}}")
        builder.add_edge("inputnode_id", "agent_id")
        builder.add_edge("agent_id", "outputnode_id")
        result = builder.save()

        # 기존 그래프 로드 후 수정
        builder = AgentGraphBuilder("", "")
        builder.load_existing_graph("graph_id")

        # 노드 조회 및 수정
        nodes = builder.list_nodes()  # 모든 노드 정보 확인
        generator_nodes = builder.get_nodes_by_type("generator")  # generator 타입 노드들만

        # 특정 노드 수정
        builder.update_node("agent_id", name="Updated Researcher", description="Updated description")

        # 노드 제거 (연결된 엣지도 함께 제거)
        builder.remove_node("unused_node_id")

        # 엣지 제거
        builder.remove_edge("source_id", "target_id")

        # 수정된 그래프 저장
        result = builder.save()
    """

    def __init__(
        self, name: str, description: str, client: Optional[AgentGraphClient] = None
    ):
        """
        AgentGraphBuilder 초기화

        Args:
            name: 그래프 이름
            description: 그래프 설명
            client: AgentGraphClient 인스턴스 (없으면 새로 생성)
        """
        self.name = name
        self.description = description

        # 클라이언트가 없으면 자동 생성 (환경변수에서 API 키 읽기)
        if client is None:
            api_key = os.getenv("AGENT_GRAPH_API_KEY")
            self.client = AgentGraphClient("https://aip-stg.sktai.io", api_key=api_key)
        else:
            self.client = client

        # 그래프 구성 요소들
        self.nodes: List[NodeSchema] = []
        self.edges: List[EdgeGraphSchema] = []
        self._edge_counter = 0

        # 저장된 그래프 ID (업데이트용)
        self._saved_graph_id: Optional[str] = None

        # 자동 배치를 위한 카운터
        self._node_counter = 0

        # keytable_id 생성을 위한 매핑 테이블
        self._keytable_mapping = {}

    def add_input_node(
        self,
        name: str,
        node_id: str,
        description: str = "",
        x: Optional[int] = None,
        y: Optional[int] = None,
        input_keys: Optional[List[InputKey]] = None,
    ) -> "AgentGraphBuilder":
        """
        input__basic 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            description: 노드 설명 (선택사항)
            x: x 좌표 (None이면 자동 배치)
            y: y 좌표 (None이면 자동 배치)
            input_keys: 입력 키 목록 (None이면 기본 query 필드 추가)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # 현재 노드 ID 설정 (헬퍼 함수에서 사용)
        self._current_node_id = node_id

        # 자동 배치
        if x is None:
            x = 100 + (self._node_counter * 300)
        if y is None:
            y = 100
        self._node_counter += 1

        # 기본 input_keys 설정
        if input_keys is None:
            input_keys = [
                InputKey(keytable_id=f"query_{node_id}", name="query", required=True),
                InputKey(
                    keytable_id=f"context_{node_id}", name="context", required=False
                ),
            ]

        # Input 노드의 출력 키 생성 (입력 키와 동일한 이름으로)
        output_keys = []
        for input_key in input_keys:
            output_keys.append(
                OutputKey(keytable_id=input_key.keytable_id, name=input_key.name)
            )

        # InputNodeDataSchema 생성
        data_schema = InputNodeDataSchema(
            name=name,
            description=description or "",
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="input__basic",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_generator_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        serving_model: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        prompt_id: str = "",
        fewshot_id: str = "",
        tool_ids: List[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> "AgentGraphBuilder":
        """
        agent__generator 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름 (예: "GIP/gpt-4o")
            serving_model: 서빙 모델 (예: "gpt-4o")
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "content" 생성)
            description: 노드 설명 (선택사항)
            prompt_id: 프롬프트 ID (선택사항)
            fewshot_id: Few-shot ID (선택사항)
            tool_ids: 도구 ID 목록 (선택사항)
            x: x 좌표 (None이면 자동 배치)
            y: y 좌표 (None이면 자동 배치)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # 자동 배치
        if x is None:
            x = 100 + (self._node_counter * 300)
        if y is None:
            y = 100
        self._node_counter += 1
        if tool_ids is None:
            tool_ids = []

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Generator 노드는 무조건 "content"로 자동 생성
            output_keys = [self.create_output_key("content", node_id)]

        # GeneratorDataSchema 생성
        data_schema = GeneratorDataSchema(
            name=name,
            description=description,
            serving_name=serving_name,
            serving_model=serving_model,
            prompt_id=prompt_id,
            fewshot_id=fewshot_id,
            tool_ids=tool_ids,
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="agent__generator",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_output_chat_node(
        self,
        name: str,
        node_id: str,
        format_string: str,
        description: str = "",
        x: Optional[int] = None,
        y: Optional[int] = None,
    ) -> "AgentGraphBuilder":
        """
        output__chat 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            format_string: 포맷 문자열 (예: "{{content_agent_id}}")
            description: 노드 설명 (선택사항)
            x: x 좌표 (None이면 자동 배치)
            y: y 좌표 (None이면 자동 배치)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # 자동 배치
        if x is None:
            x = 100 + (self._node_counter * 300)
        if y is None:
            y = 100
        self._node_counter += 1
        # OutputChatDataSchema 생성
        data_schema = OutputChatDataSchema(
            type="output__chat",
            id=node_id,
            name=name,
            description=description,
            format_string=format_string,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="output__chat",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_categorizer_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        serving_model: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        categories: List[Dict[str, Any]] = None,
        prompt_id: str = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        agent__categorizer 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름
            serving_model: 서빙 모델
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "selected" 생성)
            categories: 분류할 카테고리 목록 (선택사항)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        if categories is None:
            categories = []

        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Categorizer 노드는 무조건 "selected"로 자동 생성
            output_keys = [self.create_output_key("selected", node_id)]

        # categories를 IntentCategory 스키마로 변환
        intent_categories = []
        for cat in categories:
            intent_cat = IntentCategory(
                id=cat.get("id"),
                name=cat.get("name"),
                category=cat.get("category"),
                description=cat.get("description"),
            )
            intent_categories.append(intent_cat)

        # CategorizerDataSchema 생성
        data_schema = CategorizerDataSchema(
            name=name,
            description=description,
            serving_name=serving_name,
            serving_model=serving_model,
            prompt_id=prompt_id,
            input_keys=input_keys,
            output_keys=output_keys,
            categories=intent_categories,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="agent__categorizer",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_coder_node(
        self,
        name: str,
        node_id: str,
        code: str,
        output_keys: Optional[List[OutputKey]] = None,
        input_keys: List[InputKey] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        agent__coder 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            code: 실행할 코드
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "content" 생성)
            input_keys: 입력 키 목록 (선택사항)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        if input_keys is None:
            input_keys = []

        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Coder 노드는 무조건 "content"로 자동 생성
            output_keys = [self.create_output_key("content", node_id)]

        # CoderDataSchema 생성
        data_schema = CoderDataSchema(
            name=name,
            description=description,
            code=code,
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="agent__coder",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_tool_node(
        self,
        name: str,
        node_id: str,
        tool_id: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        tool 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            tool_id: 도구 ID
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "content" 생성)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Tool 노드는 무조건 "content"로 자동 생성
            output_keys = [self.create_output_key("content", node_id)]

        # ToolDataSchema 생성
        data_schema = ToolDataSchema(
            name=name,
            description=description,
            tool_id=tool_id,
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="tool",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_knowledge_retriever_node(
        self,
        name: str,
        node_id: str,
        knowledge_id: str,
        retrieval_config: Dict[str, Any],
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        retriever__knowledge 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            knowledge_id: 지식베이스 ID
            retrieval_config: 검색 설정
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "context"와 "docs" 생성)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Knowledge Retriever 노드는 무조건 "context"와 "docs"로 자동 생성
            output_keys = [
                self.create_output_key("context", node_id),
                self.create_output_key("docs", node_id),
            ]

        # RetrievalKnowledge 객체 생성
        knowledge_retriever = RetrievalKnowledge(
            repo_id=knowledge_id,
            project_id=retrieval_config.get("project_id", ""),
            embedding_info=None,
            knowledge_info=None,
            retrieval_options={
                "top_k": retrieval_config.get("k", 5),
                "filter": retrieval_config.get("filter", None),
                "keywords": retrieval_config.get("keywords", []),
                "order_by": retrieval_config.get("order_by", None),
                "threshold": retrieval_config.get("threshold", 0.3),
                "retrieval_mode": retrieval_config.get("retrieval_mode", "dense"),
                "doc_format_metafieds": retrieval_config.get(
                    "doc_format_metafieds", []
                ),
            },
            vectordb_conn_info=None,
            active_collection_id=retrieval_config.get("active_collection_id", ""),
        )

        # RetrieverDataSchema 생성
        data_schema = RetrieverDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            knowledge_retriever=knowledge_retriever,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__knowledge",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_output_keys_node(
        self, name: str, node_id: str, input_keys: List[InputKey], description: str = ""
    ) -> "AgentGraphBuilder":
        """
        output__keys 노드 추가

        Args:
            name: 노드 이름
            node_id: 노드 ID
            input_keys: 입력 키 목록
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # OutputKeysDataSchema 생성
        data_schema = OutputKeysDataSchema(
            name=name, description=description, input_keys=input_keys
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="output__keys",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_condition_node(
        self,
        name: str,
        node_id: str,
        condition_config: Dict[str, Any],
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        condition 노드 추가 (조건 분기)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            condition_config: 조건 설정
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "selected" 생성)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Condition 노드는 무조건 "selected"로 자동 생성
            output_keys = [self.create_output_key("selected", node_id)]

        # ConditionDataSchema 생성
        data_schema = ConditionDataSchema(
            name=name,
            description=description,
            conditions=condition_config.get("conditions", []),
            default_condition=condition_config.get(
                "default_condition", "condition-else"
            ),
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="condition",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_union_node(
        self,
        name: str,
        node_id: str,
        union_config: Dict[str, Any],
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        output_key_name: Optional[str] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        union 노드 추가 (데이터 병합)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            union_config: 병합 설정
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, output_key_name이 있으면 자동 생성)
            output_key_name: 출력 키 이름 (선택사항, 지정하면 자동으로 output_keys 생성)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (output_key_name이 지정된 경우)
        if output_key_name and output_keys is None:
            output_keys = [self.create_output_key(output_key_name, node_id)]
        elif output_keys is None:
            raise ValueError(
                "output_keys 또는 output_key_name 중 하나는 반드시 지정해야 합니다."
            )

        # UnionDataSchema 생성
        data_schema = UnionDataSchema(
            name=name,
            description=description,
            format_string=union_config.get("format_string", ""),
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="union",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_reviewer_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        serving_model: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        prompt_id: str = "",
        fewshot_id: str = "",
        tool_ids: List[str] = None,
        max_review_attempts: int = 3,
    ) -> "AgentGraphBuilder":
        """
        agent__reviewer 노드 추가 (검토/리뷰)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름
            serving_model: 서빙 모델
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "selected"와 "reason" 생성)
            description: 노드 설명 (선택사항)
            prompt_id: 프롬프트 ID (선택사항)
            fewshot_id: Few-shot ID (선택사항)
            tool_ids: 도구 ID 목록 (선택사항)
            max_review_attempts: 최대 검토 시도 횟수 (기본값: 3)

        Returns:
            self (메서드 체이닝을 위해)
        """
        if tool_ids is None:
            tool_ids = []

        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Reviewer 노드는 무조건 "selected"와 "reason"으로 자동 생성
            output_keys = [
                self.create_output_key("selected", node_id),
                self.create_output_key("reason", node_id),
            ]

        # ReviewerDataSchema 생성
        data_schema = ReviewerDataSchema(
            name=name,
            description=description,
            serving_name=serving_name,
            serving_model=serving_model,
            prompt_id=prompt_id,
            max_review_attempts=max_review_attempts,
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="agent__reviewer",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_hyde_rewriter_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        prompt: str = "",
        include_ori_query: bool = False,
    ) -> "AgentGraphBuilder":
        """
        retriever__rewriter_hyde 노드 추가 (HyDE 리라이터)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름 (LLM 모델)
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "rewritten_queries" 생성)
            description: 노드 설명 (선택사항)
            prompt: 프롬프트 (선택사항)
            include_ori_query: 원본 쿼리 포함 여부 (기본값: False)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # HyDE Rewriter 노드는 무조건 "rewritten_queries"로 자동 생성
            output_keys = [self.create_output_key("rewritten_queries", node_id)]

        # QueryRewriter 객체 생성
        query_rewriter = QueryRewriter(
            llm_chain={
                "llm_config": {"api_key": "", "serving_name": serving_name},
                "prompt": prompt,
            },
            include_ori_query=include_ori_query,
        )

        # QueryRewriterDataSchema 생성
        data_schema = QueryRewriterDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            query_rewriter=query_rewriter,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__rewriter_hyde",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_multiquery_rewriter_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        prompt: str = "",
        include_ori_query: bool = False,
    ) -> "AgentGraphBuilder":
        """
        retriever__rewriter_multiquery 노드 추가 (멀티쿼리 리라이터)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름 (LLM 모델)
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "rewritten_queries" 생성)
            description: 노드 설명 (선택사항)
            prompt: 프롬프트 (선택사항)
            include_ori_query: 원본 쿼리 포함 여부 (기본값: False)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # MultiQuery Rewriter 노드는 무조건 "rewritten_queries"로 자동 생성
            output_keys = [self.create_output_key("rewritten_queries", node_id)]

        # QueryRewriter 객체 생성
        query_rewriter = QueryRewriter(
            llm_chain={
                "llm_config": {"api_key": "", "serving_name": serving_name},
                "prompt": prompt,
            },
            include_ori_query=include_ori_query,
        )

        # QueryRewriterDataSchema 생성
        data_schema = QueryRewriterDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            query_rewriter=query_rewriter,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__rewriter_multiquery",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_doc_reranker_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        top_k: int = 10,
    ) -> "AgentGraphBuilder":
        """
        retriever__doc_reranker 노드 추가 (문서 재순위)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름 (LLM 모델)
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "context" 생성)
            description: 노드 설명 (선택사항)
            top_k: 상위 K개 문서 선택 (기본값: 10)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Doc Reranker 노드는 무조건 "context"로 자동 생성
            output_keys = [self.create_output_key("context", node_id)]

        # ContextReranker 객체 생성
        context_refiner = ContextReranker(
            rerank_cnf={
                "top_k": top_k,
                "model_info": {"api_key": "", "serving_name": serving_name},
            }
        )

        # ContextRerankerDataSchema 생성
        data_schema = ContextRerankerDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            context_refiner=context_refiner,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__doc_reranker",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_doc_compressor_node(
        self,
        name: str,
        node_id: str,
        repo_id: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        serving_name: str = "",
        retrieval_options: Dict[str, Any] = None,
    ) -> "AgentGraphBuilder":
        """
        retriever__doc_compressor 노드 추가 (문서 압축)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            repo_id: 저장소 ID
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "context" 생성)
            description: 노드 설명 (선택사항)
            serving_name: 서빙 이름 (선택사항)
            retrieval_options: 검색 옵션 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        if retrieval_options is None:
            retrieval_options = {}

        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Doc Compressor 노드는 무조건 "context"로 자동 생성
            output_keys = [self.create_output_key("context", node_id)]

        # ContextRefiner 객체 생성
        context_refiner = ContextRefiner(
            llm_chain={
                "prompt": "",
                "llm_config": {"api_key": "", "serving_name": serving_name},
            }
        )

        # ContextRefinerDataSchema 생성
        data_schema = ContextRefinerDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            context_refiner=context_refiner,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__doc_compressor",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_doc_filter_node(
        self,
        name: str,
        node_id: str,
        serving_name: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
        prompt: str = "",
    ) -> "AgentGraphBuilder":
        """
        retriever__doc_filter 노드 추가 (문서 필터)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            serving_name: 서빙 이름 (LLM 모델)
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "context" 생성)
            description: 노드 설명 (선택사항)
            prompt: 프롬프트 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # Doc Filter 노드는 무조건 "context"로 자동 생성
            output_keys = [self.create_output_key("context", node_id)]

        # ContextRefiner 객체 생성
        context_refiner = ContextRefiner(
            llm_chain={
                "prompt": prompt,
                "llm_config": {"api_key": "", "serving_name": serving_name},
            }
        )

        # ContextRefinerDataSchema 생성
        data_schema = ContextRefinerDataSchema(
            name=name,
            description=description,
            input_keys=input_keys,
            output_keys=output_keys,
            context_refiner=context_refiner,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="retriever__doc_filter",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_app_node(
        self,
        name: str,
        node_id: str,
        agent_app_id: str,
        api_key: str,
        input_keys: List[InputKey],
        output_keys: Optional[List[OutputKey]] = None,
        description: str = "",
    ) -> "AgentGraphBuilder":
        """
        agent__app 노드 추가 (외부 앱 호출)

        Args:
            name: 노드 이름
            node_id: 노드 ID
            agent_app_id: Agent App ID
            api_key: API 키 (필수)
            input_keys: 입력 키 목록
            output_keys: 출력 키 목록 (선택사항, 지정하지 않으면 자동으로 "content" 생성)
            description: 노드 설명 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        # position 자동 계산
        if not hasattr(self, "_node_counter"):
            self._node_counter = 0
        x = 100 + (self._node_counter * 300)
        y = 100
        self._node_counter += 1

        # output_keys 자동 생성 (지정되지 않은 경우)
        if output_keys is None:
            # App 노드는 무조건 "content"로 자동 생성
            output_keys = [self.create_output_key("content", node_id)]

        # AgentAppDataSchema 생성
        data_schema = AgentAppDataSchema(
            name=name,
            description=description,
            agent_app_id=agent_app_id,
            api_key=api_key,
            input_keys=input_keys,
            output_keys=output_keys,
        )

        # NodeSchema 생성
        node_schema = NodeSchema(
            id=node_id,
            type="agent__app",
            position=XYPosition(x=x, y=y),
            source_position="right",
            target_position="left",
            data=data_schema,
        )

        self.nodes.append(node_schema)
        return self

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "none",
        condition_label: str = None,
        source_handle: str = None,
        target_handle: str = None,
    ) -> "AgentGraphBuilder":
        """
        엣지 추가

        Args:
            source_id: 소스 노드 ID
            target_id: 타겟 노드 ID
            edge_type: 엣지 타입 (기본값: "none")
            condition_label: 조건부 엣지의 라벨 (선택사항)
            source_handle: 소스 핸들 (선택사항)
            target_handle: 타겟 핸들 (선택사항)

        Returns:
            self (메서드 체이닝을 위해)
        """
        edge_id = f"edge_{self._edge_counter}"
        self._edge_counter += 1

        # 엣지 연결 시 자동 keytable_id 매핑
        self._auto_map_keytable_ids(source_id, target_id)

        # EdgeGraphSchema 생성
        edge_schema = EdgeGraphSchema(
            id=edge_id,
            source=source_id,
            target=target_id,
            type=edge_type,
            condition_label=condition_label,
            source_handle=source_handle,
            target_handle=target_handle,
            sourceHandle=source_handle,  # camelCase 버전도 설정
            targetHandle=target_handle,  # camelCase 버전도 설정
        )

        self.edges.append(edge_schema)
        return self

    def get_graph_data(self) -> Dict[str, Any]:
        """
        현재 구성된 그래프 데이터 반환 (graph 부분만)

        Returns:
            그래프 데이터 딕셔너리
        """
        return {
            "nodes": [node.model_dump() for node in self.nodes],
            "edges": [edge.model_dump() for edge in self.edges],
        }

    def get_full_payload(self) -> Dict[str, Any]:
        """
        전체 API 페이로드 반환 (name, description, graph 포함)

        Returns:
            전체 API 페이로드 딕셔너리
        """
        return {
            "name": self.name,
            "description": self.description,
            "graph": {
                "nodes": [node.model_dump() for node in self.nodes],
                "edges": [edge.model_dump() for edge in self.edges],
            },
        }

    def save(self) -> AgentGraphResponse:
        """
        그래프 저장 (생성 또는 업데이트)

        Returns:
            AgentGraphResponse: 저장된 그래프 정보
        """
        graph_data = self.get_graph_data()

        if self._saved_graph_id:
            # 이미 저장된 그래프가 있으면 업데이트
            return self.client.update(
                graph_id=self._saved_graph_id,
                name=self.name,
                description=self.description,
                graph_data=graph_data,
            )
        else:
            # 새 그래프 생성
            result = self.client.create_direct(
                name=self.name, description=self.description, graph_data=graph_data
            )
            # 생성된 그래프 ID 저장 (향후 업데이트용)
            self._saved_graph_id = result.id
            return result

    # ------------------------------------------------------------
    # 배포: 생성된 그래프를 Agent App으로 배포
    # ------------------------------------------------------------
    def deploy(
        self,
        *,
        name: str,
        description: str = "",
        serving_type: str = "shared",
        version_description: str = "",
        cpu_request: int | None = None,
        cpu_limit: int | None = None,
        mem_request: int | None = None,
        mem_limit: int | None = None,
        min_replicas: int | None = None,
        max_replicas: int | None = None,
        workers_per_core: int | None = None,
    ) -> AgentApp:
        """현재 빌더 상태를 저장하고 해당 그래프를 Agent App으로 배포한다.

        요구사항:
        - target_id: graph ID
        - target_type: "agent_graph"
        - serving_type: "shared"(기본) 또는 "standalone"
        """

        if self._saved_graph_id:
            # 이미 저장된 그래프가 있으면 그 ID 사용
            target_graph_id = self._saved_graph_id
        else:
            # 새 그래프라면 저장
            result = self.save()
            target_graph_id = result.id

        app_client = AgentAppClient(self.client.credentials)
        app = app_client.deploy(
            target_id=target_graph_id,
            name=name,
            description=description,
            target_type="agent_graph",
            serving_type=serving_type,
            version_description=version_description or description,
            cpu_request=cpu_request,
            cpu_limit=cpu_limit,
            mem_request=mem_request,
            mem_limit=mem_limit,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            workers_per_core=workers_per_core,
        )
        return app

    def load_existing_graph(self, graph_id: str) -> "AgentGraphBuilder":
        """
        기존 그래프를 로드하여 수정 가능한 상태로 만들기

        Args:
            graph_id: 로드할 그래프 ID

        Returns:
            self (메서드 체이닝을 위해)
        """
        existing_graph = self.client.read(graph_id)

        # 기존 그래프 정보로 업데이트
        self.name = existing_graph.name
        self.description = existing_graph.description

        # 딕셔너리를 NodeSchema와 EdgeGraphSchema로 변환
        self.nodes = [
            NodeSchema.model_validate(node) for node in existing_graph.graph.nodes
        ]
        self.edges = [
            EdgeGraphSchema.model_validate(edge) for edge in existing_graph.graph.edges
        ]
        self._saved_graph_id = graph_id

        return self

    def load_from_dict(self, graph_data: Dict[str, Any]) -> "AgentGraphBuilder":
        """
        dict로 부터 그래프 데이터를 로드.
        /agent/agents/graphs/export/code API 그래프를 로드하고 복사하는 예제코드를 제공하는데, 이 함수를 사용한 예제코드입니다.
        """
        self.nodes = [NodeSchema.model_validate(node) for node in graph_data["nodes"]]
        self.edges = [
            EdgeGraphSchema.model_validate(edge) for edge in graph_data["edges"]
        ]
        return self

    def clear(self) -> "AgentGraphBuilder":
        """
        현재 구성된 노드와 엣지 모두 제거

        Returns:
            self (메서드 체이닝을 위해)
        """
        self.nodes = []
        self.edges = []
        self._edge_counter = 0
        return self

    # ====================================================================
    # 그래프 수정을 위한 편의 메서드들 (load_existing_graph 후 사용)
    # ====================================================================

    def get_node(self, node_id: str) -> Optional[NodeSchema]:
        """
        특정 ID의 노드 조회

        Args:
            node_id: 조회할 노드 ID

        Returns:
            NodeSchema 객체 또는 None
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_nodes_by_type(self, node_type: str) -> List[NodeSchema]:
        """
        특정 타입의 노드들 조회

        Args:
            node_type: 노드 타입 (예: "input__basic", "generator", "output__chat")

        Returns:
            해당 타입의 노드 리스트
        """
        return [node for node in self.nodes if node.type == node_type]

    def update_node(self, node_id: str, **kwargs) -> "AgentGraphBuilder":
        """
        특정 노드 업데이트

        Args:
            node_id: 업데이트할 노드 ID
            **kwargs: 업데이트할 필드들

        Returns:
            self (메서드 체이닝을 위해)

        Raises:
            ValueError: 노드를 찾을 수 없는 경우
        """
        node = self.get_node(node_id)
        if node is None:
            raise ValueError(f"Node with ID '{node_id}' not found")

        # 노드 필드 업데이트 (data 필드 내부의 속성들)
        for key, value in kwargs.items():
            if hasattr(node.data, key):
                setattr(node.data, key, value)
            elif hasattr(node, key):
                setattr(node, key, value)
            else:
                raise ValueError(f"Node does not have field '{key}'")

        return self

    def remove_node(self, node_id: str) -> "AgentGraphBuilder":
        """
        특정 노드 제거 (연결된 엣지도 함께 제거)

        Args:
            node_id: 제거할 노드 ID

        Returns:
            self (메서드 체이닝을 위해)
        """
        # 노드 제거
        self.nodes = [node for node in self.nodes if node.id != node_id]

        # 해당 노드와 연결된 엣지들도 제거
        self.edges = [
            edge
            for edge in self.edges
            if edge.source != node_id and edge.target != node_id
        ]

        return self

    def get_edge(self, source_id: str, target_id: str) -> Optional[EdgeGraphSchema]:
        """
        특정 엣지 조회

        Args:
            source_id: 소스 노드 ID
            target_id: 타겟 노드 ID

        Returns:
            EdgeGraphSchema 객체 또는 None
        """
        for edge in self.edges:
            if edge.source == source_id and edge.target == target_id:
                return edge
        return None

    def remove_edge(self, source_id: str, target_id: str) -> "AgentGraphBuilder":
        """
        특정 엣지 제거

        Args:
            source_id: 소스 노드 ID
            target_id: 타겟 노드 ID

        Returns:
            self (메서드 체이닝을 위해)
        """
        self.edges = [
            edge
            for edge in self.edges
            if not (edge.source == source_id and edge.target == target_id)
        ]
        return self

    def get_connected_nodes(self, node_id: str) -> Dict[str, List[str]]:
        """
        특정 노드와 연결된 노드들 조회

        Args:
            node_id: 기준 노드 ID

        Returns:
            {"inputs": [입력 노드들], "outputs": [출력 노드들]}
        """
        inputs = []
        outputs = []

        for edge in self.edges:
            if edge.target == node_id:
                inputs.append(edge.source)
            elif edge.source == node_id:
                outputs.append(edge.target)

        return {"inputs": inputs, "outputs": outputs}

    def list_nodes(self) -> List[Dict[str, Any]]:
        """
        현재 그래프의 모든 노드 정보를 보기 좋게 출력

        Returns:
            노드 정보 리스트
        """
        node_info = []
        for node in self.nodes:
            connected = self.get_connected_nodes(node.id)

            # data 필드에서 name과 description 가져오기
            node_name = (
                getattr(node.data, "name", "Unknown")
                if hasattr(node.data, "name")
                else "Unknown"
            )
            node_description = (
                getattr(node.data, "description", "")
                if hasattr(node.data, "description")
                else ""
            )

            node_info.append(
                {
                    "id": node.id,
                    "name": node_name,
                    "type": node.type,
                    "description": node_description,
                    "connected_inputs": connected["inputs"],
                    "connected_outputs": connected["outputs"],
                }
            )
        return node_info

    def list_edges(self) -> List[Dict[str, Any]]:
        """
        현재 그래프의 모든 엣지 정보를 보기 좋게 출력

        Returns:
            엣지 정보 리스트
        """
        edge_info = []
        for edge in self.edges:
            edge_info.append(
                {
                    "source": edge.source,
                    "target": edge.target,
                    "source_port": getattr(edge, "source_port", None),
                    "target_port": getattr(edge, "target_port", None),
                }
            )
        return edge_info

    def __str__(self) -> str:
        """문자열 표현"""
        return f"AgentGraphBuilder(name='{self.name}', nodes={len(self.nodes)}, edges={len(self.edges)})"

    def __repr__(self) -> str:
        """개발자용 문자열 표현"""
        return self.__str__()

    def validate_required_inputs(self) -> Dict[str, Any]:
        """
        필수 InputKey가 제대로 설정되었는지 검증

        Returns:
            검증 결과 딕셔너리
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "missing_inputs": [],
            "unconnected_inputs": [],
        }

        # 각 노드의 필수 입력 확인
        for node in self.nodes:
            if hasattr(node.data, "input_keys") and node.data.input_keys:
                for input_key in node.data.input_keys:
                    if input_key.required and not input_key.keytable_id:
                        validation_result["is_valid"] = False
                        validation_result["errors"].append(
                            f"노드 '{node.id}'의 필수 입력 '{input_key.name}'에 keytable_id가 없습니다"
                        )
                        validation_result["missing_inputs"].append(
                            {
                                "node_id": node.id,
                                "node_name": getattr(node.data, "name", "Unknown"),
                                "input_name": input_key.name,
                                "input_key": input_key,
                            }
                        )

        # 연결되지 않은 입력 확인
        connected_inputs = set()
        for edge in self.edges:
            connected_inputs.add(edge.target)

        for node in self.nodes:
            if hasattr(node.data, "input_keys") and node.data.input_keys:
                for input_key in node.data.input_keys:
                    if input_key.keytable_id and not self._is_input_connected(
                        input_key.keytable_id, node.type
                    ):
                        validation_result["warnings"].append(
                            f"노드 '{node.id}'의 입력 '{input_key.name}' (keytable_id: {input_key.keytable_id})이 연결되지 않았습니다"
                        )
                        validation_result["unconnected_inputs"].append(
                            {
                                "node_id": node.id,
                                "node_name": getattr(node.data, "name", "Unknown"),
                                "input_name": input_key.name,
                                "keytable_id": input_key.keytable_id,
                            }
                        )

        return validation_result

    def _is_input_connected(self, keytable_id: str, node_type: str) -> bool:
        """특정 keytable_id가 다른 노드의 출력과 연결되어 있는지 확인"""

        # Input 노드는 외부에서 데이터를 받으므로 항상 연결된 것으로 간주
        if node_type == "input__basic":
            return True

        # 다른 노드들은 실제 출력과 연결되어야 함
        for node in self.nodes:
            if hasattr(node.data, "output_keys") and node.data.output_keys:
                for output_key in node.data.output_keys:
                    if output_key.keytable_id == keytable_id:
                        return True
        return False

    def get_validation_report(self) -> str:
        """
        검증 결과를 읽기 쉬운 형태로 반환

        Returns:
            검증 리포트 문자열
        """
        result = self.validate_required_inputs()

        report = "=== 그래프 검증 리포트 ===\n"

        if result["is_valid"]:
            report += "✅ 그래프가 유효합니다!\n"
        else:
            report += "❌ 그래프에 문제가 있습니다!\n"

        if result["errors"]:
            report += "\n🚨 오류:\n"
            for error in result["errors"]:
                report += f"  - {error}\n"

        if result["warnings"]:
            report += "\n⚠️  경고:\n"
            for warning in result["warnings"]:
                report += f"  - {warning}\n"

        if result["missing_inputs"]:
            report += "\n📋 누락된 필수 입력:\n"
            for missing in result["missing_inputs"]:
                report += f"  - 노드: {missing['node_name']} ({missing['node_id']})\n"
                report += f"    입력: {missing['input_name']}\n"

        if result["unconnected_inputs"]:
            report += "\n🔗 연결되지 않은 입력:\n"
            for unconnected in result["unconnected_inputs"]:
                report += (
                    f"  - 노드: {unconnected['node_name']} ({unconnected['node_id']})\n"
                )
                report += f"    입력: {unconnected['input_name']} (keytable_id: {unconnected['keytable_id']})\n"

        return report

    def _auto_map_keytable_ids(self, source_id: str, target_id: str):
        """
        엣지 연결 시 소스 노드의 출력과 타겟 노드의 입력을 자동으로 매핑

        Args:
            source_id: 소스 노드 ID
            target_id: 타겟 노드 ID
        """
        # 소스 노드와 타겟 노드 찾기
        source_node = self.get_node(source_id)
        target_node = self.get_node(target_id)

        if not source_node or not target_node:
            return

        # 소스 노드의 출력 키들
        source_outputs = []
        if hasattr(source_node.data, "output_keys") and source_node.data.output_keys:
            source_outputs = source_node.data.output_keys

        # 타겟 노드의 입력 키들
        target_inputs = []
        if hasattr(target_node.data, "input_keys") and target_node.data.input_keys:
            target_inputs = target_node.data.input_keys

        # 매핑 로직: 이름이 같은 입력/출력을 자동 연결
        for target_input in target_inputs:
            if not target_input.keytable_id:  # 아직 keytable_id가 없는 경우만
                for source_output in source_outputs:
                    if target_input.name == source_output.name:
                        # keytable_id 매핑
                        target_input.keytable_id = source_output.keytable_id
                        print(
                            f"🔗 자동 매핑: {source_id}.{source_output.name} -> {target_id}.{target_input.name} (keytable_id: {source_output.keytable_id})"
                        )
                        break

    def auto_fix_keytable_ids(self) -> Dict[str, Any]:
        """
        keytable_id를 자동으로 수정하여 연결 문제를 해결

        Returns:
            수정 결과 딕셔너리
        """
        fix_result = {"fixed_count": 0, "fixes": [], "warnings": []}

        # 1. 빈 keytable_id를 가진 입력 찾기
        for node in self.nodes:
            if hasattr(node.data, "input_keys") and node.data.input_keys:
                for input_key in node.data.input_keys:
                    if not input_key.keytable_id and input_key.name:
                        # 같은 이름의 출력을 찾아서 연결
                        matching_output = self._find_matching_output(input_key.name)
                        if matching_output:
                            input_key.keytable_id = matching_output.keytable_id
                            fix_result["fixed_count"] += 1
                            fix_result["fixes"].append(
                                {
                                    "node_id": node.id,
                                    "node_name": getattr(node.data, "name", "Unknown"),
                                    "input_name": input_key.name,
                                    "new_keytable_id": input_key.keytable_id,
                                    "source_node": matching_output["node_id"],
                                }
                            )
                        else:
                            fix_result["warnings"].append(
                                {
                                    "node_id": node.id,
                                    "node_name": getattr(node.data, "name", "Unknown"),
                                    "input_name": input_key.name,
                                    "message": f"'{input_key.name}' 이름의 출력을 찾을 수 없습니다",
                                }
                            )

        return fix_result

    def _find_matching_output(self, input_name: str) -> Optional[Dict[str, str]]:
        """입력 이름과 일치하는 출력을 찾기"""
        for node in self.nodes:
            if hasattr(node.data, "output_keys") and node.data.output_keys:
                for output_key in node.data.output_keys:
                    if output_key.name == input_name:
                        return {
                            "keytable_id": output_key.keytable_id,
                            "node_id": node.id,
                        }
        return None

    def get_auto_fix_report(self) -> str:
        """
        자동 수정 결과를 읽기 쉬운 형태로 반환

        Returns:
            자동 수정 리포트 문자열
        """
        result = self.auto_fix_keytable_ids()

        report = "=== keytable_id 자동 수정 리포트 ===\n"

        if result["fixed_count"] > 0:
            report += f"✅ {result['fixed_count']}개의 keytable_id를 수정했습니다!\n\n"

            report += "🔧 수정된 항목:\n"
            for fix in result["fixes"]:
                report += f"  - 노드: {fix['node_name']} ({fix['node_id']})\n"
                report += f"    입력: {fix['input_name']}\n"
                report += f"    새로운 keytable_id: {fix['new_keytable_id']}\n"
                report += f"    소스 노드: {fix['source_node']}\n\n"
        else:
            report += "ℹ️  수정할 keytable_id가 없습니다.\n\n"

        if result["warnings"]:
            report += "⚠️  경고:\n"
            for warning in result["warnings"]:
                report += f"  - 노드: {warning['node_name']} ({warning['node_id']})\n"
                report += f"    입력: {warning['input_name']}\n"
                report += f"    문제: {warning['message']}\n\n"

        return report

    def create_input_key(
        self,
        name: str,
        required: bool = True,
        description: str = "",
        fixed_value: Optional[str] = None,
        node_id: Optional[str] = None,
        is_global: bool = False,
        keytable_id: Optional[str] = None,
    ) -> InputKey:
        """
        사용자 친화적인 InputKey 생성 헬퍼 함수

        Args:
            name: 키 이름 (query, context, content 등)
            required: 필수 여부 (기본값: True)
            description: 설명 (기본값: "")
            fixed_value: 고정값 (기본값: None)
            from_node_id: 노드 ID (노드를 특정할 수 없으면 None 으로 설정해주세요. 그러면 global 변수로 설정됩니다.)
            from_node_output_key: 노드의 output 키 이름 (None이면 name과 동일한 키 이름을 from_node에서 )
            # is_global: Global 변수 여부 (기본값: False)
            keytable_id: 직접 지정할 keytable_id (None이면 자동 생성)

        Returns:
            생성된 InputKey 객체
        """
        if keytable_id is None:
            # keytable_id가 직접 지정되지 않은 경우 자동 생성
            if is_global:
                # Global 변수인 경우
                keytable_id = f"{name}__global"
            else:
                if node_id is None:
                    # 현재 추가 중인 노드의 ID 사용
                    if hasattr(self, "_current_node_id") and self._current_node_id:
                        node_id = self._current_node_id
                    else:
                        raise ValueError(
                            "node_id가 필요합니다. add_*_node 함수 내에서 사용하거나 node_id를 명시하세요."
                        )

                keytable_id = f"{name}__{node_id}"

        return InputKey(
            keytable_id=keytable_id,
            name=name,
            required=required,
            description=description,
            fixed_value=fixed_value,
        )

    def create_output_key(self, name: str, node_id: Optional[str] = None) -> OutputKey:
        """
        사용자 친화적인 OutputKey 생성 헬퍼 함수

        Args:
            name: 키 이름 (content, selected, reason 등)
            node_id: 노드 ID (None이면 자동 생성)

        Returns:
            생성된 OutputKey 객체
        """
        if node_id is None:
            # 현재 추가 중인 노드의 ID 사용
            if hasattr(self, "_current_node_id") and self._current_node_id:
                node_id = self._current_node_id
            else:
                raise ValueError(
                    "node_id가 필요합니다. add_*_node 함수 내에서 사용하거나 node_id를 명시하세요."
                )

        keytable_id = f"{name}__{node_id}"
        return OutputKey(keytable_id=keytable_id, name=name)

    def make_format_string(self, node: "NodeSchema") -> str:
        """
        노드의 출력 키 ID를 format_string 형태로 반환하는 헬퍼 함수

        Args:
            node: NodeSchema 객체

        Returns:
            format_string에서 사용할 수 있는 형태 (예: "{{content__node_id}}")
        """
        if not hasattr(node, "data") or not hasattr(node.data, "output_keys"):
            raise ValueError(f"노드 {node.id}에 output_keys가 없습니다.")

        if not node.data.output_keys:
            raise ValueError(f"노드 {node.id}의 output_keys가 비어있습니다.")

        # 첫 번째 output_key의 keytable_id 사용
        output_key_id = node.data.output_keys[0].keytable_id
        return f"{{{{{output_key_id}}}}}"

    def get_node_by_name(self, name: str) -> "NodeSchema":
        """
        노드 이름으로 노드를 찾는 헬퍼 함수

        Args:
            name: 찾을 노드의 이름

        Returns:
            NodeSchema 객체

        Raises:
            ValueError: 노드를 찾을 수 없는 경우
        """
        for node in self.nodes:
            if (
                hasattr(node, "data")
                and hasattr(node.data, "name")
                and node.data.name == name
            ):
                return node
        raise ValueError(f"이름이 '{name}'인 노드를 찾을 수 없습니다.")

    def get_keytable_mapping_report(self) -> str:
        """
        keytable_id 매핑 현황 리포트

        Returns:
            매핑 현황 리포트 문자열
        """
        report = "=== keytable_id 매핑 현황 ===\n"

        if not self._keytable_mapping:
            report += "매핑된 keytable_id가 없습니다.\n"
            return report

        for keytable_id, info in self._keytable_mapping.items():
            report += f"  {keytable_id}:\n"
            report += f"    노드: {info['node_id']}\n"
            report += f"    키: {info['key_name']} ({info['key_type']})\n"

        return report

    def invoke(
        self,
        inputs: InputBody | dict,
        config: dict | None = None,
        graph_id: str | None = None,
    ) -> dict:
        """
        그래프를 실행하고 답변을 받는 함수

        Args:
            graph_id: 실행할 그래프의 ID
            inputs: 대화 메시지 리스트 (예: [{"content": "안녕하세요", "type": "human"}])
            config: 실행 설정 (Optional. langchain_core.runnables import RunnableConfig 참고)

        Returns:
            실행 결과
        """
        # TODO: client와 graph_id를 parameter로 받아야하는것인지 검토 필요. builder 내에 client와 graph_id를 가지고 있는것으로 보여짐
        if graph_id is None:
            if self._saved_graph_id is None:
                raise ValueError(
                    "graph_id가 필요합니다. save() 메서드를 호출하거나 graph_id를 명시하세요."
                )
            graph_id = self._saved_graph_id

        try:
            # 그래프 실행
            response = self.client.invoke(graph_id, inputs, config)

            # 응답에서 실제 내용만 추출
            content = response.get("content", "")

            return {
                "success": True,
                "response": content,  # 실제 답변 내용만 반환
                "run_id": response.get("run_id"),
                "graph_id": graph_id,
                "data": response,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "graph_id": graph_id,
                "data": "",
            }

    def stream(
        self,
        inputs: InputBody | dict,
        config: dict | None = None,
        graph_id: str | None = None,
    ) -> dict:
        """
        그래프를 스트리밍으로 실행하고 답변을 받는 함수

        Args:
            graph_id: 실행할 그래프의 ID
            messages: 대화 메시지 리스트 또는 단일 메시지 문자열
                     - 문자열인 경우: "안녕하세요" -> [{"content": "안녕하세요", "type": "human"}]
                     - 리스트인 경우: [{"content": "안녕하세요", "type": "human"}]
            client: AgentGraphClient 객체 (선택사항, 없으면 자동 생성)

        Returns:
            스트리밍 실행 결과 딕셔너리
        """
        if graph_id is None:
            if self._saved_graph_id is None:
                raise ValueError(
                    "graph_id가 필요합니다. save() 메서드를 호출하거나 graph_id를 명시하세요."
                )
            graph_id = self._saved_graph_id

        try:
            # 그래프 스트리밍 실행
            response = self.client.stream(graph_id, inputs, config)

            # 응답에서 실제 내용만 추출
            content = response.get("content", "")

            return {
                "success": True,
                "response": content,  # 실제 답변 내용만 반환
                "run_id": response.get("run_id"),
                "graph_id": graph_id,
                "data": response,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "graph_id": graph_id,
                "data": response,
            }

    def test_graph_execution(
        self,
        graph_id: str | None = None,
        test_message: str = "안녕하세요! 테스트입니다.",
    ) -> dict:
        """
        그래프 실행을 간단히 테스트하는 함수.

        Args:
            graph_id: 실행할 그래프의 ID
            test_message: 테스트할 메시지
            client: AgentGraphClient 객체 (선택사항, 없으면 자동 생성)

        Returns:
            테스트 결과 딕셔너리
        """
        inputs = {"messages": [{"content": test_message, "type": "human"}]}

        print(f"🧪 그래프 실행 테스트 시작...")
        print(f"   그래프 ID: {graph_id}")
        print(f"   테스트 메시지: {test_message}")
        if graph_id is None:
            if self._saved_graph_id is None:
                raise ValueError(
                    "graph_id가 필요합니다. save() 메서드를 호출하거나 graph_id를 명시하세요."
                )
            graph_id = self._saved_graph_id

        result = self.invoke(inputs, graph_id=graph_id)

        if result["success"]:
            print(f"✅ 그래프 실행 성공!")
            print(f"   응답: {result['response']}")
        else:
            print(f"❌ 그래프 실행 실패: {result['error']}")

        return result
