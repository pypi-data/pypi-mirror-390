from chonkie import Chunk
from chonkie_chunk_utils.formatters.toonify import toonify
from toon_python import encode
from loguru import logger


# ============================================================================
# Tests for toonify
# ============================================================================


def test_toonify_basic():
    """Verify basic functionality: converts Chunk to TOON string with default attributes.

    When toonify is called with default parameters, it should produce a valid TOON-encoded string
    containing the default attributes (start_index, end_index, context) and the content field.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_basic.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )

    result = toonify(chunk)

    logger.debug(f"  Actual result: '{result}'")
    logger.debug(f"  Result length: {len(result)}")

    # Verify it's a string
    assert isinstance(result, str)
    assert len(result) > 0
    # Verify it's TOON encoded by checking structure
    # Note: Dictionary key order may vary due to set operations, so we check content instead
    assert "start_index: 0" in result
    assert "end_index: 10" in result
    assert "context: example" in result
    assert "content: Hello world" in result
    logger.success(
        "  ✓ Test passed: Correctly formatted chunk to TOON with default attributes"
    )


def test_toonify_custom_attributes():
    """Verify custom attributes selection: allows specifying which attributes to include.

    When specific attributes are provided via the attributes parameter, only those attributes
    (plus the mandatory content field) should be included in the resulting TOON string.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_custom_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Custom attributes: ['start_index', 'end_index']")

    result = toonify(chunk, attributes=["start_index", "end_index"])

    logger.debug(f"  Actual result: '{result}'")

    # Verify it's a string
    assert isinstance(result, str)
    # Verify it matches manual encoding (key order may vary)
    data1 = {"start_index": 0, "end_index": 10, "content": "Hello world"}
    data2 = {"end_index": 10, "start_index": 0, "content": "Hello world"}
    expected_toon1 = encode(data1)
    expected_toon2 = encode(data2)
    assert result == expected_toon1 or result == expected_toon2
    logger.success("  ✓ Test passed: Correctly formatted chunk with custom attributes")


def test_toonify_single_attribute():
    """Verify single attribute selection: works correctly with only one attribute specified.

    When a single attribute is provided in the attributes list, the resulting TOON string should
    contain only that attribute and the mandatory content field.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_single_attribute.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Single attribute: ['start_index']")

    result = toonify(chunk, attributes=["start_index"])

    logger.debug(f"  Actual result: '{result}'")

    # Verify it matches manual encoding
    data = {"start_index": 0, "content": "Hello world"}
    expected_toon = encode(data)
    assert result == expected_toon
    logger.success("  ✓ Test passed: Correctly formatted chunk with single attribute")


def test_toonify_nonexistent_attributes():
    """Verify graceful handling of nonexistent attributes: filters out attributes that don't exist.

    When attributes list contains attribute names that don't exist in the Chunk, those
    attributes should be silently ignored and only existing attributes should be included.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10)

    logger.info(f"[TEST] {test_toonify_nonexistent_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug(
        "  Attributes with nonexistent: ['start_index', 'end_index', 'context', 'nonexistent']"
    )

    result = toonify(
        chunk, attributes=["start_index", "end_index", "context", "nonexistent"]
    )

    logger.debug(f"  Actual result: '{result}'")

    # Verify structure (key order may vary)
    assert "start_index: 0" in result
    assert "end_index: 10" in result
    assert "content: Hello world" in result
    assert "context:" not in result or "context: null" in result
    logger.success("  ✓ Test passed: Correctly filtered out nonexistent attributes")


def test_toonify_empty_text():
    """Verify handling of empty text content: correctly formats chunks with empty string text.

    When a Chunk has an empty text field, the resulting TOON string should still be valid with
    an empty string value for the content field.
    """
    chunk = Chunk(text="", start_index=0, end_index=0, context="empty")

    logger.info(f"[TEST] {test_toonify_empty_text.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (empty)"
    )

    result = toonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Verify structure (key order may vary)
    assert "start_index: 0" in result
    assert "end_index: 0" in result
    assert "context: empty" in result
    assert "content: " in result  # Empty content
    logger.success("  ✓ Test passed: Correctly handled empty text")


def test_toonify_unicode():
    """Verify Unicode support: correctly handles non-ASCII characters in text and attributes.

    When Chunk contains Unicode characters (e.g., Korean, Chinese, emoji), the TOON output
    should properly encode them and preserve the original Unicode strings.
    """
    chunk = Chunk(text="안녕하세요", start_index=0, end_index=5, context="한국어")

    logger.info(f"[TEST] {test_toonify_unicode.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (unicode)"
    )
    logger.debug(f"  Context: '{chunk.context}' (unicode)")

    result = toonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Verify structure (key order may vary)
    assert "start_index: 0" in result
    assert "end_index: 5" in result
    assert "context: 한국어" in result
    assert "content: 안녕하세요" in result
    logger.success("  ✓ Test passed: Correctly handled unicode text")


