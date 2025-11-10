# chuk-tool-processor Improvements Needed

**Date**: 2025-01-09
**Based on**: Experience building chuk-acp-agent with full type safety

---

## Critical Issues

### 1. Missing Type Stubs (`py.typed`)

**Problem**: chuk-tool-processor doesn't have a `py.typed` marker file, so mypy cannot type-check code that uses it.

**Impact**:
- Consumers must use `ignore_missing_imports = true` in mypy config
- Loss of type safety across package boundaries
- No IDE autocomplete/type hints for the package

**Solution**:
```bash
# Add to package root
touch src/chuk_tool_processor/py.typed
```

**pyproject.toml update**:
```toml
[tool.hatch.build.targets.sdist]
include = [
    "src/chuk_tool_processor/py.typed",
]
```

**Example from chuk-acp-agent**:
We had to ignore chuk-tool-processor imports:
```toml
[[tool.mypy.overrides]]
module = [
    "chuk_tool_processor.*",
]
ignore_missing_imports = true
```

This is a **regression in type safety** compared to chuk-acp which now has proper type stubs.

---

## Type Safety Issues

### 2. Missing Type Annotations

**Problem**: Based on our testing, several areas lack proper type annotations:

**Areas needing improvement**:
1. **ToolCall model** - We had to handle import errors because it wasn't clear what the API was
2. **Tool registry** - `list_tools()` return type unclear
3. **Processor execute()** - Return type not properly typed
4. **Stream manager** - No type hints for cleanup() and other methods

**Evidence from our code**:
```python
# We had to add these fallbacks due to unclear types
try:
    from chuk_tool_processor.models.tool_call import ToolCall
except ImportError:
    # Fallback handling...
```

**Solution**:
- Add comprehensive type hints to all public APIs
- Use `typing.Protocol` for interfaces
- Add `from __future__ import annotations` for forward references
- Run mypy with `--strict` mode

---

### 3. Import Error Handling

**Problem**: Package doesn't gracefully handle missing optional dependencies.

**Evidence from our tests**:
```python
# We had to add extensive import error tests
@pytest.mark.asyncio
async def test_call_import_error_toolcall(self):
    with patch.dict('sys.modules', {'chuk_tool_processor.models.tool_call': None}):
        with pytest.raises(ImportError, match="chuk-tool-processor"):
            await invoker.call("test_tool")
```

**Solution**:
1. Add better error messages for missing dependencies
2. Document which imports are required vs optional
3. Consider lazy imports for heavy dependencies
4. Add `ImportError` handling with helpful installation instructions

---

## API Design Issues

### 4. Unified API (Confusing Method Names)

**Problem**: Unclear which method to use - `process()` vs `execute()` vs something else?

**Evidence from DX work**:
```python
# Which one to use?
results = await processor.process(tool_call)  # Doesn't work!
results = await processor.execute([tool_call])  # This works
```

**Proposed Solution**:
```python
# Single, clear API
result = await processor.call("tool_name", arg1="value")
results = await processor.call_many([tool1, tool2, tool3])
```

**Implementation**:
- Deprecate `process()` or make it an alias
- Rename `execute()` to `call()` for single calls
- Add `call_many()` for batch calls
- Clear naming that matches common patterns

---

### 5. Inconsistent Return Types

**Problem**: `ToolProcessor.execute()` returns results that aren't consistently structured.

**Evidence**: We had to add this fallback:
```python
results = await self._processor.execute([tool_call])

# Handle case where no results returned
if not results:
    raise ToolExecutionError("Tool execution returned no results")

# Sometimes has .result, sometimes .content
data = result.result if hasattr(result, 'result') else result.content
```

**Proposed Solution**:
```python
# Consistent ToolResult object
result = await processor.call("echo", message="hi")
result.value  # The actual result (always present)
result.error  # None or error message
result.metadata  # Timing, etc.
```

**Implementation**:
- Always return a list (even if empty, never None)
- Standardize on single result format (Pydantic model)
- Use `.value` for the actual result
- Always include `.error` and `.metadata`
- Document the exact structure of return values

---

### 6. Registry API Clarity

**Problem**: `ToolRegistryProvider.get_registry()` and `registry.list_tools()` have unclear types and inconsistent async behavior.

**Evidence from our code**:
```python
# We had to add type annotation to make mypy happy
registry = ToolRegistryProvider.get_registry()  # Sometimes a coroutine?
tools: dict[str, Any] = registry.list_tools()
return tools
```

**Proposed Solution**:
```python
# Access via processor directly
tools = processor.list_tools()
schema = processor.get_tool_schema("echo")
```

