import uuid
from typing import Dict


def is_valid_uuid(val: str) -> bool:
    """
    Check if the given string is a valid UUID.
    """
    try:
        uuid_obj = uuid.UUID(val)
        return str(uuid_obj) == val
    except (ValueError, AttributeError, TypeError):
        return False


def format_resource_status(resource: Dict) -> str:
    """
    Format cluster resource info into human-readable string.
    
    Args:
        resource (dict): cluster_resource section from API response
    
    Returns:
        str: formatted string
    """
    if not resource:
        return "No resource information available."

    cpu_total = resource.get("cpu_total", 0)
    cpu_used = resource.get("cpu_used", 0)
    cpu_usable = resource.get("cpu_usable", 0)

    mem_total = resource.get("memory_total", 0)
    mem_used = resource.get("memory_used", 0)
    mem_usable = resource.get("memory_usable", 0)

    gpu_total = resource.get("gpu_total", 0)
    gpu_used = resource.get("gpu_used", 0)
    gpu_usable = resource.get("gpu_usable", 0)

    return (
        f"🖥️ Cluster Resource:\n"
        f"CPU: {cpu_used}/{cpu_total} (Usable: {cpu_usable})\n"
        f"Memory: {mem_used}/{mem_total} (Usable: {mem_usable})\n"
        f"GPU: {gpu_used}/{gpu_total} (Usable: {gpu_usable})"
    )
