<!-- 07797365-cdc6-497b-888b-8b695b5fff0e 549ae982-b920-4b4b-89bf-0ce2689c1cbe -->
# Remove Docstrings from Charlie Project

## Overview

This plan outlines the removal of all docstrings that only describe WHAT the code does. Based on analysis of the codebase, all current docstrings fall into this category - none explain WHY the code was created.

## Files to Modify

### Source Files (11 files)

1. **Module-level docstrings** (11 files)

- `src/charlie/__init__.py`
- `src/charlie/mcp.py`
- `src/charlie/rules.py`
- `src/charlie/agents/__init__.py`
- `src/charlie/agents/claude.py`
- `src/charlie/agents/copilot.py`
- `src/charlie/agents/cursor.py`
- `src/charlie/agents/gemini.py`
- `src/charlie/agents/qwen.py`
- `src/charlie/agents/registry.py`
- `tests/__init__.py`

2. **Class-level docstrings** (5 classes in agent files)

- `ClaudeAdapter` in `claude.py`
- `CopilotAdapter` in `copilot.py`
- `CursorAdapter` in `cursor.py`
- `GeminiAdapter` in `gemini.py`
- `QwenAdapter` in `qwen.py`

3. **Function-level docstrings** (18 functions)

- `mcp.py`: 3 functions (`_command_to_tool_schema`, `_server_to_mcp_config`, `generate_mcp_config`)
- `rules.py`: 8 functions (all private helpers and generators)
- `registry.py`: 2 functions (`get_agent_spec`, `list_supported_agents`)
- Agent adapters: 5 `generate_command` methods

4. **Test docstrings**

- Check all test files for any docstrings

## Execution Plan

- [ ] Remove module-level docstrings from main source files
- [ ] Remove module-level docstrings from agent files  
- [ ] Remove class-level docstrings from all adapter classes
- [ ] Remove function-level docstrings from `mcp.py`
- [ ] Remove function-level docstrings from `rules.py`
- [ ] Remove function-level docstrings from `registry.py`
- [ ] Remove function-level docstrings from agent adapter methods
- [ ] Remove test file docstrings
- [ ] Verify no linter errors were introduced
- [ ] Run tests to ensure functionality unchanged

## Notes

All docstrings found describe only WHAT the code does (e.g., "MCP server configuration generator", "Convert command to MCP tool schema format"). None explain WHY decisions were made or provide context about the reasoning behind the implementation. Therefore, all should be removed per the criteria.

### To-dos

- [ ] Remove module-level docstrings from all Python files
- [ ] Remove class-level docstrings from adapter classes
- [ ] Remove function-level docstrings from all modules
- [ ] Remove docstrings from test files
- [ ] Run tests and verify no linter errors