**Implementation**:
1. Make registry access consistent (always sync or always async)
2. Expose registry methods on processor
3. Cache registry instance
4. Define clear return types:
   ```python
   class ToolRegistry:
       def list_tools(self) -> dict[str, ToolMetadata]: ...
   ```
5. Use TypedDict or Pydantic models for tool metadata

---

### 7. Missing Cleanup API

**Problem**: No clear way to clean up resources. `StreamManager.cleanup()` doesn't exist or has wrong name.

**Evidence from DX work**:
```python
await stream_manager.cleanup()  # AttributeError!
```

**Proposed Solution**:
```python
# Consistent cleanup
await processor.close()

# Or context manager
async with ToolProcessor(config) as processor:
    result = await processor.call("echo", message="hi")
# Auto-cleanup
```

**Implementation**:
- Add `.close()` method to processor
- Implement `__aenter__` and `__aexit__` for context manager
- Fix StreamManager cleanup method
- Document cleanup requirements clearly

---

### 8. Stdio Command Validation

**Problem**: Easy to forget "stdio" argument in MCP server commands, leading to cryptic errors.

**Evidence from DX work**:
```python
# Need to know about stdio subcommand
config = {
    "echo": {
        "command": "uvx",
        "args": ["chuk-mcp-echo", "stdio"]  # Easy to forget "stdio"
    }
}
```

**Proposed Solution**:
```python
# Option 1: Auto-detect transport
config = {
    "echo": {
        "command": "uvx chuk-mcp-echo",  # Auto-adds stdio
        "transport": "stdio"  # Explicit
    }
}

# Option 2: Validation with helpful errors
# Error: Server 'echo' command must include 'stdio' subcommand for STDIO transport
# Suggestion: Add 'stdio' to args: ["chuk-mcp-echo", "stdio"]
```

**Implementation**:
- Add transport detection/validation
- Provide helpful error messages
- Consider auto-adding stdio for known servers
- Document transport requirements

---

## Testing & Quality Issues

### 9. Missing Test Coverage Reports

**Problem**: No visibility into test coverage for chuk-tool-processor.

**Recommendation**:
```toml
# Add to pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src/chuk_tool_processor --cov-report=html --cov-report=term"

[tool.coverage.run]
branch = true
source = ["src/chuk_tool_processor"]

[tool.coverage.report]
fail_under = 90
precision = 2
show_missing = true
```

**Add Make targets** (like we have in chuk-acp-agent):
```makefile
test-cov:
	pytest --cov=src/chuk_tool_processor --cov-report=html --cov-report=term --cov-fail-under=90

lint:
	ruff check .
	ruff format --check .

typecheck:
	mypy src/chuk_tool_processor

check: lint typecheck test-cov
	@echo "All checks completed."
```

---

### 10. Missing Type Checking in CI

**Problem**: No mypy validation in development workflow.

**Recommendation**:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict = true

[[tool.mypy.overrides]]
module = ["chuk_mcp.*"]
ignore_missing_imports = true
```

---

## Documentation Issues

### 11. Missing API Documentation

**Problems identified**:
1. No clear examples of `ToolProcessor` usage
2. No documentation of `ToolCall` structure
3. No guide on how to extend the registry
4. No explanation of MCP setup parameters

**Recommendation**: Add comprehensive docstrings with examples:

```python
class ToolProcessor:
    """Process and execute tool calls from LLM agents.

    Examples:
        Basic usage:

        >>> processor = ToolProcessor()
        >>> tool_call = ToolCall(tool="echo", arguments={"message": "hello"})
        >>> results = await processor.execute([tool_call])
        >>> print(results[0].text)
        'hello'

        With MCP servers:

        >>> config = {"mcpServers": {"echo": {...}}}
        >>> processor, stream_manager = await setup_mcp_stdio(
        ...     config_file="config.json",
        ...     servers=["echo"]
        ... )
        >>> # Use processor...
        >>> await stream_manager.cleanup()

    Args:
        config: Optional MCP configuration
        timeout: Default timeout for tool execution

    Raises:
        ToolExecutionError: If tool execution fails
        ImportError: If required dependencies not installed
    """
```

---

### 12. Missing Type Documentation

**Problem**: No `py.typed` means users don't know what types to expect.

**Recommendation**:
1. Add `py.typed` marker (see #1)
2. Add a TYPE_CHECKING section to exports:
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from .models.tool_call import ToolCall
       from .registry import ToolRegistry

   __all__ = ["ToolProcessor", "ToolCall", "ToolRegistry", ...]
   ```

---

## Consistency Issues

### 13. Different Pattern from chuk-acp

