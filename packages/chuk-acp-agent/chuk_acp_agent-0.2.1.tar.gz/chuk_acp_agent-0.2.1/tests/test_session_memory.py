"""
Tests for session memory.
"""

from chuk_acp_agent.agent.session import SessionMemory


def test_set_and_get():
    """Test basic set/get operations."""
    memory = SessionMemory()

    memory.set("key1", "value1")
    assert memory.get("key1") == "value1"


def test_get_default():
    """Test get with default value."""
    memory = SessionMemory()

    assert memory.get("missing", default="default") == "default"
    assert memory.get("missing") is None


def test_delete():
    """Test delete operation."""
    memory = SessionMemory()

    memory.set("key1", "value1")
    memory.delete("key1")
    assert memory.get("key1") is None


def test_delete_missing():
    """Test deleting non-existent key (should not raise)."""
    memory = SessionMemory()
    memory.delete("missing")  # Should not raise


def test_clear():
    """Test clear operation."""
    memory = SessionMemory()

    memory.set("key1", "value1")
    memory.set("key2", "value2")
    memory.clear()

    assert memory.get("key1") is None
    assert memory.get("key2") is None


def test_keys():
    """Test keys listing."""
    memory = SessionMemory()

    memory.set("key1", "value1")
    memory.set("key2", "value2")

    keys = memory.keys()
    assert len(keys) == 2
    assert "key1" in keys
    assert "key2" in keys


def test_has():
    """Test has operation."""
    memory = SessionMemory()

    memory.set("key1", "value1")

    assert memory.has("key1") is True
    assert memory.has("missing") is False


def test_complex_values():
    """Test storing complex values (dict, list)."""
    memory = SessionMemory()

    memory.set("dict", {"a": 1, "b": 2})
    memory.set("list", [1, 2, 3])

    assert memory.get("dict") == {"a": 1, "b": 2}
    assert memory.get("list") == [1, 2, 3]
