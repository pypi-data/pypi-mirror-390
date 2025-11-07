import pytest
from functools import partial
from chonkie import Chunk
from chonkie_chunk_utils.render_chunks import render_chunks
from chonkie_chunk_utils.formatters import xmlify, jsonify, toonify
from loguru import logger


# ============================================================================
# Visualization helpers for tests
# ============================================================================


def visualize_chunks(chunks, title="Chunks"):
    """Visualize chunks in a timeline format for better understanding.

    Creates an ASCII art visualization showing:
    - Index timeline with key positions
    - Chunk positions and overlaps
    - Chunk text content with indices

    Example output:
    Index:  0    5    10   15   20   25
    Chunk1: [Hello] (0-5)
    Chunk2:     [o world] (4-10)
    Merged: [Hello world] (0-10)
    """
    if not chunks:
        return f"{title}: (empty)"

    # Find the range
    min_idx = min(chunk.start_index for chunk in chunks)
    max_idx = max(chunk.end_index for chunk in chunks)

    # Determine step size for index line (show key positions)
    range_size = max_idx - min_idx
    if range_size <= 10:
        step = 1
    elif range_size <= 50:
        step = 5
    else:
        step = max(5, range_size // 10)

    # Create index line showing key positions
    index_line = "Index:  "
    positions = []
    for i in range(min_idx, max_idx + 1, step):
        positions.append(i)
    if max_idx not in positions:
        positions.append(max_idx)

    for pos in positions:
        index_line += f"{pos:<5}"

    # Create chunk visualization lines
    lines = [f"\n{title}:", index_line]

    for i, chunk in enumerate(chunks):
        chunk_line = f"Chunk{i + 1}: "
        # Calculate relative position (simplified - show approximate position)
        if range_size > 0:
            rel_pos = int(
                (chunk.start_index - min_idx) / range_size * (len(positions) - 1) * 5
            )
        else:
            rel_pos = 0
        chunk_line += " " * max(0, rel_pos)

        # Add chunk box with text and indices
        chunk_text = chunk.text[:15] + "..." if len(chunk.text) > 15 else chunk.text
        chunk_line += f"[{chunk_text}] ({chunk.start_index}-{chunk.end_index})"
        lines.append(chunk_line)

    return "\n".join(lines)


def visualize_processing_pipeline(
    chunks, result, format_fn=None, ellipsis_message="[...]"
):
    """Visualize the complete processing pipeline.

    Shows:
    1. Input chunks
    2. After filtering (empty chunks removed)
    3. After merging (adjacent chunks merged)
    4. Final result
    """
    from chonkie_chunk_utils.merge_adjacent_chunks import merge_adjacent_chunks

    # Step 1: Input
    input_viz = visualize_chunks(chunks, "Input Chunks")

    # Step 2: Filtered
    filtered_chunks = [chunk for chunk in chunks if len(chunk.text) > 0]
    filtered_viz = visualize_chunks(filtered_chunks, "After Filtering (empty removed)")

    # Step 3: Merged
    merged_chunks = merge_adjacent_chunks(filtered_chunks)
    merged_viz = visualize_chunks(merged_chunks, "After Merging (adjacent merged)")

    # Step 4: Result
    result_viz = f"\nFinal Result:\n  '{result}'"

    return "\n".join([input_viz, filtered_viz, merged_viz, result_viz])


def visualize_chunk_groups(chunks, ellipsis_message="[...]"):
    """Visualize how chunks are grouped (adjacent vs non-adjacent).

    Shows which chunks will be merged together and which will be separated.
    """
    from chonkie_chunk_utils.utils.is_adjacent_chunks import is_adjacent_chunks

    if not chunks:
        return "Groups: (empty)"

    groups = []
    current_group = [chunks[0]]

    for i in range(len(chunks) - 1):
        if is_adjacent_chunks(chunks[i], chunks[i + 1]):
            current_group.append(chunks[i + 1])
        else:
            groups.append(current_group)
            current_group = [chunks[i + 1]]

    if current_group:
        groups.append(current_group)

    lines = ["\nChunk Groups:"]
    for i, group in enumerate(groups):
        group_texts = [f"[{chunk.text}]" for chunk in group]
        if len(group) > 1:
            lines.append(f"  Group {i + 1}: {' + '.join(group_texts)} → merged")
        else:
            lines.append(f"  Group {i + 1}: {group_texts[0]} (standalone)")

    if len(groups) > 1:
        lines.append(
            f"\n  Separators: {len(groups) - 1} ellipsis message(s) will be inserted"
        )

    return "\n".join(lines)


# ============================================================================
# Test data and formatter configurations
# ============================================================================

# Test data sets for parametrized tests
TEST_DATA_SETS = {
    "single_chunk": {
        "chunks": [Chunk(start_index=0, end_index=5, text="Hello", context="test")],
        "description": "Single chunk",
    },
    "adjacent_overlapping": {
        "chunks": [
            Chunk(start_index=0, end_index=5, text="Hello", context="test"),
            Chunk(start_index=4, end_index=10, text="o world", context="test"),
        ],
        "description": "Adjacent overlapping chunks",
    },
    "non_adjacent_with_gap": {
        "chunks": [
            Chunk(start_index=0, end_index=5, text="Hello", context="test"),
            Chunk(start_index=20, end_index=25, text="world", context="test"),
        ],
        "description": "Non-adjacent chunks with gap",
    },
    "multiple_groups": {
        "chunks": [
            Chunk(start_index=0, end_index=5, text="First", context="test"),
            Chunk(start_index=4, end_index=10, text="t group", context="test"),
            Chunk(start_index=20, end_index=25, text="Second", context="test"),
            Chunk(start_index=24, end_index=30, text="nd group", context="test"),
        ],
        "description": "Multiple groups of adjacent chunks",
    },
    "all_adjacent": {
        "chunks": [
            Chunk(start_index=0, end_index=5, text="The", context="test"),
            Chunk(start_index=4, end_index=10, text=" quick", context="test"),
            Chunk(start_index=9, end_index=15, text=" brown", context="test"),
        ],
        "description": "All adjacent chunks",
    },
}

# Formatter functions to test
FORMATTERS = [
    (None, "None (plain text)"),
    (xmlify, "xmlify (XML)"),
    (jsonify, "jsonify (JSON)"),
    (partial(jsonify, wrap_xml=True), "jsonify (JSON, wrap_xml=True)"),
    (toonify, "toonify (TOON)"),
    (partial(toonify, wrap_xml=True), "toonify (TOON, wrap_xml=True)"),
]


# ============================================================================
# Tests for render_chunks
# ============================================================================


def test_render_chunks_empty():
    """Verify edge case handling: correctly handles empty chunks list.

    When an empty list of chunks is provided, render_chunks should return an empty string.
    This ensures the function gracefully handles the minimal edge case without errors.
    """
    chunks = []
    expected = ""

    logger.info(f"[TEST] {test_render_chunks_empty.__name__}")
    logger.debug("  Input: empty chunks list")
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(chunks)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Result length: {len(result)}")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled empty chunks list")


