from chonkie.types.base import Chunk
from chonkie_chunk_utils.utils.merge_chunks import merge_chunks, _find_text_overlap
import pytest
from loguru import logger


# ============================================================================
# Tests for _find_text_overlap
# ============================================================================


def test_find_text_overlap_single_word():
    """Verify text overlap detection: correctly identifies overlapping word between two texts.

    When text2 starts with the ending of text1 (e.g., "Hello world" and "world there"),
    the function should correctly identify the overlap length. This is fundamental for
    merging chunks with overlapping text content without duplicating shared segments.
    """
    text1 = "Hello world"
    text2 = "world there"
    expected = 5

    logger.info(f"[TEST] {test_find_text_overlap_single_word.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}' (if result > 0)")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found overlap length {result}")


def test_find_text_overlap_full_prefix():
    """Verify full prefix overlap: text2 starts with the complete text1.

    When text2 begins with the entire text1 (e.g., "Hello" and "Hello there"),
    the function should identify the full length of text1 as the overlap. This handles
    cases where one chunk's text is a prefix of another chunk's text.
    """
    text1 = "Hello"
    text2 = "Hello there"
    expected = 5

    logger.info(f"[TEST] {test_find_text_overlap_full_prefix.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}' (if result > 0)")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found overlap length {result}")


def test_find_text_overlap_no_overlap():
    """Verify no overlap detection: correctly identifies when texts don't overlap.

    When text2 doesn't start with any ending portion of text1, the function should
    return 0. This is important for distinguishing between chunks that can be merged
    (with overlap) and those that should remain separate.
    """
    text1 = "Hello"
    text2 = "there"
    expected = 0

    logger.info(f"[TEST] {test_find_text_overlap_no_overlap.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (no overlap)")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly identified no overlap")


def test_find_text_overlap_multiple_words():
    """Verify multi-word overlap detection: correctly identifies overlapping phrase.

    When text2 starts with multiple words from the end of text1, the function should
    identify the full phrase overlap. This ensures that common phrases spanning
    multiple words are correctly detected and handled during chunk merging.
    """
    text1 = "The quick brown"
    text2 = "quick brown fox"
    expected = 11

    logger.info(f"[TEST] {test_find_text_overlap_multiple_words.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: 'quick brown')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found multi-word overlap length {result}")


def test_find_text_overlap_single_character():
    """Verify single character overlap: correctly identifies minimal overlap.

    When text2 starts with the last character of text1, the function should identify
    the single character overlap. This tests the function's ability to handle the
    smallest possible overlap case, including partial word overlaps at word boundaries
    or within words, ensuring accurate text merging.
    """
    text1 = "Hello"
    text2 = "o there"
    expected = 1

    logger.info(f"[TEST] {test_find_text_overlap_single_character.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: 'o')")
    logger.debug(
        "  Testing both single character and partial word overlap perspectives"
    )

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(
        f"  ✓ Test passed: Found single character/partial word overlap length {result}"
    )


def test_find_text_overlap_whitespace():
    """Verify whitespace handling: correctly identifies overlap including whitespace characters.

    When overlap includes whitespace characters (spaces, tabs, newlines), the function
    should correctly identify them. This is important for preserving proper text
    formatting when merging chunks that share whitespace boundaries.
    """
    text1 = "Hello "
    text2 = " world"
    expected = 1

    logger.info(f"[TEST] {test_find_text_overlap_whitespace.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: ' ')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found whitespace overlap length {result}")


def test_find_text_overlap_empty_text1():
    """Verify edge case handling: correctly handles empty text1.

    When text1 is empty, there can be no overlap, so the function should return 0.
    This ensures the function gracefully handles edge cases without errors.
    """
    text1 = ""
    text2 = "Hello"
    expected = 0

    logger.info(f"[TEST] {test_find_text_overlap_empty_text1.__name__}")
    logger.debug(f"  Input: text1='{text1}' (empty), text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled empty text1")


def test_find_text_overlap_empty_text2():
    """Verify edge case handling: correctly handles empty text2.

    When text2 is empty, there can be no overlap, so the function should return 0.
    This ensures the function handles empty input gracefully.
    """
    text1 = "Hello"
    text2 = ""
    expected = 0

    logger.info(f"[TEST] {test_find_text_overlap_empty_text2.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}' (empty)")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled empty text2")