def test_toonify_special_characters():
    """Verify special character handling: correctly processes quotes, newlines, and tabs.

    When Chunk contains special characters like quotes, newlines, or tabs, the TOON output
    should handle them appropriately (may be escaped or encoded according to TOON format).
    """
    chunk = Chunk(
        text='Hello "world" with\nnewline\tand\ttab',
        start_index=0,
        end_index=30,
        context='test "quotes"',
    )

    logger.info(f"[TEST] {test_toonify_special_characters.__name__}")
    logger.debug("  Input chunk: text contains quotes, newlines, tabs")
    logger.debug("  Context: contains quotes")

    result = toonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Verify structure (key order may vary, special chars may be escaped)
    assert "start_index: 0" in result
    assert "end_index: 30" in result
    assert "context:" in result
    assert "content:" in result
    # Special characters may be escaped in TOON format
    logger.success("  ✓ Test passed: Correctly handled special characters")


def test_toonify_wrap_xml_false():
    """Verify default behavior: returns plain TOON string without XML tags when wrap_xml is False.

    By default (wrap_xml=False), toonify should return a pure TOON-encoded string without any
    XML wrapper tags.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_wrap_xml_false.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=False (default)")

    result = toonify(chunk, wrap_xml=False)

    logger.debug(f"  Actual result: '{result}'")

    assert not result.startswith("<chunk>")
    assert not result.endswith("</chunk>")
    assert isinstance(result, str)
    logger.success("  ✓ Test passed: Correctly returned TOON without XML wrapping")


def test_toonify_wrap_xml_true():
    """Verify XML wrapping option: wraps TOON string in <chunk> tags when wrap_xml is True.

    When wrap_xml=True, the TOON string should be wrapped in <chunk>...</chunk> XML tags,
    but the XML tag itself should not contain any attributes (unlike xmlify).
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_wrap_xml_true.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=True")

    result = toonify(chunk, wrap_xml=True)

    logger.debug(f"  Actual result: '{result}'")

    assert result.startswith("<chunk>")
    assert result.endswith("</chunk>")
    # Extract TOON part and verify structure (key order may vary)
    toon_part = result[7:-8]  # Remove <chunk> and </chunk>
    assert "start_index: 0" in toon_part
    assert "end_index: 10" in toon_part
    assert "context: example" in toon_part
    assert "content: Hello world" in toon_part
    logger.success("  ✓ Test passed: Correctly wrapped TOON in XML tags")


def test_toonify_wrap_xml_no_attributes():
    """Verify XML tag format: XML wrapper should be plain <chunk> tag without attributes.

    When wrap_xml=True, the XML tag should be exactly "<chunk>" without any attributes.
    This distinguishes toonify from xmlify, which includes attributes in the XML tag.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_wrap_xml_no_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=True")
    logger.debug("  Verifying XML tag has no attributes (unlike xmlify)")

    result = toonify(chunk, wrap_xml=True)

    logger.debug(f"  Actual result: '{result}'")

    assert result.startswith("<chunk>")
    assert result.endswith("</chunk>")
    # XML tag should be exactly "<chunk>" without any attributes
    assert result[:7] == "<chunk>"
    assert (
        "start_index=" not in result[:20]
    )  # Attributes should be in TOON, not XML tag
    logger.success("  ✓ Test passed: XML tag correctly has no attributes")


def test_toonify_content_always_included():
    """Verify mandatory content field: content is always included even with empty attributes list.

    The content field (derived from chunk.text) should always be present in the TOON output,
    regardless of what attributes are specified or even if the attributes list is empty.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_content_always_included.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Empty attributes list: []")

    result = toonify(chunk, attributes=[])

    logger.debug(f"  Actual result: '{result}'")

    # Verify it matches manual encoding (only content)
    data = {"content": "Hello world"}
    expected_toon = encode(data)
    assert result == expected_toon
    logger.success(
        "  ✓ Test passed: Content always included even with empty attributes"
    )


def test_toonify_numeric_types():
    """Verify numeric type handling: correctly formats integer and numeric attribute values.

    When Chunk attributes contain numeric values (integers), they should be properly encoded
    in the TOON format and preserved in the output.
    """
    chunk = Chunk(text="Test", start_index=100, end_index=200, context="test")

    logger.info(f"[TEST] {test_toonify_numeric_types.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Numeric values: start_index=100, end_index=200")

    result = toonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Verify structure (key order may vary)
    assert "start_index: 100" in result
    assert "end_index: 200" in result
    assert "context: test" in result
    assert "content: Test" in result
    logger.success("  ✓ Test passed: Correctly handled numeric types")


def test_toonify_tuple_attributes():
    """Verify iterable support: accepts tuple (or any iterable) for attributes parameter.

    The attributes parameter should accept any iterable type (list, tuple, set, etc.),
    not just lists, demonstrating flexibility in the API.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_toonify_tuple_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Attributes as tuple: ('start_index', 'end_index')")

    result = toonify(chunk, attributes=("start_index", "end_index"))

    logger.debug(f"  Actual result: '{result}'")

    # Verify it matches manual encoding (key order may vary)
    data1 = {"start_index": 0, "end_index": 10, "content": "Hello world"}
    data2 = {"end_index": 10, "start_index": 0, "content": "Hello world"}
    expected_toon1 = encode(data1)
    expected_toon2 = encode(data2)
    assert result == expected_toon1 or result == expected_toon2
    logger.success("  ✓ Test passed: Correctly handled tuple as attributes parameter")