def test_render_chunks_single():
    """Verify single chunk rendering: correctly renders a single chunk without separators.

    When only one chunk is provided, render_chunks should return the chunk's text directly
    without any ellipsis separators. This ensures single chunks are handled correctly.
    """
    chunks = [Chunk(start_index=0, end_index=5, text="Hello")]
    expected = "Hello"

    logger.info(f"[TEST] {test_render_chunks_single.__name__}")
    logger.debug(visualize_chunks(chunks, "Input"))
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly rendered single chunk")


def test_render_chunks_adjacent_no_separator():
    """Verify adjacent chunk merging: adjacent chunks are merged without separator.

    When chunks are adjacent (overlapping or meeting at boundary), render_chunks should
    merge them into continuous text without inserting ellipsis separators. This ensures
    that continuous content is properly reconstructed.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=4, end_index=10, text="o world"),
    ]
    ellipsis_message = "\n[...]\n"
    expected = "Hello world"

    logger.info(f"[TEST] {test_render_chunks_adjacent_no_separator.__name__}")
    logger.debug(visualize_processing_pipeline(chunks, expected, format_fn=None))
    logger.debug(visualize_chunk_groups(chunks))

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Separator present: {ellipsis_message in result}")

    assert result == expected
    assert ellipsis_message not in result
    logger.success(
        "  ✓ Test passed: Correctly merged adjacent chunks without separator"
    )


def test_render_chunks_non_adjacent_with_separator():
    """Verify gap handling: non-adjacent chunks are separated with ellipsis message.

    When chunks have gaps between them (not adjacent), render_chunks should insert
    the configured ellipsis_message between them. This clearly indicates missing
    content between chunks, which is crucial for LLM understanding.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=20, end_index=25, text="world"),
    ]
    ellipsis_message = "\n[...]\n"
    expected = f"Hello{ellipsis_message}world"

    logger.info(f"[TEST] {test_render_chunks_non_adjacent_with_separator.__name__}")
    logger.debug(
        visualize_processing_pipeline(
            chunks, expected, format_fn=None, ellipsis_message=ellipsis_message
        )
    )
    logger.debug(visualize_chunk_groups(chunks))
    logger.debug(
        f"  Gap between chunks: {chunks[1].start_index - chunks[0].end_index - 1} characters"
    )

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Separator present: {ellipsis_message in result}")

    assert result == expected
    assert ellipsis_message in result
    logger.success(
        "  ✓ Test passed: Correctly separated non-adjacent chunks with separator"
    )


