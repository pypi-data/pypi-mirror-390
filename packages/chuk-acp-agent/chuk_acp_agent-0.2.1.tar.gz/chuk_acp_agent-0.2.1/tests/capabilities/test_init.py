"""Tests for capabilities package __init__."""


def test_imports():
    """Test that capabilities package exports expected classes."""
    from chuk_acp_agent.capabilities import CommandResult, FileSystem, Terminal

    # Verify classes are imported
    assert FileSystem is not None
    assert Terminal is not None
    assert CommandResult is not None

    # Verify __all__ is correct
    from chuk_acp_agent import capabilities

    assert "FileSystem" in capabilities.__all__
    assert "Terminal" in capabilities.__all__
    assert "CommandResult" in capabilities.__all__
