from chonkie import Chunk
from typing import Iterable, Optional
from .formatters import FormatFn, xmlify
from .merge_adjacent_chunks import merge_adjacent_chunks


def render_chunks(
    chunks: Iterable[Chunk],
    format_fn: Optional[FormatFn] = xmlify,
    ellipsis_message: str = "[...]",
    manual_ellipsis_message: bool = False,
) -> str:
    """
    Render chunks into a single string with ellipsis separators.

    This function processes an iterable of chunks, merges adjacent chunks,
    and joins them into a single string using the ellipsis message. **Note:**
    This function does not perform sorting on the input chunks. The chunks are
    processed in the order they are provided. If sorting is needed, chunks should
    be sorted beforehand (e.g., using `sort_chunks`).

    Processing Steps
    ----------------
    1. **Filter empty chunks**: Chunks with empty text (text="") are filtered out.
    2. **Format ellipsis message**: If `manual_ellipsis_message` is False, the
       ellipsis message is automatically formatted by removing leading/trailing
       newlines and wrapping with single newlines.
    3. **Merge adjacent chunks**: Adjacent chunks are merged using
       `merge_adjacent_chunks`. Adjacent chunks appear as continuous text without
       separators.
    4. **Format chunks**: Each merged chunk is formatted using the `format_fn`
       function. By default, chunks are formatted as XML using `xmlify`. If `format_fn`
       is explicitly set to None, chunks are rendered using their text content directly
       (chunk.text).
    5. **Join with separators**: Non-adjacent chunk groups are joined using the
       ellipsis message. Adjacent chunks within a group appear without separators.

    Result
    ------
    A single string where:
    - Adjacent chunks are merged and appear as continuous text without separators.
    - Non-adjacent chunk groups are separated by the ellipsis message.
    - Empty chunks are excluded from the output.

    Parameters
    ----------
    chunks : Iterable[Chunk]
        An iterable of Chunk objects to render. **Important:** This function
        does not sort chunks. Chunks are processed in the order provided. For
        best results, chunks should be sorted by start_index beforehand (e.g.,
        using `sort_chunks`).
    format_fn : FormatFn, optional, default=xmlify
        Formatter function to use for formatting individual chunks. Must conform to
        the FormatFn protocol, which accepts a Chunk object and optional attributes
        parameter, and returns a formatted string. Available formatters include:
        - xmlify: Formats chunks as XML with attributes (default)
        - jsonify: Formats chunks as JSON with specified attributes
        - toonify: Formats chunks as TOON (Token Oriented Object Notation)
        If explicitly set to None, chunks are rendered using their text content
        directly (chunk.text) without formatting.
    ellipsis_message : str, default="[...]"
        Message to insert between non-adjacent chunk groups. The formatting behavior
        depends on the `manual_ellipsis_message` parameter.
    manual_ellipsis_message : bool, default=False
        If False (default), the message will be automatically formatted by removing
        all leading/trailing newlines and wrapping with single newlines.
        If True, the message is used exactly as provided without any modification.
        **Warning when True**: If the message lacks leading/trailing newlines, it may
        appear cramped or cause issues for LLM processing. For example:
        - Without newlines: "chunk1[...]chunk2" (hard to read, may confuse LLM)
        - With newlines: "chunk1" + newline + "[...]" + newline + "chunk2" (properly separated, LLM-friendly)

    Returns
    -------
    str
        A single string containing all chunk texts joined by the ellipsis message.
        Adjacent chunks are merged and appear as continuous text. Non-adjacent
        chunks are separated by the ellipsis message.

    Notes
    -----
    - Adjacent chunks are merged before rendering, so they appear without
      separators. See `merge_adjacent_chunks` for details on adjacency detection.
    - The ellipsis message is only inserted between non-adjacent chunk groups.
      If all chunks are adjacent, the result will be a single continuous string
      without any ellipsis messages.
    - Empty chunks list will return an empty string.
    - Chunks with empty text (text="") are automatically filtered out before
      processing. This ensures that empty chunks don't appear in the rendered
      output and don't affect the merging or separation logic.
    - When `manual_ellipsis_message` is False, the ellipsis message is automatically
      formatted: leading/trailing newlines are removed and the message is wrapped
      with single newlines. Empty strings remain unchanged.

    Examples
    --------
    **Render adjacent chunks (no separator, default XML formatting):**
    >>> from chonkie import Chunk
    >>> from chonkie_chunk_utils.render_chunks import render_chunks
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello"),
    ...     Chunk(start_index=4, end_index=10, text="o world")
    ... ]
    >>> render_chunks(chunks, ellipsis_message="[...]")
    '<chunk start_index="0" end_index="10">Hello world</chunk>'

    **Render adjacent chunks without formatting (format_fn=None):**
    >>> render_chunks(chunks, format_fn=None, ellipsis_message="[...]")
    'Hello world'

    **Render non-adjacent chunks (with separator, default XML formatting):**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello"),
    ...     Chunk(start_index=20, end_index=25, text="world")
    ... ]
    >>> result = render_chunks(chunks, ellipsis_message="[...]")
    >>> result
    '<chunk start_index="0" end_index="5">Hello</chunk>\\n[...]\\n<chunk start_index="20" end_index="25">world</chunk>'

    **Render with custom ellipsis message (default XML formatting):**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="First"),
    ...     Chunk(start_index=20, end_index=25, text="Second")
    ... ]
    >>> render_chunks(chunks, ellipsis_message="(omitted)", manual_ellipsis_message=True)
    '<chunk start_index="0" end_index="5">First</chunk>(omitted)<chunk start_index="20" end_index="25">Second</chunk>'

    **Render with custom formatter:**
    >>> from chonkie_chunk_utils.formatters import jsonify
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text="Hello", context="test")
    ... ]
    >>> render_chunks(chunks, format_fn=jsonify)
    '{"start_index": 0, "end_index": 5, "context": "test", "content": "Hello"}'

    **Render empty chunks list:**
    >>> render_chunks([])
    ''

    **Render chunks with empty text (filtered out, default XML formatting):**
    >>> chunks = [
    ...     Chunk(start_index=0, end_index=5, text=""),
    ...     Chunk(start_index=5, end_index=10, text="Hello"),
    ...     Chunk(start_index=10, end_index=15, text="")
    ... ]
    >>> render_chunks(chunks, ellipsis_message="[...]")
    '<chunk start_index="5" end_index="10">Hello</chunk>'
    """
    # Filter out chunks with empty text
    chunks = [chunk for chunk in chunks if len(chunk.text) > 0]

    # Format ellipsis message (unless manual mode)
    if not manual_ellipsis_message and ellipsis_message:
        # Remove all leading and trailing newlines
        message = ellipsis_message.strip("\n")
        # Wrap with single newlines
        formatted_ellipsis = f"\n{message}\n"
    else:
        formatted_ellipsis = ellipsis_message

    # Merge adjacent chunks
    merged_chunks = merge_adjacent_chunks(chunks)

    # Format each chunk using the format function (or use text directly if None)
    if format_fn is not None:
        rendered_chunks = [format_fn(chunk) for chunk in merged_chunks]
    else:
        rendered_chunks = [chunk.text for chunk in merged_chunks]

    # Join with ellipsis message
    return formatted_ellipsis.join(rendered_chunks)
