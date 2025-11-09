from __future__ import annotations

import os
import re
import uuid
from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from ragu.common.batch_generator import BatchGenerator
from ragu.common.logger import logger
from ragu.embedder.base_embedder import BaseEmbedder
from ragu.storage.base_storage import BaseVectorStorage


def _sanitize_collection_name(candidates: Iterable[str], fallback: str = "ragu_collection") -> str:
    """
    Build a Qdrant-compatible collection name from possible candidates.

    Qdrant allows alphanumeric characters, dashes and underscores. Any other
    characters are replaced with underscores. The first valid candidate wins.
    """
    pattern = re.compile(r"[^0-9a-zA-Z_-]+")

    for candidate in candidates:
        if not candidate:
            continue

        name = os.path.splitext(os.path.basename(candidate))[0]
        name = pattern.sub("_", name).strip("_").lower()
        if name:
            return name

    return fallback


def _normalize_point_id(doc_id: Any) -> Union[int, str]:
    """Cast ``doc_id`` to a Qdrant-compatible point identifier.

    Qdrant only accepts unsigned integers or UUID strings. We preserve integers
    when possible, pass through valid UUIDs, and deterministically derive UUIDs
    for arbitrary identifiers.
    """

    if isinstance(doc_id, (int, np.integer)):
        if doc_id < 0:
            raise ValueError(f"Qdrant point ID must be non-negative, got {doc_id}.")
        return int(doc_id)

    doc_str = str(doc_id).strip()
    if not doc_str:
        raise ValueError("Qdrant point ID cannot be an empty string.")

    # Keep numeric strings as integers to avoid unnecessary UUID allocations.
    if doc_str.isdigit():
        return int(doc_str)

    try:
        parsed = uuid.UUID(doc_str)
        return str(parsed)
    except (ValueError, TypeError):
        return doc_str.split("-")[1]