**Problem**: chuk-acp uses clean patterns (Transport.get_streams(), proper types) but chuk-tool-processor doesn't follow same standards.

**Recommendations**:
1. **Use consistent naming**:
   - chuk-acp: `TerminalInfo` has `.id`
   - chuk-tool-processor should follow same patterns

2. **Use Pydantic consistently**:
   - chuk-acp uses Pydantic models throughout
   - chuk-tool-processor should do the same for all data structures

3. **Follow same error handling pattern**:
   - chuk-acp raises clear exceptions with helpful messages
   - chuk-tool-processor should match

---

## Priority Recommendations

### Critical Priority (Blocking Issues)
1. **Add `py.typed` marker file** (#1) - Required for type checking
2. **Fix cleanup API** (#7) - StreamManager.cleanup() doesn't exist
3. **Consistent return types** (#5) - Never return None, always return list
4. **Registry API consistency** (#6) - Sometimes async, sometimes sync

### High Priority (Major DX Issues)
5. **Add comprehensive type annotations** (#2) - Enable strict mypy
6. **Unified API naming** (#4) - Call() vs execute() vs process()
7. **Add mypy to CI/development workflow** (#10) - Catch type errors early
8. **Stdio command validation** (#8) - Helpful errors for missing "stdio"

### Medium Priority (Quality Improvements)
9. **Add test coverage reporting** (#9) - 90% target
10. **Improve error messages** (#3) - Better ImportError handling
11. **Add API documentation** (#11) - Examples and docstrings
12. **Type documentation** (#12) - TYPE_CHECKING exports

### Low Priority (Nice to Have)
13. **Align naming conventions with chuk-acp** (#13) - Consistency across packages
14. **Add more integration tests** - Increase confidence
15. **Create migration guide** - Help users upgrade

---

## Implementation Checklist

```bash
# Step 1: Add type stubs
touch src/chuk_tool_processor/py.typed
# Update pyproject.toml to include it

# Step 2: Add mypy config
# Add [tool.mypy] section to pyproject.toml

# Step 3: Run mypy and fix errors
mypy src/chuk_tool_processor --strict
# Fix all type errors

# Step 4: Add test coverage
# Update pyproject.toml with coverage config
pytest --cov=src/chuk_tool_processor --cov-report=html

# Step 5: Add Makefile targets
# Create Makefile with check, lint, typecheck targets

# Step 6: Update CI
# Add mypy and coverage checks to CI pipeline
```

---

## Breaking Changes to Consider

If doing a major version bump, consider these breaking changes for better DX:

### API Simplification
1. **Rename `execute()` → `call()`** - More intuitive naming
   ```python
   # Old
   results = await processor.execute([tool_call])

   # New
   result = await processor.call("tool_name", **kwargs)
   results = await processor.call_many([...])
   ```

2. **Standardize result format**:
   ```python
   # Always return ToolResult Pydantic model
   result.value  # The actual result
   result.error  # None or error message
   result.metadata  # Timing, etc.
   ```

3. **Registry access via processor**:
   ```python
   # Old
   registry = ToolRegistryProvider.get_registry()
   tools = registry.list_tools()

   # New
   tools = processor.list_tools()
   ```

### Cleanup & Context Managers
4. **Add async context manager support**:
   ```python
   async with ToolProcessor(config) as processor:
       result = await processor.call("echo", message="hi")
   # Auto cleanup
   ```

5. **Consistent cleanup API**:
   ```python
   # Add processor.close() method
   await processor.close()
   ```

### Type Safety
6. **Rename `ToolCall` → `ToolInvocation`** (more descriptive)
7. **Make all results Pydantic models** (no raw dicts)
8. **Never return None** - Always return list (even if empty)

### Other Considerations
9. **Split registry into separate package** (if it grows significantly)
10. **Transport validation** - Auto-detect or validate stdio requirement

---

## Examples of Good Patterns from chuk-acp

These patterns should be adopted:

### 1. Clean Type Definitions
```python
# From chuk-acp
PlanEntryStatus = Literal["pending", "in_progress", "completed"]
PlanEntryPriority = Literal["high", "medium", "low"]
```

### 2. Proper Pydantic Models
```python
# From chuk-acp
class TerminalInfo(AcpPydanticBase):
    id: str
    command: str
    args: Optional[List[str]] = None
```

### 3. Clear Method Signatures
```python
# From chuk-acp
async def send_terminal_create(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    command: str,
    args: Optional[List[str]] = None,
    *,
    timeout: float = 60.0,
) -> TerminalInfo:
    """Create a terminal session.

    Args:
        read_stream: Stream to receive messages
        write_stream: Stream to send messages
        command: Command to execute
        args: Command arguments
        timeout: Request timeout in seconds

    Returns:
        TerminalInfo with session ID

    Raises:
        Exception: If terminal creation fails
    """
```

---

## Before/After Comparison

### Example 1: Basic Tool Execution

**Current (Confusing)**:
```python
from chuk_tool_processor import ToolProcessor
from chuk_tool_processor.models.tool_call import ToolCall

processor = ToolProcessor()
tool_call = ToolCall(tool="echo", arguments={"message": "hello"})
results = await processor.execute([tool_call])

# Results might be None!
if not results:
    raise Exception("No results")

# Extract value - inconsistent structure
result = results[0]
value = result.result if hasattr(result, 'result') else result.content
```

**Proposed (Clean)**:
```python
from chuk_tool_processor import ToolProcessor

async with ToolProcessor() as processor:
    result = await processor.call("echo", message="hello")
    print(result.value)  # Clean access
    print(result.error)  # None if successful
```

### Example 2: Tool Discovery

**Current (Confusing)**:
```python
from chuk_tool_processor.registry import ToolRegistryProvider

# Sometimes async, sometimes not?
registry = ToolRegistryProvider.get_registry()
tools = registry.list_tools()  # What type is this?
```

**Proposed (Clean)**:
```python
from chuk_tool_processor import ToolProcessor

processor = ToolProcessor()
tools = processor.list_tools()  # Returns list[ToolMetadata]
for tool in tools:
    print(f"{tool.name}: {tool.description}")
```

### Example 3: Cleanup

**Current (Broken)**:
```python
from chuk_tool_processor.mcp import setup_mcp_stdio

processor, stream_manager = await setup_mcp_stdio(config_file="config.json")
# ... use processor ...
await stream_manager.cleanup()  # AttributeError!
```

**Proposed (Clean)**:
```python
from chuk_tool_processor import ToolProcessor

# Option 1: Context manager
async with ToolProcessor(config_file="config.json") as processor:
    result = await processor.call("echo", message="hi")
# Auto-cleanup

# Option 2: Explicit cleanup
processor = ToolProcessor(config_file="config.json")
try:
    result = await processor.call("echo", message="hi")
finally:
    await processor.close()
```

---

## Conclusion

This document identifies **13 critical improvements** for chuk-tool-processor based on real-world experience building chuk-acp-agent with full type safety and comprehensive testing.

### Impact Summary

Implementing these improvements will make chuk-tool-processor:
- ✅ **Type-safe** - Full mypy support with py.typed marker
- ✅ **Intuitive** - Clear API naming (call() vs execute())
- ✅ **Reliable** - Consistent return types, never None
- ✅ **Easy to use** - Context managers, clean result access
- ✅ **Well-documented** - Examples, docstrings, type hints
- ✅ **Well-tested** - 90%+ coverage with CI checks
- ✅ **Maintainable** - Follows chuk-acp patterns

### Quick Wins

The **biggest quick wins** that can be done immediately:

1. **Add `py.typed` marker** - Single empty file unlocks type checking for all users!
2. **Fix cleanup API** - Add processor.close() method
3. **Never return None** - Always return list (even if empty)
4. **Add mypy to CI** - Catch type errors before release

### Developer Experience Impact

**Current state**: Confusing API, inconsistent results, no type checking, broken cleanup
**After improvements**: Clean API, typed results, full IDE support, reliable cleanup

**Estimated DX improvement**: 3-5x easier to use based on chuk-acp-agent experience

---

## References

### Related Documentation
- **DX_IMPROVEMENTS.md** - Original planned improvements for both packages
- **DX_IMPROVEMENTS_COMPLETED.md** - Completed chuk-acp-agent improvements and learnings

### Code Examples
- **chuk-acp** - Good example of proper type stubs, Pydantic models, and clean APIs
- **chuk-acp-agent** - Shows how to properly consume typed packages and wrap tool-processor

### Standards & Tools
- **PEP 561**: Distributing and Packaging Type Information
- **mypy documentation**: https://mypy.readthedocs.io/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **ruff**: https://docs.astral.sh/ruff/

---

## Next Steps

1. **Review this document** with the team
2. **Create GitHub issues** for each improvement (numbered 1-13)
3. **Prioritize** based on Critical/High/Medium/Low categories
4. **Assign to sprint** - Start with Critical priority items
5. **Consider major version bump** for breaking API changes
6. **Plan migration guide** for users upgrading

**Estimated effort**:
- Critical items: 1-2 days
- High priority: 3-5 days
- Medium priority: 3-5 days
- Low priority: 2-3 days
- **Total: ~2-3 weeks** for full implementation