def test_render_chunks_custom_ellipsis_message():
    """Verify customization: allows using custom ellipsis message for gaps.

    When a custom ellipsis_message is provided, render_chunks should
    use it to separate non-adjacent chunks. This allows users to customize how gaps
    are represented in the rendered output.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=20, end_index=25, text="Second"),
    ]
    custom_message = "(omitted)"
    expected = f"First{custom_message}Second"

    logger.info(f"[TEST] {test_render_chunks_custom_ellipsis_message.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug(f"  Custom ellipsis_message: '{custom_message}'")
    logger.debug("  manual_ellipsis_message: True")
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(
        chunks,
        format_fn=None,
        ellipsis_message=custom_message,
        manual_ellipsis_message=True,
    )

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly used custom ellipsis message")


def test_render_chunks_multiple_groups():
    """Verify group handling: correctly handles multiple groups of adjacent chunks.

    When chunks form multiple groups (each group contains adjacent chunks, but groups
    are separated by gaps), render_chunks should merge chunks within each group and
    insert separators between groups. This ensures proper handling of complex chunk
    arrangements.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=4, end_index=10, text="t group"),
        Chunk(start_index=20, end_index=25, text="Second"),
        Chunk(start_index=24, end_index=30, text="nd group"),
    ]
    ellipsis_message = "\n[...]\n"
    expected = f"First group{ellipsis_message}Second group"

    logger.info(f"[TEST] {test_render_chunks_multiple_groups.__name__}")
    logger.debug(
        visualize_processing_pipeline(
            chunks, expected, format_fn=None, ellipsis_message=ellipsis_message
        )
    )
    logger.debug(visualize_chunk_groups(chunks))

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Number of separators: {result.count(ellipsis_message)}")

    assert result == expected
    assert result.count(ellipsis_message) == 1
    logger.success("  ✓ Test passed: Correctly rendered multiple groups with separator")


