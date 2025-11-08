from typing import Optional, List, Dict, Any

def prepare_grit_filter(filters: Optional[List[Dict[str, Any]]]) -> List[str]:
    if not filters:
        return []
    return [
        f"filter={f['field']}:{f.get('type', 'eql')}:{f['value']}"
        for f in filters
    ]

def prepare_grit_order(order: Optional[Dict[str, str]]) -> List[str]:
    if not order:
        return []
    return [
        f"order_by={order['field']}",
        f"order={order['type']}"
    ]

def prepare_grit_query(payload: Optional[Dict[str, Any]]) -> str:
    if not payload:
        return ""

    query: List[str] = []

    query.extend(prepare_grit_filter(payload.get("filters")))
    query.extend(prepare_grit_order(payload.get("order")))

    cursor = payload.get("cursor")
    if cursor:
        query.append(f"page_cursor={cursor}")

    return "&".join(query)
