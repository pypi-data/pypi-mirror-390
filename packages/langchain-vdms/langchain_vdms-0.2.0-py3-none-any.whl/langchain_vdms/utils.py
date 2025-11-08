"""Various Utility Functions

Functions "maximal_marginal_relevance" and "cosine_similarity"
are duplicated in this utility respectively from LangChain modules:

    - "libs/community/langchain_community/vectorstores/utils.py"
    - "libs/community/langchain_community/utils/math.py"
"""

import base64
from typing import (
    Any,
    List,
    Sized,
    Union,
)

import numpy as np
from langchain_core.documents import Document

Matrix = Union[List[List[float]], List[np.ndarray], np.ndarray]


def maximal_marginal_relevance(
    query_embedding: np.ndarray,
    embedding_list: list,
    lambda_mult: float = 0.5,
    k: int = 4,
) -> List[int]:
    """Calculate maximal marginal relevance."""
    if min(k, len(embedding_list)) <= 0:
        return []
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    similarity_to_query = cosine_similarity(query_embedding, embedding_list)[0]
    most_similar = int(np.argmax(similarity_to_query))
    idxs = [most_similar]
    selected = np.array([embedding_list[most_similar]])
    while len(idxs) < min(k, len(embedding_list)):
        best_score = -np.inf
        idx_to_add = -1
        similarity_to_selected = cosine_similarity(embedding_list, selected)
        for i, query_score in enumerate(similarity_to_query):
            if i in idxs:
                continue
            redundant_score = max(similarity_to_selected[i])
            equation_score = (
                lambda_mult * query_score - (1 - lambda_mult) * redundant_score
            )
            if equation_score > best_score:
                best_score = equation_score
                idx_to_add = i
        idxs.append(idx_to_add)
        selected = np.append(selected, [embedding_list[idx_to_add]], axis=0)
    return idxs


def cosine_similarity(X: Matrix, Y: Matrix) -> np.ndarray:
    """Row-wise cosine similarity between two equal-width matrices."""
    if len(X) == 0 or len(Y) == 0:
        return np.array([])

    X = np.array(X)
    Y = np.array(Y)
    if X.shape[1] != Y.shape[1]:
        raise ValueError(
            f"Number of columns in X and Y must be the same. X has shape {X.shape} "
            f"and Y has shape {Y.shape}."
        )
    try:
        import simsimd as simd

        X = np.array(X, dtype=np.float32)
        Y = np.array(Y, dtype=np.float32)
        Z = 1 - np.array(simd.cdist(X, Y, metric="cosine"))
        return Z
    except ImportError:
        X_norm = np.linalg.norm(X, axis=1)
        Y_norm = np.linalg.norm(Y, axis=1)
        # Ignore divide by zero errors run time warnings as those are handled below.
        with np.errstate(divide="ignore", invalid="ignore"):
            similarity = np.dot(X, Y.T) / np.outer(X_norm, Y_norm)
        similarity[np.isnan(similarity) | np.isinf(similarity)] = 0.0
        return similarity


def check_if_same_size(x: Any, y: Any, x_name: str, y_name: str) -> None:
    """
    Check that sizes of two variables are the same

    Args:
        x: Variable to compare
        y: Variable to compare
        x_name: Name for variable x
        y_name: Name for variable y
    """
    if isinstance(x, Sized) and isinstance(y, Sized) and len(x) != len(y):
        raise ValueError(
            f"{x_name} and {y_name} expected to be equal length but "
            f"len({x_name})={len(x)} and len({y_name})={len(y)}"
        )
    return


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        blob = f.read()
        return base64.b64encode(blob).decode("utf-8")


def decode_image(base64_image: str) -> bytes:
    return base64.b64decode(base64_image)


def reorder_mmr_documents(
    documents: Union[list[Document], list[tuple[Document, float]]],
    mmr_selected: list[int],
) -> list[Any]:
    # Reorder the values and return.
    reordered_docs = []
    for idx in mmr_selected:
        # Function can return -1 index
        if idx == -1:
            break
        else:
            reordered_docs.append(documents[idx])
    return reordered_docs