def test_find_text_overlap_both_empty():
    """Verify edge case handling: correctly handles both texts being empty.

    When both text1 and text2 are empty, there can be no overlap, so the function
    should return 0. This ensures the function handles the minimal edge case correctly.
    """
    text1 = ""
    text2 = ""
    expected = 0

    logger.info(f"[TEST] {test_find_text_overlap_both_empty.__name__}")
    logger.debug(f"  Input: text1='{text1}' (empty), text2='{text2}' (empty)")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")

    assert result == expected
    logger.success("  ✓ Test passed: Correctly handled both empty texts")


def test_find_text_overlap_identical_texts():
    """Verify identical text handling: correctly identifies full overlap for identical texts.

    When text1 and text2 are identical, the function should identify the full length
    as overlap. This handles cases where chunks contain the same text content.
    """
    text1 = "Hello"
    text2 = "Hello"
    expected = 5

    logger.info(f"[TEST] {test_find_text_overlap_identical_texts.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}' (identical)")
    logger.debug(f"  Expected overlap length: {expected}")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success("  ✓ Test passed: Found full overlap for identical texts")


def test_find_text_overlap_longest_match():
    """Verify longest match selection: finds the maximum possible overlap length.

    When multiple overlap possibilities exist, the function should identify the longest
    match. This ensures optimal text merging by maximizing the overlap detection,
    which is critical for accurate chunk combination.
    """
    text1 = "xabc"
    text2 = "abcx"
    expected = 3  # "abc" appears at end of text1 and start of text2

    logger.info(f"[TEST] {test_find_text_overlap_longest_match.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (should find longest: 'abc')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found longest overlap length {result}")


def test_find_text_overlap_repeated_pattern():
    """Verify repeated pattern handling: correctly identifies overlap in patterns.

    When texts contain repeated patterns (e.g., "ababab" and "abab"), the function
    should identify the longest matching pattern. This tests the algorithm's ability
    to handle complex text structures with repeating sequences.
    """
    text1 = "ababab"
    text2 = "abab"
    expected = 4  # "abab"

    logger.info(f"[TEST] {test_find_text_overlap_repeated_pattern.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: 'abab')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found repeated pattern overlap length {result}")


def test_find_text_overlap_unicode():
    """Verify Unicode support: correctly identifies overlap in Unicode text.

    When texts contain Unicode characters (e.g., Korean, Chinese), the function should
    correctly identify overlaps. This ensures the function works with international
    text and multi-byte characters, which is essential for global text processing.
    """
    text1 = "안녕하세요"
    text2 = "하세요 세계"
    expected = 3  # "하세요" (3 characters)

    logger.info(f"[TEST] {test_find_text_overlap_unicode.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: '하세요')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found unicode overlap length {result}")


def test_find_text_overlap_mixed_unicode():
    """Verify mixed character handling: correctly identifies overlap in mixed Unicode/ASCII text.

    When texts contain a mix of Unicode and ASCII characters, the function should
    correctly identify overlaps. This ensures the function handles real-world text
    that often contains both character types.
    """
    text1 = "Hello 안녕"
    text2 = "안녕 there"
    expected = 2  # "안녕"

    logger.info(f"[TEST] {test_find_text_overlap_mixed_unicode.__name__}")
    logger.debug(f"  Input: text1='{text1}', text2='{text2}'")
    logger.debug(f"  Expected overlap length: {expected} (overlap: '안녕')")

    result = _find_text_overlap(text1, text2)

    logger.debug(f"  Actual overlap length: {result}")
    logger.debug(f"  Overlap text: '{text1[-result:]}'")

    assert result == expected
    logger.success(f"  ✓ Test passed: Found mixed unicode overlap length {result}")


# ============================================================================
# Tests for merge_chunks
# ============================================================================

# --- Overlapping chunks tests ---


def test_merge_overlapping_chunks():
    """Verify basic merge functionality: correctly merges chunks with overlapping text.

    When two chunks have overlapping text content, merge_chunks should combine them
    into a single chunk, removing the duplicate overlap and preserving the combined
    text. This is the core functionality for consolidating adjacent chunks.

    Indices are based on character count: chunk1 has "Hello world" (11 chars) at [0, 11),
    chunk2 has "world there" (11 chars) starting at index 6 (overlapping "world" with chunk1).
    Merged result should be "Hello world there" (17 chars) at [0, 17).
    """
    chunk1 = Chunk(start_index=0, end_index=11, text="Hello world")
    chunk2 = Chunk(start_index=6, end_index=17, text="world there")
    expected_text = "Hello world there"
    expected_start = 0
    expected_end = 17

    logger.info(f"[TEST] {test_merge_overlapping_chunks.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged overlapping chunks")


