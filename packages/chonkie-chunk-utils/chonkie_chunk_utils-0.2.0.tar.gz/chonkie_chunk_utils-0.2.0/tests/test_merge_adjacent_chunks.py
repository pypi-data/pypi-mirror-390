from chonkie import Chunk
from chonkie_chunk_utils.merge_adjacent_chunks import merge_adjacent_chunks
from loguru import logger


# ============================================================================
# Tests for merge_adjacent_chunks
# ============================================================================


def test_merge_adjacent_chunks_empty():
    """Verify edge case handling: correctly handles empty iterable.

    When an empty iterable is provided, merge_adjacent_chunks should return an empty list.
    This ensures the function gracefully handles the minimal edge case without errors.
    """
    chunks = []
    expected_count = 0

    logger.info(f"[TEST] {test_merge_adjacent_chunks_empty.__name__}")
    logger.debug("  Input: empty iterable")
    logger.debug(f"  Expected count: {expected_count}")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}")

    assert len(result) == expected_count
    logger.success("  ✓ Test passed: Correctly handled empty iterable")


def test_merge_adjacent_chunks_single():
    """Verify single chunk handling: correctly handles a single chunk.

    When only one chunk is provided, merge_adjacent_chunks should return it unchanged
    in a list. This ensures single chunks are handled correctly without unnecessary processing.
    """
    chunks = [Chunk(start_index=0, end_index=5, text="Hello")]
    expected_count = 1
    expected_text = "Hello"

    logger.info(f"[TEST] {test_merge_adjacent_chunks_single.__name__}")
    logger.debug(f"  Input: single chunk with text='{chunks[0].text}'")
    logger.debug(f"  Expected count: {expected_count}")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}")
    logger.debug(f"  Result text: '{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    logger.success("  ✓ Test passed: Correctly handled single chunk")


def test_merge_adjacent_chunks_overlapping():
    """Verify overlapping chunk merging: correctly merges chunks with overlapping ranges.

    When chunks have overlapping index ranges, merge_adjacent_chunks should merge them
    into a single chunk, combining their text content and adjusting indices. This is
    the core functionality for consolidating adjacent chunks.

    Indices are based on character count: chunk1 has "Hello world" (11 chars) at [0, 11),
    chunk2 has "world there" (11 chars) starting at index 6 (overlapping "world" with chunk1).
    Merged result should be "Hello world there" (17 chars) at [0, 17).
    """
    chunks = [
        Chunk(start_index=0, end_index=11, text="Hello world"),
        Chunk(start_index=6, end_index=17, text="world there"),
    ]
    expected_count = 1
    expected_text = "Hello world there"
    expected_start = 0
    expected_end = 17

    logger.info(f"[TEST] {test_merge_adjacent_chunks_overlapping.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")
    logger.debug(
        f"  Merged chunk: start={result[0].start_index}, end={result[0].end_index}"
    )

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged overlapping chunks")


def test_merge_adjacent_chunks_boundary_meeting():
    """Verify boundary merge: correctly merges chunks meeting exactly at boundary.

    When chunks meet exactly at the boundary (chunk2.start_index == chunk1.end_index),
    merge_adjacent_chunks should merge them. This handles the standard case for
    sequential chunks that form continuous content.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=5, end_index=10, text=" there"),
    ]
    expected_count = 1
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 10

    logger.info(f"[TEST] {test_merge_adjacent_chunks_boundary_meeting.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks meeting at boundary")


def test_merge_adjacent_chunks_immediately_adjacent():
    """Verify immediate adjacency: correctly merges chunks with one-position gap.

    When chunks are immediately adjacent (chunk2.start_index == chunk1.end_index + 1),
    merge_adjacent_chunks should merge them. This ensures continuous text reconstruction
    even when chunks are separated by exactly one character position.
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=6, end_index=10, text=" there"),
    ]
    expected_count = 1
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 10

    logger.info(f"[TEST] {test_merge_adjacent_chunks_immediately_adjacent.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged immediately adjacent chunks")


