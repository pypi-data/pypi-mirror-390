from chonkie import Chunk
from chonkie_chunk_utils.formatters.xmlify import xmlify
from loguru import logger


# ============================================================================
# Tests for xmlify
# ============================================================================


def test_xmlify_basic():
    """Verify basic functionality: converts Chunk to XML string with default attributes.

    When xmlify is called with default parameters, it should produce a valid XML string
    with default attributes (start_index, end_index, context) as XML attributes and
    the chunk text as the tag content.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    logger.info(f"[TEST] {test_xmlify_basic.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Note: XML attribute order may vary due to set operations
    assert result.startswith("<chunk")
    assert result.endswith("</chunk>")
    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    assert 'context="example"' in result
    assert "Hello world" in result
    logger.success(
        "  ✓ Test passed: Correctly formatted chunk to XML with default attributes"
    )


def test_xmlify_custom_attributes():
    """Verify custom attributes selection: allows specifying which attributes to include.

    When specific attributes are provided via the attributes parameter, only those attributes
    should be included as XML attributes in the opening tag.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    logger.info(f"[TEST] {test_xmlify_custom_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Custom attributes: ['start_index', 'end_index']")

    result = xmlify(chunk, attributes=["start_index", "end_index"])

    logger.debug(f"  Actual result: '{result}'")

    # Note: XML attribute order may vary due to set operations
    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    assert "context=" not in result
    assert "Hello world" in result
    logger.success("  ✓ Test passed: Correctly formatted chunk with custom attributes")


def test_xmlify_single_attribute():
    """Verify single attribute selection: works correctly with only one attribute specified.

    When a single attribute is provided in the attributes list, the resulting XML should
    contain only that attribute in the opening tag.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_xmlify_single_attribute.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}', context='{chunk.context}'"
    )
    logger.debug("  Single attribute: ['start_index']")

    result = xmlify(chunk, attributes=["start_index"])

    logger.debug(f"  Actual result: '{result}'")

    assert 'start_index="0"' in result
    assert "Hello world" in result
    assert "end_index=" not in result
    assert "context=" not in result
    logger.success("  ✓ Test passed: Correctly formatted chunk with single attribute")


def test_xmlify_nonexistent_attributes():
    """Verify graceful handling of nonexistent attributes: filters out attributes that don't exist.

    When attributes list contains attribute names that don't exist in the Chunk, those
    attributes should be silently ignored and only existing attributes should be included.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10)

    logger.info(f"[TEST] {test_xmlify_nonexistent_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug(
        "  Attributes with nonexistent: ['start_index', 'end_index', 'context', 'nonexistent']"
    )

    result = xmlify(
        chunk, attributes=["start_index", "end_index", "context", "nonexistent"]
    )

    logger.debug(f"  Actual result: '{result}'")

    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    assert "Hello world" in result
    # context may be None if it exists in chunk but is None
    assert "nonexistent=" not in result
    logger.success("  ✓ Test passed: Correctly filtered out nonexistent attributes")


def test_xmlify_empty_text():
    """Verify handling of empty text content: correctly formats chunks with empty string text.

    When a Chunk has an empty text field, the resulting XML should still be valid with
    an empty tag body (between > and <).
    """
    chunk = Chunk(text="", start_index=0, end_index=0, context="empty")
    logger.info(f"[TEST] {test_xmlify_empty_text.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (empty)"
    )

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Note: XML attribute order may vary due to set operations
    assert result.endswith("></chunk>")
    logger.success("  ✓ Test passed: Correctly handled empty text")


def test_xmlify_unicode():
    """Verify Unicode support: correctly handles non-ASCII characters in text and attributes.

    When Chunk contains Unicode characters (e.g., Korean, Chinese, emoji), the XML output
    should properly encode them and preserve the original Unicode strings in both attributes
    and tag content.
    """
    chunk = Chunk(text="안녕하세요", start_index=0, end_index=5, context="한국어")

    logger.info(f"[TEST] {test_xmlify_unicode.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}' (unicode)"
    )
    logger.debug(f"  Context: '{chunk.context}' (unicode)")

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    assert "안녕하세요" in result
    assert 'context="한국어"' in result
    assert result.startswith("<chunk")
    assert result.endswith("</chunk>")
    logger.success("  ✓ Test passed: Correctly handled unicode text")