class QdrantVectorStorage(BaseVectorStorage):
    """
    Qdrant implementation for :class:`BaseVectorStorage`.

    Stores vectors in a Qdrant collection and supports similarity search using
    cosine distance by default.
    """

    def __init__(
        self,
        embedder: BaseEmbedder,
        *,
        collection_name: Optional[str] = None,
        filename: Optional[str] = None,
        host: Optional[str] = "localhost",
        port: Optional[int] = 6333,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
        https: Optional[bool] = None,
        vector_size: Optional[int] = None,
        distance: Distance = Distance.COSINE,
        batch_size: int = 64,
        score_threshold: Optional[float] = None,
        recreate_collection: bool = False,
        **client_kwargs: Any,
    ) -> None:
        """
        Initialize a Qdrant-backed vector storage.

        :param embedder: Embedder used to compute vector representations.
        :param collection_name: Name of the Qdrant collection (auto-inferred if omitted).
        :param filename: Optional filename used to infer collection name when ``collection_name`` is not provided.
        :param host: Qdrant host (ignored when ``url`` is provided).
        :param port: Qdrant port (ignored when ``url`` is provided).
        :param url: Full Qdrant endpoint URL.
        :param api_key: API key for Qdrant Cloud deployments.
        :param prefer_grpc: Whether to use gRPC protocol if available.
        :param https: Force HTTPS when using host/port constructor.
        :param vector_size: Dimensionality of stored vectors (defaults to embedder.dim).
        :param distance: Distance metric to use (defaults to cosine).
        :param batch_size: Number of texts to embed per batch during upsert.
        :param score_threshold: Optional minimum score required when querying.
        :param recreate_collection: Whether to recreate the collection on init.
        :param client_kwargs: Additional keyword arguments forwarded to QdrantClient.
        """
        super().__init__()

        if vector_size is None:
            vector_size = getattr(embedder, "dim", None)
        if vector_size is None:
            raise ValueError("`vector_size` must be provided when the embedder does not expose `dim`.")

        resolved_collection_name = collection_name or _sanitize_collection_name(
            candidates=[collection_name or "", filename or ""],
            fallback="ragu_collection",
        )

        self.embedder = embedder
        self.collection_name = resolved_collection_name
        self.batch_size = batch_size
        self.distance = distance
        self.vector_size = vector_size
        self.score_threshold = score_threshold

        client_args: Dict[str, Any] = dict(
            api_key=api_key,
            prefer_grpc=prefer_grpc,
            **client_kwargs,
        )

        if url:
            client_args["url"] = url
        else:
            client_args["host"] = host
            client_args["port"] = port
            if https is not None:
                client_args["https"] = https

        self._client = QdrantClient(**client_args)
        self._ensure_collection(recreate_collection=recreate_collection)

    def _ensure_collection(self, *, recreate_collection: bool) -> None:
        """
        Make sure the target collection exists and has the expected vector params.
        """
        if recreate_collection:
            logger.info(f"Recreating Qdrant collection `{self.collection_name}`")
            self._client.recreate_collection(
                self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=self.distance),
            )
            return

        if self._client.collection_exists(self.collection_name):
            return

        logger.info(f"Creating Qdrant collection `{self.collection_name}`")
        self._client.create_collection(
            self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=self.distance),
        )

    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Insert or update points in Qdrant.

        :param data: Mapping of IDs to payload dictionaries (must include ``content`` for embedding).
        :return: List of upserted IDs.
        """
        if not data:
            logger.warning("Attempted to insert empty data into Qdrant vector DB.")
            return []

        items = list(data.items())
        contents = [str(value.get("content", "")) for _, value in items]

        batch_generator = BatchGenerator(contents, batch_size=self.batch_size)
        embeddings: List[List[float]] = []

        for batch in batch_generator.get_batches():
            batch_embeddings = await self.embedder(batch)
            if batch_embeddings is None:
                raise ValueError("Embedder returned None while processing batch.")

            for vector in batch_embeddings:
                if vector is None:
                    embeddings.append([0.0] * self.vector_size)
                    continue
                if isinstance(vector, np.ndarray):
                    embeddings.append(vector.astype(float).tolist())
                else:
                    embeddings.append([float(component) for component in vector])

        if len(embeddings) != len(items):
            raise ValueError("Number of embeddings does not match number of data items.")

        points: List[PointStruct] = []
        for (doc_id, payload), vector in zip(items, embeddings, strict=True):
            point_id = _normalize_point_id(doc_id)
            payload_dict: Dict[str, Any] = dict(payload or {})
            payload_dict.setdefault("__original_id__", str(doc_id))
            points.append(PointStruct(id=point_id, vector=vector, payload=payload_dict))

        self._client.upsert(collection_name=self.collection_name, points=points)
        return [str(doc_id) for doc_id, _ in items]

    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for the most similar points stored in Qdrant.

        :param query: Natural language query to embed.
        :param top_k: Maximum number of results to return.
        :return: List of dictionaries compatible with downstream consumers.
        """
        if not query:
            return []

        query_vectors = await self.embedder(query)
        if not query_vectors:
            return []

        search_kwargs: Dict[str, Any] = {
            "collection_name": self.collection_name,
            "query_vector": query_vectors[0],
            "limit": top_k,
        }
        if self.score_threshold is not None:
            search_kwargs["score_threshold"] = self.score_threshold

        results = self._client.search(**search_kwargs)

        formatted: List[Dict[str, Any]] = []
        for point in results:
            payload = dict(point.payload or {})
            original_id = payload.pop("__original_id__", str(point.id))
            formatted.append(
                {
                    "__id__": str(original_id),
                    "__score__": point.score,
                    "__payload__": payload,
                    "id": str(original_id),
                    "score": point.score,
                    "payload": payload,
                }
            )

        return formatted

    async def index_start_callback(self):
        pass

    async def index_done_callback(self):
        pass

    async def query_done_callback(self):
        pass