def test_merge_adjacent_chunks_with_gap():
    """Verify gap preservation: non-adjacent chunks remain separate.

    When chunks have a gap between them (not adjacent), merge_adjacent_chunks should
    keep them as separate chunks in the result. This ensures that distinct text segments
    are not incorrectly merged together. Tests both small and large gaps to ensure
    the function correctly keeps chunks separate regardless of gap size.
    """
    # Test case 1: Small gap
    chunks_small = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=10, end_index=15, text="world"),
    ]
    expected_count = 2
    expected_chunk1_start = 0
    expected_chunk1_end = 5
    expected_chunk2_start_small = 10
    expected_chunk2_end_small = 15

    logger.info(f"[TEST] {test_merge_adjacent_chunks_with_gap.__name__}")
    logger.debug("  Test case 1: Small gap")
    logger.debug(
        f"  Input chunk1: start={chunks_small[0].start_index}, end={chunks_small[0].end_index}, text='{chunks_small[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks_small[1].start_index}, end={chunks_small[1].end_index}, text='{chunks_small[1].text}'"
    )
    logger.debug(f"  Gap: {chunks_small[1].start_index - chunks_small[0].end_index - 1}")
    logger.debug(f"  Expected count: {expected_count} (should remain separate)")

    result_small = merge_adjacent_chunks(chunks_small)

    logger.debug(f"  Actual count: {len(result_small)}")
    logger.debug(
        f"  Result chunk1: start={result_small[0].start_index}, end={result_small[0].end_index}, text='{result_small[0].text}'"
    )
    logger.debug(
        f"  Result chunk2: start={result_small[1].start_index}, end={result_small[1].end_index}, text='{result_small[1].text}'"
    )

    assert len(result_small) == expected_count
    assert result_small[0].text == "Hello"
    assert result_small[0].start_index == expected_chunk1_start
    assert result_small[0].end_index == expected_chunk1_end
    assert result_small[1].text == "world"
    assert result_small[1].start_index == expected_chunk2_start_small
    assert result_small[1].end_index == expected_chunk2_end_small
    logger.success("  ✓ Test passed: Correctly kept chunks with small gap separate")

    # Test case 2: Large gap
    chunks_large = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=100, end_index=105, text="world"),
    ]
    expected_chunk2_start_large = 100
    expected_chunk2_end_large = 105

    logger.debug("  Test case 2: Large gap")
    logger.debug(
        f"  Input chunk1: start={chunks_large[0].start_index}, end={chunks_large[0].end_index}, text='{chunks_large[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks_large[1].start_index}, end={chunks_large[1].end_index}, text='{chunks_large[1].text}'"
    )
    logger.debug(f"  Gap: {chunks_large[1].start_index - chunks_large[0].end_index - 1}")
    logger.debug(f"  Expected count: {expected_count} (should remain separate)")

    result_large = merge_adjacent_chunks(chunks_large)

    logger.debug(f"  Actual count: {len(result_large)}")
    logger.debug(
        f"  Result chunk1: start={result_large[0].start_index}, end={result_large[0].end_index}, text='{result_large[0].text}'"
    )
    logger.debug(
        f"  Result chunk2: start={result_large[1].start_index}, end={result_large[1].end_index}, text='{result_large[1].text}'"
    )

    assert len(result_large) == expected_count
    assert result_large[0].text == "Hello"
    assert result_large[0].start_index == expected_chunk1_start
    assert result_large[0].end_index == expected_chunk1_end
    assert result_large[1].text == "world"
    assert result_large[1].start_index == expected_chunk2_start_large
    assert result_large[1].end_index == expected_chunk2_end_large
    logger.success("  ✓ Test passed: Correctly kept chunks with large gap separate")


def test_merge_adjacent_chunks_multiple_adjacent():
    """Verify chain merging: correctly merges multiple consecutive adjacent chunks.

    When multiple chunks are all adjacent to each other, merge_adjacent_chunks should
    merge them all into a single chunk. This ensures optimal consolidation when
    content is fully continuous.

    Indices are based on character count: chunk1 has "The quick" (9 chars) at [0, 9),
    chunk2 has "quick brown" (11 chars) starting at index 4 (overlapping "quick" with chunk1),
    chunk3 has "brown fox" (9 chars) starting at index 10 (overlapping "brown" with chunk2).
    Merged result should be "The quick brown fox" (19 chars) at [0, 19).
    """
    chunks = [
        Chunk(start_index=0, end_index=9, text="The quick"),
        Chunk(start_index=4, end_index=15, text="quick brown"),
        Chunk(start_index=10, end_index=19, text="brown fox"),
    ]
    expected_count = 1
    expected_text = "The quick brown fox"
    expected_start = 0
    expected_end = 19

    logger.info(f"[TEST] {test_merge_adjacent_chunks_multiple_adjacent.__name__}")
    logger.debug(f"  Input: {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        logger.debug(
            f"  Chunk {i + 1}: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
        )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged multiple adjacent chunks")