def test_xmlify_special_characters():
    """Verify special character handling: correctly processes quotes, newlines, and tabs.

    When Chunk contains special characters like quotes, newlines, or tabs, the XML output
    should handle them appropriately (may be escaped in attributes or preserved in content).
    """
    chunk = Chunk(
        text='Hello "world" with\nnewline\tand\ttab',
        start_index=0,
        end_index=30,
        context='test "quotes"',
    )

    logger.info(f"[TEST] {test_xmlify_special_characters.__name__}")
    logger.debug("  Input chunk: text contains quotes, newlines, tabs")
    logger.debug("  Context: contains quotes")

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # XML attributes should escape quotes (implementation may vary)
    assert "context=" in result
    # Content should be in tag body
    assert "Hello" in result
    assert result.startswith("<chunk")
    assert result.endswith("</chunk>")
    logger.success("  ✓ Test passed: Correctly handled special characters")


def test_xmlify_content_in_tag():
    """Verify content placement: chunk text appears as tag body content, not as an attribute.

    The chunk text should be placed between the opening and closing tags (as tag content),
    not as an XML attribute. This is the key difference from how attributes are handled.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_xmlify_content_in_tag.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Verifying content is in tag body, not as attribute")

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    assert "Hello world" in result
    # Content should be between > and <
    assert ">Hello world<" in result
    # Content should not be an attribute
    assert "content=" not in result
    logger.success("  ✓ Test passed: Content correctly included as tag text")


def test_xmlify_attributes_as_xml_attributes():
    """Verify attribute placement: specified attributes appear as XML attributes in the opening tag.

    Attributes specified in the attributes parameter should be included as XML attributes
    in the opening <chunk> tag, with their values properly quoted.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_xmlify_attributes_as_xml_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Verifying attributes are XML attributes in tag")

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    # Attributes should be in the opening tag
    assert result.startswith("<chunk")
    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    assert 'context="example"' in result
    # Attributes should come before the closing >
    tag_end = result.find(">")
    assert tag_end > 0
    assert 'start_index="0"' in result[:tag_end]
    logger.success("  ✓ Test passed: Attributes correctly included as XML attributes")


def test_xmlify_empty_attributes_list():
    """Verify empty attributes handling: produces valid XML even when no attributes are specified.

    When an empty attributes list is provided, the XML should still be valid with an empty
    opening tag (no attributes), containing only the chunk text as tag content.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")
    logger.info(f"[TEST] {test_xmlify_empty_attributes_list.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Empty attributes list: []")

    result = xmlify(chunk, attributes=[])

    logger.debug(f"  Actual result: '{result}'")

    expected = "<chunk >Hello world</chunk>"
    assert result == expected
    assert "Hello world" in result
    assert "start_index=" not in result
    assert "end_index=" not in result
    assert "context=" not in result
    logger.success("  ✓ Test passed: Correctly handled empty attributes list")


def test_xmlify_all_nonexistent_attributes():
    """Verify edge case: handles situation when all requested attributes don't exist.

    When all attributes in the attributes list don't exist in the Chunk (or are None),
    the XML should still be valid with an empty opening tag, containing only the chunk text.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10)
    logger.info(f"[TEST] {test_xmlify_all_nonexistent_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug(
        "  All nonexistent attributes: ['context', 'nonexistent1', 'nonexistent2']"
    )

    result = xmlify(chunk, attributes=["context", "nonexistent1", "nonexistent2"])

    logger.debug(f"  Actual result: '{result}'")

    assert "Hello world" in result
    # context may be None if it exists in chunk but is None
    # Check that it's either not present or is None
    if "context=" in result:
        assert (
            'context="None"' in result
            or "context='None'" in result
            or "context=null" in result.lower()
        )
    assert "nonexistent1=" not in result
    assert "nonexistent2=" not in result
    logger.success("  ✓ Test passed: Correctly handled all nonexistent attributes")


