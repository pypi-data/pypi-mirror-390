from enum import Enum
from typing import Any, Literal, TypedDict

JSON = dict[str, Any]


class ResponseError(TypedDict):
    detail: str


class ResponseSuccess(TypedDict):
    message: Literal["ok"]


class PodBaseOptions(TypedDict, total=False):
    baseUrl: str


class Pagination(TypedDict):
    count: int
    hasNextPage: bool
    hasPreviousPage: bool


VectorDistance = Literal[
    "vector::euclidean",
    "vector::dot",
    "vector::cosine",
    "vector::manhattan",
    "halfvec::euclidean",
    "halfvec::dot",
    "halfvec::cosine",
    "halfvec::manhattan",
    "sparsevec::euclidean",
    "sparsevec::dot",
    "sparsevec::cosine",
    "sparsevec::manhattan",
    "bit::hamming",
    "bit::jaccard",
]


class SbertEmbeddingOptions(TypedDict, total=False):
    provider: Literal["sbert"]
    model: str
    dimension: int
    options: JSON


class EmbeddingModeEnum(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"


class JSONFilterOperators(TypedDict, total=False):
    """MongoDB-style filter operators (use $ prefix like $eq, $neq, etc.)"""
    pass  # This is a flexible dict that accepts $eq, $neq, etc. as string keys


JSONFilterValue = dict[str, JSONFilterOperators]


class Storage:
    class Collection:
        class Options(TypedDict, total=False):
            embedding: SbertEmbeddingOptions
            auto_index: dict[str, bool]

        class ExistResponseSuccess(ResponseSuccess):
            exists: bool

        class CountResponseSuccess(ResponseSuccess):
            counts: int

        class PurgeResponseSuccess(ResponseSuccess):
            pass

        class DeleteResponseSuccess(ResponseSuccess):
            pass


class Collection:
    class Record(TypedDict, total=False):
        id: str
        content: str
        embedding: list[float]
        payload: JSON
        metadata: JSON

    class Records:
        class InsertRecord(TypedDict, total=False):
            content: str
            payload: JSON
            mode: EmbeddingModeEnum

        class InsertResponseSuccess(ResponseSuccess):
            inserts: int

        class SearchFilter(TypedDict, total=False):
            term: str
            mode: EmbeddingModeEnum
            score: float
            distance: VectorDistance
            payload: JSONFilterValue
            metadata: JSONFilterValue
            fields: list[Literal["content", "embedding", "payload", "metadata"]]
            limit: int
            offset: int

        class SearchResponseSuccess(ResponseSuccess, Pagination):
            records: list[dict[str, Any]]

        class UnsertFilter(TypedDict, total=False):
            ids: list[str]
            payload: JSONFilterValue
            metadata: JSONFilterValue

        class UnsertResponseSuccess(ResponseSuccess):
            unserted_ids: list[str]

        class OnsertFilter(TypedDict, total=False):
            ids: list[str]
            payload: JSONFilterValue
            metadata: JSONFilterValue

        class OnsertUpdates(TypedDict, total=False):
            payload: JSON | None
            metadata: JSON | None

        class OnsertResponseSuccess(ResponseSuccess):
            onserted_ids: list[str]