def test_render_chunks_all_adjacent():
    """Verify complete merging: all adjacent chunks are merged into single text.

    When all chunks in the list are adjacent to each other, render_chunks should merge
    them all into a single continuous text without any separators. This ensures optimal
    text reconstruction when content is fully continuous.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="The"),
        Chunk(start_index=4, end_index=10, text=" quick"),
        Chunk(start_index=9, end_index=15, text=" brown"),
    ]
    ellipsis_message = "\n[...]\n"
    expected = "The quick brown"

    logger.info(f"[TEST] {test_render_chunks_all_adjacent.__name__}")
    logger.debug(visualize_processing_pipeline(chunks, expected, format_fn=None))
    logger.debug(visualize_chunk_groups(chunks))

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Separator present: {ellipsis_message in result}")

    assert result == expected
    assert ellipsis_message not in result
    logger.success(
        "  ✓ Test passed: Correctly merged all adjacent chunks without separator"
    )


def test_render_chunks_empty_ellipsis_message():
    """Verify empty separator handling: empty ellipsis message produces no separator.

    When ellipsis_message is set to empty string, render_chunks should concatenate
    non-adjacent chunks directly without any separator. This allows users to control
    whether gaps should be explicitly marked or silently concatenated.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=20, end_index=25, text="Second"),
    ]
    expected = "FirstSecond"

    logger.info(f"[TEST] {test_render_chunks_empty_ellipsis_message.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug("  ellipsis_message: '' (empty)")
    logger.debug("  manual_ellipsis_message: True")
    logger.debug(f"  Expected result: '{expected}' (no separator)")

    result = render_chunks(
        chunks, format_fn=None, ellipsis_message="", manual_ellipsis_message=True
    )

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled empty ellipsis message")


def test_render_chunks_automatic_formatting():
    """Verify automatic formatting: ellipsis message is automatically formatted with newlines.

    When manual_ellipsis_message is False (default), the ellipsis_message is automatically
    formatted by wrapping it with newlines. This ensures proper spacing
    and readability in the rendered output for LLM consumption.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=20, end_index=25, text="Second"),
    ]
    # Automatic formatting wraps with newlines: "\n[...]\n"
    ellipsis_message = "\n[...]\n"
    expected = f"First{ellipsis_message}Second"

    logger.info(f"[TEST] {test_render_chunks_automatic_formatting.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug(
        f"  ellipsis_message='[...]' (will be auto-formatted to '{ellipsis_message}')"
    )
    logger.debug("  manual_ellipsis_message=False (default)")
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(chunks, format_fn=None, ellipsis_message="[...]")

    logger.debug(f"  Actual result: '{result}'")
    newline = "\n"
    logger.debug(
        f"  Separator starts with newline: {result.startswith('First' + newline)}"
    )
    logger.debug(
        f"  Separator ends with newline: {result.endswith(newline + 'Second')}"
    )

    assert result == expected
    assert newline in result
    logger.success("  ✓ Test passed: Correctly used auto-formatted ellipsis message")


def test_render_chunks_manual_formatting():
    """Verify manual formatting: ellipsis message is used exactly as provided.

    When manual_ellipsis_message is True, the ellipsis_message is preserved
    exactly as provided without any automatic formatting. This gives users full control
    over the separator format, including newlines and spacing.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=20, end_index=25, text="Second"),
    ]
    custom_message = "\n\n[...]\n\n"
    expected = f"First{custom_message}Second"

    logger.info(f"[TEST] {test_render_chunks_manual_formatting.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug(f"  ellipsis_message='{custom_message}' (manual)")
    logger.debug("  manual_ellipsis_message=True")
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(
        chunks,
        format_fn=None,
        ellipsis_message=custom_message,
        manual_ellipsis_message=True,
    )

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Custom message preserved: {custom_message in result}")

    assert result == expected
    assert custom_message in result
    logger.success(
        "  ✓ Test passed: Correctly preserved manual ellipsis message formatting"
    )


def test_render_chunks_unicode():
    """Verify Unicode support: correctly handles Unicode characters in chunk text.

    When chunks contain Unicode characters (e.g., Korean, Chinese, emoji), render_chunks
    should correctly merge and render them. This ensures the function works with
    international text and preserves Unicode content accurately.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="안녕하세요"),
        Chunk(start_index=3, end_index=8, text="하세요 세계"),
    ]
    expected = "안녕하세요 세계"

    logger.info(f"[TEST] {test_render_chunks_unicode.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly rendered unicode chunks")


def test_render_chunks_empty_text():
    """Verify empty text handling: correctly filters out chunks with empty text content.

    When chunks have empty text fields (text=""), render_chunks should automatically
    filter them out before processing. This ensures that empty chunks don't appear in
    the rendered output and don't affect the merging or separation logic. Empty chunks
    are filtered out regardless of their position (beginning, middle, or end).

    This test verifies that:
    - Empty chunks at the beginning are filtered out
    - Empty chunks in the middle are filtered out
    - Empty chunks at the end are filtered out
    - Only chunks with non-empty text appear in the output
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text=""),
        Chunk(start_index=5, end_index=10, text="Hello"),
        Chunk(start_index=10, end_index=15, text=""),
    ]
    ellipsis_message = "\n[...]\n"
    expected = "Hello"

    logger.info(f"[TEST] {test_render_chunks_empty_text.__name__}")
    logger.debug(visualize_processing_pipeline(chunks, expected, format_fn=None))
    logger.debug(
        f"  Empty chunks: {len([c for c in chunks if len(c.text) == 0])} chunks will be filtered"
    )

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    assert ellipsis_message not in result
    logger.success("  ✓ Test passed: Correctly filtered out chunks with empty text")