def test_xmlify_numeric_types():
    """Verify numeric type handling: correctly formats integer and numeric attribute values.

    When Chunk attributes contain numeric values (integers), they should be properly converted
    to strings and included as quoted XML attribute values.
    """
    chunk = Chunk(text="Test", start_index=100, end_index=200, context="test")

    logger.info(f"[TEST] {test_xmlify_numeric_types.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Numeric values: start_index=100, end_index=200")

    result = xmlify(chunk)

    logger.debug(f"  Actual result: '{result}'")

    assert 'start_index="100"' in result
    assert 'end_index="200"' in result
    assert "Test" in result
    logger.success("  ✓ Test passed: Correctly handled numeric types")


def test_xmlify_tuple_attributes():
    """Verify iterable support: accepts tuple (or any iterable) for attributes parameter.

    The attributes parameter should accept any iterable type (list, tuple, set, etc.),
    not just lists, demonstrating flexibility in the API.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_xmlify_tuple_attributes.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Attributes as tuple: ('start_index', 'end_index')")

    result = xmlify(chunk, attributes=("start_index", "end_index"))

    logger.debug(f"  Actual result: '{result}'")

    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    assert "Hello world" in result
    assert "context=" not in result
    logger.success("  ✓ Test passed: Correctly handled tuple as attributes parameter")


def test_xmlify_attributes_order():
    """Verify attribute order handling: attributes may appear in different orders due to set operations.

    Since set intersection is used internally, attribute order in the XML may vary, but
    all specified attributes should be present and the XML should remain valid.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10, context="example")

    logger.info(f"[TEST] {test_xmlify_attributes_order.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  Testing multiple calls produce consistent order")

    result1 = xmlify(chunk, attributes=["context", "start_index", "end_index"])
    result2 = xmlify(chunk, attributes=["end_index", "context", "start_index"])

    logger.debug(f"  Result 1: '{result1}'")
    logger.debug(f"  Result 2: '{result2}'")

    # Both should contain all attributes
    assert 'start_index="0"' in result1
    assert 'end_index="10"' in result1
    assert 'context="example"' in result1
    assert 'start_index="0"' in result2
    assert 'end_index="10"' in result2
    assert 'context="example"' in result2
    # Order might differ due to set operations, but both should be valid XML
    assert result1.startswith("<chunk")
    assert result2.startswith("<chunk")
    logger.success(
        "  ✓ Test passed: XML attributes correctly formatted (order may vary)"
    )


def test_xmlify_no_context():
    """Verify missing attribute handling: gracefully handles Chunks without context attribute.

    When a Chunk doesn't have a context attribute (or it's None), and context is requested
    in the attributes list, it should be handled gracefully without errors.
    """
    chunk = Chunk(text="Hello world", start_index=0, end_index=10)
    logger.info(f"[TEST] {test_xmlify_no_context.__name__}")
    logger.debug(
        f"  Input chunk: start={chunk.start_index}, end={chunk.end_index}, text='{chunk.text}'"
    )
    logger.debug("  No context attribute")

    result = xmlify(chunk, attributes=["start_index", "end_index", "context"])

    logger.debug(f"  Actual result: '{result}'")

    # Note: XML attribute order may vary due to set operations
    assert 'start_index="0"' in result
    assert 'end_index="10"' in result
    # context may be None if it exists in chunk but is None
    if "context=" in result:
        assert (
            'context="None"' in result
            or "context='None'" in result
            or "context=null" in result.lower()
        )
    assert "Hello world" in result
    logger.success("  ✓ Test passed: Correctly handled missing context attribute")
