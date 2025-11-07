from chonkie import Chunk
from chonkie_chunk_utils.formatters.jsonify import jsonify
import json
from loguru import logger


# ============================================================================
# Tests for jsonify
# ============================================================================


def test_jsonify_basic():
    """Verify basic functionality: converts Chunk to JSON string with default attributes.

    When jsonify is called with default parameters, it should produce a valid JSON string
    containing the default attributes (start_index, end_index, context) and the content field.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    expected = '{"start_index": 0, "end_index": 10, "context": "example", "content": "Hello world"}'

    logger.info(f"[TEST] {test_jsonify_basic.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug(f"  Expected result: '{expected}'")

    result = jsonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Parse JSON to verify it's valid
    parsed = json.loads(result)
    assert parsed["start_index"] == 0
    assert parsed["end_index"] == 10
    assert parsed["context"] == "example"
    assert parsed["content"] == "Hello world"
    # Note: JSON key order may vary due to set operations, so we verify structure instead
    assert set(parsed.keys()) == {"start_index", "end_index", "context", "content"}
    logger.success(
        "  ✓ Test passed: Correctly formatted chunk to JSON with default attributes"
    )


def test_jsonify_custom_attributes():
    """Verify custom attributes selection: allows specifying which attributes to include.

    When specific attributes are provided via the attributes parameter, only those attributes
    (plus the mandatory content field) should be included in the resulting JSON.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    expected = '{"start_index": 0, "end_index": 10, "content": "Hello world"}'

    logger.info(f"[TEST] {test_jsonify_custom_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Custom attributes: ['start_index', 'end_index']")
    logger.debug(f"  Expected result: '{expected}'")

    result = jsonify(chunk, attributes=["start_index", "end_index"])

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert "start_index" in parsed
    assert "end_index" in parsed
    assert "content" in parsed
    assert "context" not in parsed
    assert parsed["start_index"] == 0
    assert parsed["end_index"] == 10
    assert parsed["content"] == "Hello world"
    logger.success("  ✓ Test passed: Correctly formatted chunk with custom attributes")


def test_jsonify_single_attribute():
    """Verify single attribute selection: works correctly with only one attribute specified.

    When a single attribute is provided in the attributes list, the resulting JSON should
    contain only that attribute and the mandatory content field.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_jsonify_single_attribute.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Single attribute: ['start_index']")

    result = jsonify(chunk, attributes=["start_index"])

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert "start_index" in parsed
    assert "content" in parsed
    assert "end_index" not in parsed
    assert "context" not in parsed
    assert parsed["start_index"] == 0
    assert parsed["content"] == "Hello world"
    logger.success("  ✓ Test passed: Correctly formatted chunk with single attribute")


def test_jsonify_nonexistent_attributes():
    """Verify graceful handling of nonexistent attributes: filters out attributes that don't exist.

    When attributes list contains attribute names that don't exist in the Chunk, those
    attributes should be silently ignored and only existing attributes should be included.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10)

    logger.info(f"[TEST] {test_jsonify_nonexistent_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug(
        "  Attributes with nonexistent: ['start_index', 'end_index', 'context', 'nonexistent']"
    )

    result = jsonify(
        chunk, attributes=["start_index", "end_index", "context", "nonexistent"]
    )

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert "start_index" in parsed
    assert "end_index" in parsed
    assert "content" in parsed
    # context may be None if it exists in chunk but is None
    # nonexistent should not be in result
    assert "nonexistent" not in parsed
    logger.success("  ✓ Test passed: Correctly filtered out nonexistent attributes")


def test_jsonify_empty_text():
    """Verify handling of empty text content: correctly formats chunks with empty string text.

    When a Chunk has an empty text field, the resulting JSON should still be valid with
    an empty string value for the content field.
    """
    chunk = Chunk(text="", start_index=0, end_index=0, context="empty")
    expected = '{"start_index": 0, "end_index": 0, "context": "empty", "content": ""}'

    logger.info(f"[TEST] {test_jsonify_empty_text.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (empty)"
    )
    logger.debug(f"  Expected result: '{expected}'")

    result = jsonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert parsed["content"] == ""
    assert parsed["start_index"] == 0
    assert parsed["end_index"] == 0
    assert parsed["context"] == "empty"
    logger.success("  ✓ Test passed: Correctly handled empty text")


def test_jsonify_unicode():
    """Verify Unicode support: correctly handles non-ASCII characters in text and attributes.

    When Chunk contains Unicode characters (e.g., Korean, Chinese, emoji), the JSON output
    should properly encode them and be parseable back to the original Unicode strings.
    """
    chunk = Chunk(text="안녕하세요", start_index=0, end_index=5, context="한국어")

    logger.info(f"[TEST] {test_jsonify_unicode.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (unicode)"
    )
    logger.debug(f"  Context: '{chunk.context}' (unicode)")

    result = jsonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert parsed["content"] == "안녕하세요"
    assert parsed["context"] == "한국어"
    # JSON may escape unicode, so check parsed values instead
    assert parsed["content"] == chunk.text
    assert parsed["context"] == chunk.context
    logger.success("  ✓ Test passed: Correctly handled unicode text")