def test_merge_chunks_full_overlap():
    """Verify full overlap handling: correctly merges when chunk2 starts with chunk1's text.

    When chunk2's text begins with the complete text of chunk1, merge_chunks should
    merge them by using chunk2's text (which contains chunk1's text as a prefix).
    This handles cases where one chunk is a prefix of another.

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has "Hello there" (11 chars) starting at index 5 (overlapping "Hello" with chunk1).
    Merged result should be "Hello there" (11 chars) at [0, 16), where end_index=16 is max(5, 16).
    """
    chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2 = Chunk(start_index=5, end_index=16, text="Hello there")
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 16

    logger.info(f"[TEST] {test_merge_chunks_full_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with full overlap")


def test_merge_chunks_partial_overlap():
    """Verify partial overlap handling: correctly merges chunks with partial text overlap.

    When chunks have partial text overlap (sharing some words but not all), merge_chunks
    should combine them by removing the duplicate portion. This ensures accurate text
    reconstruction when chunks share common phrases.

    Indices are based on character count: chunk1 has "The quick brown" (15 chars) at [0, 15),
    chunk2 has "brown fox jumps" (15 chars) starting at index 10 (overlapping "brown" with chunk1).
    Merged result should be "The quick brown fox jumps" (25 chars) at [0, 25).
    """
    chunk1 = Chunk(start_index=0, end_index=15, text="The quick brown")
    chunk2 = Chunk(start_index=10, end_index=25, text="brown fox jumps")
    expected_text = "The quick brown fox jumps"
    expected_start = 0
    expected_end = 25

    logger.info(f"[TEST] {test_merge_chunks_partial_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with partial overlap")


def test_merge_chunks_boundary_no_overlap():
    """Verify boundary merge: correctly merges chunks meeting at boundary without text overlap.

    When chunks meet at the boundary (chunk2.start_index == chunk1.end_index) but have
    no text overlap, merge_chunks should combine them by concatenating the texts.
    This handles sequential chunks that form continuous content.

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has " there" (6 chars) starting at index 5.
    Merged result should be "Hello there" (11 chars) at [0, 11).
    """
    chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2 = Chunk(start_index=5, end_index=11, text=" there")
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 11

    logger.info(f"[TEST] {test_merge_chunks_boundary_no_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks meeting at boundary")


def test_merge_chunks_adjacent_no_overlap():
    """Verify adjacent merge: correctly merges immediately adjacent chunks without overlap.

    When chunks are immediately adjacent (chunk2.start_index == chunk1.end_index + 1)
    with no text overlap, merge_chunks should combine them. This ensures continuous
    text reconstruction even when chunks are separated by one character position.

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has " there" (6 chars) starting at index 6 (adjacent, gap at index 5).
    Merged result should be "Hello there" (11 chars) at [0, 12).
    """
    chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2 = Chunk(start_index=6, end_index=12, text=" there")
    expected_text = "Hello there"
    expected_start = 0
    expected_end = 12

    logger.info(f"[TEST] {test_merge_chunks_adjacent_no_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged adjacent chunks")