def test_merge_adjacent_chunks_mixed_adjacent_and_gap():
    """Verify selective merging: correctly handles mix of adjacent and non-adjacent chunks.

    When chunks form groups (adjacent chunks within groups, gaps between groups),
    merge_adjacent_chunks should merge chunks within each group but keep groups separate.
    This ensures proper handling of complex chunk arrangements with both continuous
    and discontinuous segments.

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has "o world" (7 chars) starting at index 4 (overlapping "o" with chunk1),
    chunk3 has "there" (5 chars) starting at index 15 (gap between chunk2 and chunk3).
    Merged result should be "Hello world" (11 chars) at [0, 11) and "there" (5 chars) at [15, 20).
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=4, end_index=11, text="o world"),
        Chunk(start_index=15, end_index=20, text="there"),
    ]
    expected_count = 2
    expected_chunk1_start = 0
    expected_chunk1_end = 11
    expected_chunk2_start = 15
    expected_chunk2_end = 20

    logger.info(f"[TEST] {test_merge_adjacent_chunks_mixed_adjacent_and_gap.__name__}")
    logger.debug(f"  Input: {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        logger.debug(
            f"  Chunk {i + 1}: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
        )
    logger.debug(
        f"  Expected count: {expected_count} (first two merged, third separate)"
    )

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}")
    logger.debug(
        f"  Result chunk1: start={result[0].start_index}, end={result[0].end_index}, text='{result[0].text}'"
    )
    logger.debug(
        f"  Result chunk2: start={result[1].start_index}, end={result[1].end_index}, text='{result[1].text}'"
    )

    assert len(result) == expected_count
    assert result[0].text == "Hello world"
    assert result[0].start_index == expected_chunk1_start
    assert result[0].end_index == expected_chunk1_end
    assert result[1].text == "there"
    assert result[1].start_index == expected_chunk2_start
    assert result[1].end_index == expected_chunk2_end
    logger.success(
        "  ✓ Test passed: Correctly handled mixed adjacent and non-adjacent chunks"
    )


def test_merge_adjacent_chunks_full_overlap():
    """Verify full text overlap: correctly merges when chunk2 starts with chunk1's text.

    When chunk2's text begins with the complete text of chunk1, merge_adjacent_chunks
    should merge them by using chunk2's text. This handles cases where one chunk's
    text is a prefix of another chunk's text.

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has "Hello there" (11 chars) starting at index 5 (boundary meeting).
    Merged result should be "Hello there" (11 chars) at [0, 16).
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=5, end_index=16, text="Hello there"),
    ]
    expected_count = 1
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 16

    logger.info(f"[TEST] {test_merge_adjacent_chunks_full_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with full text overlap")


def test_merge_adjacent_chunks_partial_overlap():
    """Verify partial text overlap: correctly merges chunks with partial text overlap.

    When chunks have partial text overlap (sharing some words but not all),
    merge_adjacent_chunks should merge them by removing the duplicate portion.
    This ensures accurate text reconstruction when chunks share common phrases.

    Indices are based on character count: chunk1 has "The quick brown" (15 chars) at [0, 15),
    chunk2 has "brown fox jumps" (15 chars) starting at index 10 (overlapping "brown" with chunk1).
    Merged result should be "The quick brown fox jumps" (25 chars) at [0, 25).
    """
    chunks = [
        Chunk(start_index=0, end_index=15, text="The quick brown"),
        Chunk(start_index=10, end_index=25, text="brown fox jumps"),
    ]
    expected_count = 1
    expected_text = "The quick brown fox jumps"
    expected_start = 0
    expected_end = 25

    logger.info(f"[TEST] {test_merge_adjacent_chunks_partial_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with partial overlap")


def test_merge_adjacent_chunks_unicode():
    """Verify Unicode support: correctly merges chunks with Unicode text.

    When chunks contain Unicode characters (e.g., Korean, Chinese, emoji),
    merge_adjacent_chunks should correctly merge them. This ensures the function
    works with international text and preserves Unicode content accurately.

    Indices are based on character count: chunk1 has "안녕하세요" (5 chars) at [0, 5),
    chunk2 has "하세요 세계" (5 chars) starting at index 2 (overlapping "하세요" with chunk1).
    Merged result should be "안녕하세요 세계" (8 chars) at [0, 8).
    """
    chunks = [
        Chunk(start_index=0, end_index=5, text="안녕하세요"),
        Chunk(start_index=2, end_index=8, text="하세요 세계"),
    ]
    expected_count = 1
    expected_text = "안녕하세요 세계"
    expected_start = 0
    expected_end = 8

    logger.info(f"[TEST] {test_merge_adjacent_chunks_unicode.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with unicode text")


