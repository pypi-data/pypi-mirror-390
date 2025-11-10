"""
Agent Graph CRUD SDK의 유틸리티 함수들
"""

import uuid
from typing import Dict, Any, List, Optional


def generate_node_id() -> str:
    """새로운 노드 ID 생성"""
    return str(uuid.uuid4())


def generate_edge_id() -> str:
    """새로운 엣지 ID 생성"""
    return str(uuid.uuid4())


def create_input_node(name: str, description: str = "") -> Dict[str, Any]:
    """
    입력 노드 생성
    
    Args:
        name: 노드 이름
        description: 노드 설명
        
    Returns:
        Dict[str, Any]: 입력 노드 데이터
    """
    node_id = generate_node_id()
    return {
        "id": node_id,
        "type": "input__basic",
        "data": {
            "name": name,
            "description": description,
            "input_keys": [],
            "output_keys": [
                {
                    "keytable_id": f"query_{node_id}",
                    "name": "query"
                }
            ],
            "fewshot_id": "",
            "prompt_id": "",
            "serving_model": "",
            "serving_name": "",
            "tool_ids": []
        }
    }


def create_agent_node(
    name: str,
    description: str = "",
    serving_model: str = "gpt-4o",
    serving_name: str = "GIP/gpt-4o",
    prompt_template: str = "",
    input_keys: Optional[List[Dict[str, Any]]] = None,
    output_keys: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    에이전트 노드 생성
    
    Args:
        name: 노드 이름
        description: 노드 설명
        serving_model: 서빙 모델
        serving_name: 서빙 이름
        prompt_template: 프롬프트 템플릿
        input_keys: 입력 키 목록
        output_keys: 출력 키 목록
        
    Returns:
        Dict[str, Any]: 에이전트 노드 데이터
    """
    node_id = generate_node_id()
    
    if input_keys is None:
        input_keys = [
            {
                "keytable_id": f"query_{node_id}",
                "name": "query",
                "required": "true"
            }
        ]
    
    if output_keys is None:
        output_keys = [
            {
                "keytable_id": f"content_{node_id}",
                "name": "content"
            }
        ]
    
    return {
        "id": node_id,
        "type": "agent__generator",
        "data": {
            "name": name,
            "description": description,
            "input_keys": input_keys,
            "output_keys": output_keys,
            "fewshot_id": "",
            "prompt_id": "",
            "serving_model": serving_model,
            "serving_name": serving_name,
            "tool_ids": [],
            "prompt_template": prompt_template
        }
    }


def create_output_node(
    name: str,
    description: str = "",
    format_string: str = "",
    input_keys: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    출력 노드 생성
    
    Args:
        name: 노드 이름
        description: 노드 설명
        format_string: 포맷 문자열
        input_keys: 입력 키 목록
        
    Returns:
        Dict[str, Any]: 출력 노드 데이터
    """
    node_id = generate_node_id()
    
    if input_keys is None:
        input_keys = [
            {
                "keytable_id": f"content_{node_id}",
                "name": "content",
                "required": "true"
            }
        ]
    
    return {
        "id": node_id,
        "type": "output__chat",
        "data": {
            "name": name,
            "description": description,
            "input_keys": input_keys,
            "output_keys": [],
            "fewshot_id": "",
            "prompt_id": "",
            "serving_model": "",
            "serving_name": "",
            "tool_ids": [],
            "format_string": format_string
        }
    }


def create_edge(source_id: str, target_id: str, edge_type: str = "none") -> Dict[str, Any]:
    """
    엣지 생성
    
    Args:
        source_id: 소스 노드 ID
        target_id: 타겟 노드 ID
        edge_type: 엣지 타입
        
    Returns:
        Dict[str, Any]: 엣지 데이터
    """
    return {
        "id": generate_edge_id(),
        "source": source_id,
        "target": target_id,
        "type": edge_type
    }