def test_merge_chunks_with_whitespace():
    """Verify whitespace preservation: correctly handles overlaps containing whitespace.

    When chunk overlap includes whitespace characters, merge_chunks should preserve
    proper formatting. This ensures that text structure and readability are maintained
    when merging chunks with whitespace boundaries.

    Indices are based on character count: chunk1 has "Hello " (6 chars) at [0, 6),
    chunk2 has " world" (6 chars) starting at index 5 (overlapping " " with chunk1).
    Merged result should be "Hello world" (11 chars) at [0, 11).
    """
    chunk1 = Chunk(start_index=0, end_index=6, text="Hello ")
    chunk2 = Chunk(start_index=5, end_index=11, text=" world")

    logger.info(f"[TEST] {test_merge_chunks_with_whitespace.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug("  Expected: merged text should contain 'Hello' and 'world'")

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert "Hello" in merged.text
    assert "world" in merged.text
    logger.success(
        "  ✓ Test passed: Successfully merged chunks with whitespace overlap"
    )


# --- Error cases tests ---


def test_merge_chunks_not_adjacent_raises_error():
    """Verify error handling: raises ValueError when chunks are not adjacent.

    When chunks have a gap between them (not adjacent), merge_chunks should raise
    a ValueError. This prevents accidental merging of unrelated chunks and ensures
    data integrity in chunk operations. Tests both small and large gaps to ensure
    the function correctly rejects any non-adjacent chunks regardless of gap size.
    """
    # Test case 1: Small gap
    chunk1_small = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2_small = Chunk(start_index=10, end_index=15, text="world")
    gap_small = chunk2_small.start_index - chunk1_small.end_index - 1

    logger.info(f"[TEST] {test_merge_chunks_not_adjacent_raises_error.__name__}")
    logger.debug("  Test case 1: Small gap")
    logger.debug(
        f"  Input chunk1: start={chunk1_small.start_index}, end={chunk1_small.end_index}, text='{chunk1_small.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2_small.start_index}, end={chunk2_small.end_index}, text='{chunk2_small.text}'"
    )
    logger.debug(f"  Gap between chunks: {gap_small}")
    logger.debug("  Expected: ValueError (chunks are not adjacent)")

    with pytest.raises(ValueError, match="Chunks are not adjacent") as exc_info:
        merge_chunks(chunk1_small, chunk2_small)

    logger.debug(f"  Exception raised: {exc_info.value}")
    logger.success("  ✓ Test passed: Correctly raised ValueError for small gap")

    # Test case 2: Large gap
    chunk1_large = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2_large = Chunk(start_index=100, end_index=105, text="world")
    gap_large = chunk2_large.start_index - chunk1_large.end_index - 1

    logger.debug("  Test case 2: Large gap")
    logger.debug(
        f"  Input chunk1: start={chunk1_large.start_index}, end={chunk1_large.end_index}, text='{chunk1_large.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2_large.start_index}, end={chunk2_large.end_index}, text='{chunk2_large.text}'"
    )
    logger.debug(f"  Gap between chunks: {gap_large}")
    logger.debug("  Expected: ValueError (chunks are not adjacent)")

    with pytest.raises(ValueError, match="Chunks are not adjacent") as exc_info:
        merge_chunks(chunk1_large, chunk2_large)

    logger.debug(f"  Exception raised: {exc_info.value}")
    logger.success("  ✓ Test passed: Correctly raised ValueError for large gap")


def test_merge_chunks_reverse_order_raises_error():
    """Verify error handling: raises ValueError for chunks in reverse order.

    When chunks are provided in reverse order (chunk2 before chunk1), merge_chunks
    should raise a ValueError. This ensures proper validation of input ordering
    and prevents incorrect merge results. Tests both cases: with overlap and with gap.
    """
    # Test case 1: Reverse order with overlap (chunk2 contains chunk1)
    chunk1_overlap = Chunk(start_index=5, end_index=10, text="world")
    chunk2_overlap = Chunk(start_index=0, end_index=6, text="Hello world")

    logger.info(f"[TEST] {test_merge_chunks_reverse_order_raises_error.__name__}")
    logger.debug("  Test case 1: Reverse order with overlap")
    logger.debug(
        f"  Input chunk1: start={chunk1_overlap.start_index}, end={chunk1_overlap.end_index}, text='{chunk1_overlap.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2_overlap.start_index}, end={chunk2_overlap.end_index}, text='{chunk2_overlap.text}'"
    )
    logger.debug("  Expected: ValueError (chunk2 starts before chunk1, with overlap)")

    with pytest.raises(ValueError, match="Chunks are not adjacent") as exc_info:
        merge_chunks(chunk1_overlap, chunk2_overlap)

    logger.debug(f"  Exception raised: {exc_info.value}")
    logger.success(
        "  ✓ Test passed: Correctly raised ValueError for reverse order with overlap"
    )

    # Test case 2: Reverse order with gap
    chunk1_gap = Chunk(start_index=5, end_index=10, text="world")
    chunk2_gap = Chunk(start_index=0, end_index=4, text="Hello")

    logger.debug("  Test case 2: Reverse order with gap")
    logger.debug(
        f"  Input chunk1: start={chunk1_gap.start_index}, end={chunk1_gap.end_index}, text='{chunk1_gap.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2_gap.start_index}, end={chunk2_gap.end_index}, text='{chunk2_gap.text}'"
    )
    logger.debug("  Expected: ValueError (chunk2 starts before chunk1, with gap)")

    with pytest.raises(ValueError, match="Chunks are not adjacent") as exc_info:
        merge_chunks(chunk1_gap, chunk2_gap)

    logger.debug(f"  Exception raised: {exc_info.value}")
    logger.success(
        "  ✓ Test passed: Correctly raised ValueError for reverse order with gap"
    )


def test_merge_chunks_multiple_word_overlap():
    """Verify multi-word overlap handling: correctly merges chunks with phrase overlap.

    When chunks share a multi-word phrase at their boundary, merge_chunks should
    correctly identify and remove the duplicate phrase. This ensures accurate text
    reconstruction for complex overlapping content.

    Indices are based on character count: chunk1 has "The quick brown" (15 chars) at [0, 15),
    chunk2 has "quick brown fox" (15 chars) starting at index 4 (overlapping "quick brown" with chunk1).
    Merged result should be "The quick brown fox" (19 chars) at [0, 19).
    """
    chunk1 = Chunk(start_index=0, end_index=15, text="The quick brown")
    chunk2 = Chunk(start_index=4, end_index=19, text="quick brown fox")
    expected_text = "The quick brown fox"
    expected_start = 0
    expected_end = 19

    logger.info(f"[TEST] {test_merge_chunks_multiple_word_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success(
        "  ✓ Test passed: Successfully merged chunks with multi-word overlap"
    )


def test_merge_chunks_single_character_overlap():
    """Verify single character overlap: correctly merges chunks with minimal overlap.

    When chunks overlap by only a single character, merge_chunks should correctly
    identify and handle it. This tests the function's precision in handling the
    smallest possible overlap case. Also verifies that merged chunk indices are
    correctly computed (start_index = min, end_index = max).

    Indices are based on character count: chunk1 has "Hello" (5 chars) at [0, 5),
    chunk2 has "o there" (7 chars) starting at index 4 (overlapping "o" with chunk1).
    Merged result should be "Hello there" (11 chars) at [0, 11), where start_index=0
    (min(0, 4)) and end_index=11 (max(5, 11)).
    """
    chunk1 = Chunk(start_index=0, end_index=5, text="Hello")
    chunk2 = Chunk(start_index=4, end_index=11, text="o there")
    expected_text = "Hello there"
    expected_start = 0  # min(0, 4)
    expected_end = 11  # max(5, 11)

    logger.info(f"[TEST] {test_merge_chunks_single_character_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start} (min), end={expected_end} (max), text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success(
        "  ✓ Test passed: Successfully merged chunks with single character overlap and verified index calculation"
    )


def test_merge_chunks_unicode_overlap():
    """Verify Unicode overlap handling: correctly merges chunks with Unicode text overlap.

    When chunks contain Unicode characters and have overlapping text, merge_chunks
    should correctly identify and merge them. This ensures the function works with
    international text and multi-byte characters.

    Indices are based on character count: chunk1 has "안녕하세요" (5 chars) at [0, 5),
    chunk2 has "하세요 세계" (5 chars) starting at index 2 (overlapping "하세요" with chunk1).
    Merged result should be "안녕하세요 세계" (8 chars) at [0, 8).
    """
    chunk1 = Chunk(start_index=0, end_index=5, text="안녕하세요")
    chunk2 = Chunk(start_index=2, end_index=8, text="하세요 세계")
    expected_text = "안녕하세요 세계"
    expected_start = 0
    expected_end = 8

    logger.info(f"[TEST] {test_merge_chunks_unicode_overlap.__name__}")
    logger.debug(
        f"  Input chunk1: start={chunk1.start_index}, end={chunk1.end_index}, text='{chunk1.text}'"
    )
    logger.debug(
        f"  Input chunk2: start={chunk2.start_index}, end={chunk2.end_index}, text='{chunk2.text}'"
    )
    logger.debug(
        f"  Expected merged: start={expected_start}, end={expected_end}, text='{expected_text}'"
    )

    merged = merge_chunks(chunk1, chunk2)

    logger.debug(
        f"  Actual merged: start={merged.start_index}, end={merged.end_index}, text='{merged.text}'"
    )

    assert merged.text == expected_text
    assert merged.start_index == expected_start
    assert merged.end_index == expected_end
    logger.success("  ✓ Test passed: Successfully merged chunks with unicode overlap")
