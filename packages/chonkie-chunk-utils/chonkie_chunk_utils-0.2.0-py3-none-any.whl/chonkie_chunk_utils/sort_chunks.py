from chonkie import Chunk
from typing import Iterable


def sort_chunks(chunks: Iterable[Chunk]) -> list[Chunk]:
    chunks = list(chunks)
    sorted_chunks = sorted(chunks, key=lambda x: x.start_index)
    return sorted_chunks
