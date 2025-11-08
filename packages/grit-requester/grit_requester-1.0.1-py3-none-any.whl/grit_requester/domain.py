from typing import List, Dict, Any, Optional
from .query import prepare_grit_query

class GritDomain:
    def __init__(self, service, path: str):
        self.api = service.session
        self.base_url = service.base_url.rstrip("/")
        self.path = path.strip("/")

    def _url(self, endpoint: str = "") -> str:
        return f"{self.base_url}/{self.path}/{endpoint}".rstrip("/")

    def detail(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.api.get(self._url(f"detail/{id}"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                return None
            raise

    def dead_detail(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.api.get(self._url(f"detail/{id}"))
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                return None
            raise

    def list(self, filters: Optional[List[Dict[str, Any]]] = None,
            order: Optional[Dict[str, str]] = None,
            cursor: Optional[str] = None) -> Dict[str, Any]:

        query = prepare_grit_query({
            "filters": filters,
            "order": order,
            "cursor": cursor
        })

        url = f"{self._url('list')}?{query}" if query else self._url('list')
        resp = self.api.get(url)
        resp.raise_for_status()

        return {
            "data": resp.json(),
            "cursor": resp.headers.get('x-page-cursor', '')
        }

    def dead_list(self, filters: Optional[List[Dict[str, Any]]] = None,
            order: Optional[Dict[str, str]] = None,
            cursor: Optional[str] = None) -> Dict[str, Any]:

        query = prepare_grit_query({
            "filters": filters,
            "order": order,
            "cursor": cursor
        })

        url = f"{self._url('dead_list')}?{query}" if query else self._url('list')
        resp = self.api.get(url)
        resp.raise_for_status()

        return {
            "data": resp.json(),
            "cursor": resp.headers.get('x-page-cursor', '')
        }

    def list_all(self, filters: Optional[List[Dict[str, Any]]] = None,
                 order: Optional[str] = None) -> List[Dict[str, Any]]:
        data = []
        cursor = None

        while True:
            result = self.list(filters=filters, order=order, cursor=cursor)
            data.extend(result["data"])

            if not result["cursor"] or cursor == result["cursor"]:
                break

            cursor = result["cursor"]

        return data

    def list_one(self, filters: Optional[List[Dict[str, Any]]] = None,
                order: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        query = prepare_grit_query({
            "filters": filters,
            "order": order
        })
        url = f"{self._url('list_one')}?{query}"
        resp = self.api.get(url)
        resp.raise_for_status()

        result = resp.json()

        if not result or not isinstance(result, dict) or not result.keys():
            return None

        return result

    def add(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.api.post(self._url("add"), json=payload)
        resp.raise_for_status()
        return resp.json()

    def bulk_add(self, payload: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        chunk_size = 25
        results = {"ids": []}

        for i in range(0, len(payload), chunk_size):
            chunk = payload[i:i + chunk_size]
            response = self.api.post(self._url("bulk_add"), json=chunk)
            response.raise_for_status()
            data = response.json()
            results["ids"].extend(data.get("ids", []))

        return results

    def edit(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.api.patch(self._url(f"edit/{id}"), json=data)
        resp.raise_for_status()
        return resp.json()

    def delete(self, id: str):
        resp = self.api.delete(self._url(f"delete/{id}"))
        resp.raise_for_status()

    def bulk(self, ids: List[str]) -> List[Dict[str, Any]]:
        resp = self.api.post(self._url("bulk"), json={"ids": ids})
        resp.raise_for_status()
        return resp.json()

    def bulk_all(self, ids: List[str]) -> List[Dict[str, Any]]:
        results = []
        size = 25

        for i in range(0, len(ids), size):
            chunk = ids[i:i + size]
            res = self.bulk(chunk)
            results.extend(res)

        return results

    def select_raw(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.api.post(self._url("select_raw"), json={ "query": query, "params": params })
        resp.raise_for_status()
        return resp.json()