def test_jsonify_special_characters():
    """Verify special character handling: correctly escapes quotes, newlines, and tabs.

    When Chunk contains special characters like quotes, newlines, or tabs, the JSON output
    should properly escape them according to JSON standards and remain valid and parseable.
    """
    chunk = Chunk(
        text='Hello "world" with\nnewline\tand\ttab',
        start_index=0,
        end_index=30,
        context='test "quotes"',
    )

    logger.info(f"[TEST] {test_jsonify_special_characters.__name__}")
    logger.debug("  Input chunk: text contains quotes, newlines, tabs")
    logger.debug("  Context: contains quotes")

    result = jsonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Should be valid JSON despite special characters
    parsed = json.loads(result)
    assert "\n" in parsed["content"]
    assert "\t" in parsed["content"]
    assert '"' in parsed["content"]
    assert '"' in parsed["context"]
    logger.success("  ✓ Test passed: Correctly handled special characters in JSON")


def test_jsonify_wrap_xml_false():
    """Verify default behavior: returns plain JSON string without XML tags when wrap_xml is False.

    By default (wrap_xml=False), jsonify should return a pure JSON string without any
    XML wrapper tags, making it suitable for direct JSON parsing.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_jsonify_wrap_xml_false.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=False (default)")

    result = jsonify(chunk, wrap_xml=False)

    logger.debug(f"  Actual result: '{result}'")

    assert not result.startswith("<chunk>")
    assert not result.endswith("</chunk>")
    assert json.loads(result) is not None
    logger.success("  ✓ Test passed: Correctly returned JSON without XML wrapping")


def test_jsonify_wrap_xml_true():
    """Verify XML wrapping option: wraps JSON string in <chunk> tags when wrap_xml is True.

    When wrap_xml=True, the JSON string should be wrapped in <chunk>...</chunk> XML tags,
    but the XML tag itself should not contain any attributes (unlike xmlify).
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    logger.info(f"[TEST] {test_jsonify_wrap_xml_true.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=True")

    result = jsonify(chunk, wrap_xml=True)

    logger.debug(f"  Actual result: '{result}'")

    assert result.startswith("<chunk>")
    assert result.endswith("</chunk>")
    # Extract JSON part and verify it's valid
    json_part = result[7:-8]  # Remove <chunk> and </chunk>
    assert json.loads(json_part) is not None
    logger.success("  ✓ Test passed: Correctly wrapped JSON in XML tags")


def test_jsonify_wrap_xml_no_attributes():
    """Verify XML tag format: XML wrapper should be plain <chunk> tag without attributes.

    When wrap_xml=True, the XML tag should be exactly "<chunk>" without any attributes.
    This distinguishes jsonify from xmlify, which includes attributes in the XML tag.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_jsonify_wrap_xml_no_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  wrap_xml=True")
    logger.debug("  Verifying XML tag has no attributes (unlike xmlify)")

    result = jsonify(chunk, wrap_xml=True)

    logger.debug(f"  Actual result: '{result}'")

    assert result.startswith("<chunk>")
    assert result.endswith("</chunk>")
    # XML tag should be exactly "<chunk>" without any attributes
    assert result[:7] == "<chunk>"
    assert (
        "start_index=" not in result[:20]
    )  # Attributes should be in JSON, not XML tag
    logger.success("  ✓ Test passed: XML tag correctly has no attributes")


def test_jsonify_content_always_included():
    """Verify mandatory content field: content is always included even with empty attributes list.

    The content field (derived from chunk.text) should always be present in the JSON output,
    regardless of what attributes are specified or even if the attributes list is empty.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_jsonify_content_always_included.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Empty attributes list: []")

    result = jsonify(chunk, attributes=[])

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert "content" in parsed
    assert parsed["content"] == "Hello world"
    assert len(parsed) == 1  # Only content should be present
    logger.success(
        "  ✓ Test passed: Content always included even with empty attributes"
    )


def test_jsonify_numeric_types():
    """Verify numeric type preservation: correctly formats integer and numeric attribute values.

    When Chunk attributes contain numeric values (integers), they should be preserved as
    numbers in the JSON output, not converted to strings.
    """
    chunk = Chunk(text="Test", start_index=100, end_index=200, context="test")

    logger.info(f"[TEST] {test_jsonify_numeric_types.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Numeric values: start_index=100, end_index=200")

    result = jsonify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert isinstance(parsed["start_index"], int)
    assert isinstance(parsed["end_index"], int)
    assert parsed["start_index"] == 100
    assert parsed["end_index"] == 200
    logger.success("  ✓ Test passed: Correctly handled numeric types")


def test_jsonify_tuple_attributes():
    """Verify iterable support: accepts tuple (or any iterable) for attributes parameter.

    The attributes parameter should accept any iterable type (list, tuple, set, etc.),
    not just lists, demonstrating flexibility in the API.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_jsonify_tuple_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Attributes as tuple: ('start_index', 'end_index')")

    result = jsonify(chunk, attributes=("start_index", "end_index"))

    logger.debug(f"  Actual result: '{result}'")

    parsed = json.loads(result)
    assert "start_index" in parsed
    assert "end_index" in parsed
    assert "content" in parsed
    assert "context" not in parsed
    logger.success("  ✓ Test passed: Correctly handled tuple as attributes parameter")
