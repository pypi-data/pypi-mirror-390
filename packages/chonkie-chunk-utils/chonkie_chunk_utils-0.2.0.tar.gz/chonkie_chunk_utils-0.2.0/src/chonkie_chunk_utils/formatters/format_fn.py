from typing import Protocol, Iterable
from chonkie import Chunk


class FormatFn(Protocol):
    """Protocol for formatter functions that convert Chunk objects to formatted strings.

    This protocol defines the common interface for formatter functions like
    xmlify, jsonify, and toonify. All formatters accept a Chunk object and
    optional attributes parameter, and return a formatted string.

    Parameters
    ----------
    chunk : Chunk
        The Chunk object to format.
    attributes : Iterable[str], optional
        Iterable of attribute names to include in the formatted output.
        Defaults to ["start_index", "end_index", "context"].
    **kwargs
        Additional keyword arguments specific to each formatter.
        For jsonify and toonify: wrap_xml (bool) - whether to wrap output in XML tags.
        For xmlify: no additional kwargs.

    Returns
    -------
    str
        Formatted string representation of the chunk.

    Examples
    --------
    >>> from chonkie_chunk_utils.formatters import FormatFn, xmlify, jsonify, toonify
    >>> from chonkie import Chunk
    >>> chunk = Chunk(text="Hello", start_index=0, end_index=5)
    >>>
    >>> # All formatters conform to FormatFn protocol
    >>> formatters: list[FormatFn] = [xmlify, jsonify, toonify]
    >>> for formatter in formatters:
    ...     result = formatter(chunk)
    ...     print(result)
    """

    def __call__(self, chunk: Chunk, attributes: Iterable[str] = ..., **kwargs) -> str:
        """Format a Chunk object into a string representation."""
        ...
