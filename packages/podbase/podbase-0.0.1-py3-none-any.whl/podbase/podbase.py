from types import SimpleNamespace
from typing import Any, Callable

import httpx

from .types import (
    Collection,
    PodBaseOptions,
    ResponseSuccess,
    Storage,
)


class PodBase:
    def __init__(self, options: PodBaseOptions | None = None):
        options = options or {}
        self._base_url = options.get("baseUrl", "http://localhost:8080")

        self.exist = SimpleNamespace(collection=self._exist_collection)
        self.purge = SimpleNamespace(collection=self._purge_collection)
        self.delete = SimpleNamespace(collection=self._delete_collection)
        self.create = SimpleNamespace(collection=self._create_collection)
        self.select = SimpleNamespace(collection=self._select_collection)

    async def _request(self, method: str, path: str, data: Any = None) -> Any:
        try:
            url = f"{self._base_url}/api/v0{path}"
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                )

                if not response.is_success:
                    raise Exception(f"HTTP error! status: {response.status_code}")

                return response.json()
        except Exception as error:
            raise Exception(f"Unexpected error: {str(error)}")

    async def health(self) -> ResponseSuccess:
        return await self._request("GET", "/health")

    async def _exist_collection(
        self, name: str
    ) -> Storage.Collection.ExistResponseSuccess:
        return await self._request("GET", f"/storage/exist/collection/{name}")

    async def _purge_collection(
        self, name: str
    ) -> Storage.Collection.PurgeResponseSuccess:
        return await self._request("DELETE", f"/storage/purge/collection/{name}")

    async def _delete_collection(
        self, name: str
    ) -> Storage.Collection.DeleteResponseSuccess:
        return await self._request("DELETE", f"/storage/delete/collection/{name}")

    async def _create_collection(
        self, name: str, options: Storage.Collection.Options | None = None
    ) -> "PodCollection":
        await self._request(
            "POST", "/storage/create/collection", {"name": name, "options": options}
        )
        return PodCollection(self._request, name, options or {})

    def _select_collection(
        self, name: str, options: Storage.Collection.Options | None = None
    ) -> "PodCollection":
        return PodCollection(self._request, name, options or {})


class PodCollection:
    def __init__(
        self,
        request: Callable[[str, str, Any], Any],
        name: str,
        options: Storage.Collection.Options,
    ):
        self._request = request
        self.name = name
        self.options = options

        self.records = SimpleNamespace(
            insert=self._insert_records,
            search=self._search_records,
            onsert=self._onsert_records,
            unsert=self._unsert_records,
        )

    async def _insert_records(
        self, records: list[Collection.Records.InsertRecord]
    ) -> Collection.Records.InsertResponseSuccess:
        return await self._request(
            "POST",
            "/collection/records/insert",
            {"collection_name": self.name, "records": records},
        )

    async def _onsert_records(
        self,
        filter: Collection.Records.OnsertFilter,
        updates: Collection.Records.OnsertUpdates,
    ) -> Collection.Records.OnsertResponseSuccess:
        return await self._request(
            "PATCH",
            "/collection/records/onsert",
            {"collection_name": self.name, "filter": filter, "updates": updates},
        )

    async def _unsert_records(
        self, filter: Collection.Records.UnsertFilter
    ) -> Collection.Records.UnsertResponseSuccess:
        return await self._request(
            "DELETE",
            "/collection/records/unsert",
            {"collection_name": self.name, "filter": filter},
        )

    async def _search_records(
        self, filter: Collection.Records.SearchFilter
    ) -> Collection.Records.SearchResponseSuccess:
        return await self._request(
            "POST",
            "/collection/records/search",
            {
                "collection_name": self.name,
                "embedding": self.options.get("embedding"),
                "filter": filter,
            },
        )