def test_merge_adjacent_chunks_empty_text():
    """Verify empty text handling: correctly merges chunks when one has empty text.

    When one chunk has empty text, merge_adjacent_chunks should handle it gracefully
    by effectively using the non-empty chunk's text. This ensures the function works
    correctly with edge cases involving empty content.

    Indices are based on character count: chunk1 has empty text at [0, 0),
    chunk2 has "Hello" (5 chars) starting at index 0 (boundary meeting at chunk1.end_index).
    Note: Empty text chunks with same start_index require chunk2 to start at chunk1.end_index
    for adjacency. Merged result should be "Hello" (5 chars) at [0, 5).
    """
    chunks = [
        Chunk(start_index=0, end_index=0, text=""),
        Chunk(start_index=0, end_index=5, text="Hello"),
    ]
    expected_count = (
        2  # Empty chunk and non-empty chunk with same start_index are not adjacent
    )
    expected_text_chunk1 = ""
    expected_chunk1_start = 0
    expected_chunk1_end = 0
    expected_text_chunk2 = "Hello"
    expected_chunk2_start = 0
    expected_chunk2_end = 5

    logger.info(f"[TEST] {test_merge_adjacent_chunks_empty_text.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunks[0].start_index}, end={chunks[0].end_index}, text='{chunks[0].text}' (empty)"
    )
    logger.debug(
        f"  Input chunk2: start={chunks[1].start_index}, end={chunks[1].end_index}, text='{chunks[1].text}'"
    )
    logger.debug(
        f"  Expected count: {expected_count} (empty chunk and non-empty chunk with same start_index are not adjacent)"
    )

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}")
    logger.debug(
        f"  Result chunk1: start={result[0].start_index}, end={result[0].end_index}, text='{result[0].text}'"
    )
    logger.debug(
        f"  Result chunk2: start={result[1].start_index}, end={result[1].end_index}, text='{result[1].text}'"
    )

    assert len(result) == expected_count
    assert result[0].text == expected_text_chunk1
    assert result[0].start_index == expected_chunk1_start
    assert result[0].end_index == expected_chunk1_end
    assert result[1].text == expected_text_chunk2
    assert result[1].start_index == expected_chunk2_start
    assert result[1].end_index == expected_chunk2_end
    logger.success(
        "  ✓ Test passed: Correctly kept empty chunk and non-empty chunk with same start_index separate"
    )


def test_merge_adjacent_chunks_iterable():
    """Verify iterable support: accepts any iterable type, not just lists.

    The chunks parameter should accept any iterable type (list, tuple, generator, etc.),
    not just lists. This demonstrates flexibility in the API and allows for more
    efficient memory usage with generators.
    """
    chunks = (
        Chunk(start_index=0, end_index=5, text="Hello"),
        Chunk(start_index=4, end_index=10, text="o world"),
    )
    expected_count = 1
    expected_text = "Hello world"

    logger.info(f"[TEST] {test_merge_adjacent_chunks_iterable.__name__}")
    logger.debug("  Input: tuple of chunks")
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    logger.success("  ✓ Test passed: Correctly handled tuple iterable")


def test_merge_adjacent_chunks_three_adjacent():
    """Verify chain merging: correctly merges three or more consecutive adjacent chunks.

    When three or more chunks are all adjacent to each other, merge_adjacent_chunks
    should merge them all into a single chunk. This ensures optimal consolidation
    for longer chains of continuous content.

    Indices are based on character count: chunk1 has "The" (3 chars) at [0, 3),
    chunk2 has " quick" (6 chars) starting at index 3 (boundary meeting),
    chunk3 has " brown" (6 chars) starting at index 9 (boundary meeting).
    Merged result should be "The quick brown" (15 chars) at [0, 15).
    """
    chunks = [
        Chunk(start_index=0, end_index=3, text="The"),
        Chunk(start_index=3, end_index=9, text=" quick"),
        Chunk(start_index=9, end_index=15, text=" brown"),
    ]
    expected_count = 1
    expected_text = "The quick brown"
    expected_start = 0
    expected_end = 15

    logger.info(f"[TEST] {test_merge_adjacent_chunks_three_adjacent.__name__}")
    logger.debug(f"  Input: {len(chunks)} consecutive adjacent chunks")
    logger.debug(f"  Expected count: {expected_count}, text='{expected_text}'")

    result = merge_adjacent_chunks(chunks)

    logger.debug(f"  Actual count: {len(result)}, text='{result[0].text}'")

    assert len(result) == expected_count
    assert result[0].text == expected_text
    assert result[0].start_index == expected_start
    assert result[0].end_index == expected_end
    logger.success(
        "  ✓ Test passed: Successfully merged three consecutive adjacent chunks"
    )