def test_render_chunks_iterable():
    """Verify iterable support: accepts any iterable type, not just lists.

    The chunks parameter should accept any iterable type (list, tuple, generator, etc.),
    not just lists. This demonstrates flexibility in the API and allows for more
    efficient memory usage with generators.
    """
    chunks = (
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=4, end_index=10, text="o world"),
    )
    expected = "Hello world"

    logger.info(f"[TEST] {test_render_chunks_iterable.__name__}")
    logger.debug("  Input: tuple of chunks")
    logger.debug(visualize_chunks(list(chunks), "Input Chunks"))
    logger.debug(f"  Expected result: '{expected}'")

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled tuple iterable")


def test_render_chunks_three_groups():
    """Verify multiple group separation: correctly handles three or more groups.

    When chunks form three or more groups separated by gaps, render_chunks should
    correctly merge chunks within each group and insert separators between all groups.
    This ensures proper handling of complex scenarios with multiple distinct text segments.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="First"),
        Chunk(start_index=4, end_index=10, text="st group"),
        Chunk(start_index=20, end_index=25, text="Second"),
        Chunk(start_index=40, end_index=45, text="Third"),
    ]
    ellipsis_message = "\n[...]\n"
    # First chunks merged (overlap removed), then separator, Second, separator, Third
    # "First" + "st group" -> overlap "st" removed -> "First group"
    expected = f"First group{ellipsis_message}Second{ellipsis_message}Third"

    logger.info(f"[TEST] {test_render_chunks_three_groups.__name__}")
    logger.debug(
        visualize_processing_pipeline(
            chunks, expected, format_fn=None, ellipsis_message=ellipsis_message
        )
    )
    logger.debug(visualize_chunk_groups(chunks))

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Number of separators: {result.count(ellipsis_message)}")

    assert result == expected
    assert result.count(ellipsis_message) == 2
    logger.success("  ✓ Test passed: Correctly rendered three groups with separators")


def test_render_chunks_boundary_meeting():
    """Verify boundary case: chunks meeting exactly at boundary are merged.

    When chunks meet exactly at the boundary (chunk2.start_index == chunk1.end_index),
    they should be merged without separators. This handles the standard case for
    sequential chunks forming continuous content.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=5, end_index=10, text=" there"),
    ]
    ellipsis_message = "\n[...]\n"
    expected = "Hello there"

    logger.info(f"[TEST] {test_render_chunks_boundary_meeting.__name__}")
    logger.debug(visualize_chunks(chunks, "Input Chunks"))
    logger.debug(
        f"  Boundary: chunk2.start_index ({chunks[1].start_index}) == chunk1.end_index ({chunks[0].end_index})"
    )
    logger.debug(f"  Expected result: '{expected}' (no separator, chunks merged)")

    result = render_chunks(chunks, format_fn=None)

    logger.debug(f"  Actual result: '{result}'")

    assert result == expected
    assert ellipsis_message not in result
    logger.success("  ✓ Test passed: Correctly merged chunks meeting at boundary")


# ============================================================================
# Parametrized tests for different formatters
# ============================================================================


@pytest.mark.parametrize("format_fn,formatter_name", FORMATTERS)
@pytest.mark.parametrize("data_key,data_set", TEST_DATA_SETS.items())
def test_render_chunks_with_formatters(format_fn, formatter_name, data_key, data_set):
    """Verify render_chunks works correctly with different formatters.

    This parametrized test iterates through all formatter functions (None, xmlify,
    jsonify, toonify) and all test data sets to ensure that render_chunks correctly
    processes chunks and applies formatting functions.

    Parameters
    ----------
    format_fn : FormatFn | None
        The formatter function to use (None for plain text).
    formatter_name : str
        Human-readable name of the formatter for logging.
    data_key : str
        Key identifying the test data set.
    data_set : dict
        Dictionary containing 'chunks' and 'description' for the test data.
    """
    chunks = data_set["chunks"]
    description = data_set["description"]
    ellipsis_message = "\n[...]\n"

    logger.info(
        f"[TEST] {test_render_chunks_with_formatters.__name__} - {formatter_name} - {data_key} ({description})"
    )
    logger.debug(f"  Data set: {data_key}")
    logger.debug(f"  Formatter: {formatter_name}")
    logger.debug(f"  Number of chunks: {len(chunks)}")

    result = render_chunks(
        chunks, format_fn=format_fn, ellipsis_message=ellipsis_message
    )

    logger.debug(
        visualize_processing_pipeline(
            chunks, result, format_fn=format_fn, ellipsis_message=ellipsis_message
        )
    )
    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Result length: {len(result)}")

    # Basic assertions that should hold for all formatters
    assert isinstance(result, str)

    # If format_fn is None, result should contain chunk texts
    if format_fn is None:
        # For adjacent chunks, texts should be merged
        # For non-adjacent chunks, ellipsis should be present
        if len(chunks) > 1:
            # Check if chunks are adjacent (simplified check)
            from chonkie_chunk_utils.utils.is_adjacent_chunks import is_adjacent_chunks

            is_adjacent = all(
                is_adjacent_chunks(chunks[i], chunks[i + 1])
                for i in range(len(chunks) - 1)
            )
            if is_adjacent:
                # Adjacent chunks should be merged without separator
                assert ellipsis_message not in result
            else:
                # Non-adjacent chunks should have separator
                assert ellipsis_message in result
    else:
        # For formatters, result should contain formatted output
        # Each merged chunk should be formatted
        assert len(result) > 0

        # Verify formatter-specific patterns
        # Check if format_fn is a partial function (wrap_xml=True case)
        is_wrapped_jsonify = hasattr(format_fn, "func") and format_fn.func == jsonify
        is_wrapped_toonify = hasattr(format_fn, "func") and format_fn.func == toonify

        if format_fn == xmlify:
            assert "<chunk" in result or result == ""
        elif format_fn == jsonify or is_wrapped_jsonify:
            # JSON should contain quotes or braces
            assert ("{" in result or '"' in result) or result == ""
            # If wrap_xml=True, should have XML wrapper
            if is_wrapped_jsonify:
                assert "<chunk>" in result and "</chunk>" in result or result == ""
        elif format_fn == toonify or is_wrapped_toonify:
            # TOON format is less predictable, just check it's not empty (unless no chunks)
            if chunks:
                assert len(result) > 0
            # If wrap_xml=True, should have XML wrapper
            if is_wrapped_toonify:
                assert "<chunk>" in result and "</chunk>" in result or result == ""

    logger.success(
        f"  ✓ Test passed: {formatter_name} correctly processed {data_key} ({description})"
    )
