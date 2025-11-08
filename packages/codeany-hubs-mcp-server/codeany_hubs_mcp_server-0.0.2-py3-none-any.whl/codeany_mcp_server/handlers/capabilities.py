"""Tool discovery helpers for MCP clients."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any, Dict, List, Tuple

from ..auth_guard import MCPAuthorizationGuard
from ..client_factory import ClientFactory
from ..config import MCPServerConfig
from ..router import Router
from ..logging_config import get_logger
from ..types import ConsentPrompt

_RAW_TOOLS: List[Tuple[str, str]] = [
    (
        "hubs.list_mine",
        "List hubs owned by the authenticated user.\nExample args: {}",
    ),
    (
        "hubs.detail",
        "Fetch detailed metadata for a single hub.\nExample args: {\"hub\": \"awesome-hub\"}",
    ),
    (
        "tasks.create",
        "Create a new task within a hub (payload mirrors SDK client).\nExample args: {\"hub\": \"awesome-hub\", \"name\": \"New Task\", \"confirm\": true}",
    ),
    (
        "tasks.list",
        "List tasks within a hub with optional filters.\nExample args: {\"hub\": \"awesome-hub\", \"page\": 1, \"filters\": {\"query\": \"dp\"}}",
    ),
    (
        "tasks.delete",
        "Delete a task (requires confirmation unless `confirm=true`).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.rename",
        "Rename an existing task.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"name\": \"new-title\", \"confirm\": true}",
    ),
    (
        "tasks.toggle_visibility",
        "Toggle task visibility.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"confirm\": true}",
    ),
    (
        "tasks.get_settings",
        "Retrieve task settings (limits, IO, statements metadata).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.type.get",
        "Fetch the current task type metadata (batch/mcq/etc.).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.type.update",
        "Update the task type (batch/mcq/etc.).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"payload\": {\"type\": \"mcq\"}, \"confirm\": true}",
    ),
    (
        "tasks.limits.get",
        "Retrieve execution limits (time/memory).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.limits.update",
        "Update execution limits (milliseconds / megabytes).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"time_limit\": 2000, \"memory_limit\": 256, \"confirm\": true}",
    ),
    (
        "tasks.statements.get",
        "Retrieve statements for a task (optionally by language).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"language\": \"en\"}",
    ),
    (
        "tasks.statements.list",
        "List available statement languages.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.statements.create_lang",
        "Create a new statement language payload.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"language\": \"en\", \"content\": {...}, \"confirm\": true}",
    ),
    (
        "tasks.statements.delete_lang",
        "Delete statement content for a locale.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"language\": \"en\", \"confirm\": true}",
    ),
    (
        "tasks.statements.update",
        "Update a specific statement by ID (SDK `update_statement`).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"statement_id\": 7, \"payload\": {\"title\": \"Updated\"}, \"confirm\": true}",
    ),
    (
        "tasks.statements.upload_image",
        "Upload an inline statement image (bytes / data URI / path).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"language\": \"en\", \"image\": \"data:image/png;base64,...\"}",
    ),
    (
        "tasks.io.get",
        "Retrieve IO/checker configuration.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.io.update",
        "Update IO/checker payload.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"io\": {...}, \"confirm\": true}",
    ),
    (
        "tasks.checker.get",
        "Retrieve checker metadata (checker_type, precision, custom code, etc.).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.checker.update",
        "Update the checker definition via SDK `update_checker`. Supported checker_type values include:\n"
        "- compare_lines_ignore_whitespaces\n"
        "- single_or_multiple_double_ignore_whitespaces\n"
        "- single_or_multiple_int64_ignore_whitespaces\n"
        "- single_or_multiple_yes_or_no_case_insensitive\n"
        "- single_yes_or_no_case_insensitive\n"
        "Set checker_type=\"custom_checker\" plus `checker` (source code) and optional `checker_language` for custom logic.\n"
        "Example args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"checker\": {\"checker_type\": \"custom_checker\", \"checker\": \"// C++ code\", \"checker_language\": \"cpp:20-clang13\"}, \"confirm\": true}",
    ),
    (
        "tasks.testsets.list",
        "List testsets for a task with pagination.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"page\": 1, \"page_size\": 10}",
    ),
    (
        "tasks.testsets.get",
        "Retrieve a single testset.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7}",
    ),
    (
        "tasks.testsets.create",
        "Create a new testset at an optional index.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"index\": 0, \"confirm\": true}",
    ),
    (
        "tasks.testsets.update",
        "Update metadata for a testset (index, score, metadata, etc.).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"update\": {\"index\": 1}, \"confirm\": true}",
    ),
    (
        "tasks.testsets.delete",
        "Delete a testset.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"confirm\": true}",
    ),
    (
        "tasks.testsets.upload_zip",
        "Upload a ZIP archive of tests (streaming optional).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"zip\": b\"...\", \"stream\": true, \"confirm\": true}",
    ),
    (
        "tasks.tests.get",
        "Fetch a single test case by index.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"index\": 0}",
    ),
    (
        "tasks.tests.upload_single",
        "Upload a single test case (input + answer bytes or paths).\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"input_data\": b\"in\", \"answer_data\": b\"out\", \"position\": -1, \"confirm\": true}",
    ),
    (
        "tasks.tests.delete_one",
        "Delete a single test case.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"index\": 0, \"confirm\": true}",
    ),
    (
        "tasks.tests.delete_many",
        "Delete multiple test cases by indexes.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"testset_id\": 7, \"indexes\": [0, 1], \"confirm\": true}",
    ),
    (
        "tasks.examples.get",
        "Retrieve a task's example IO pairs.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42}",
    ),
    (
        "tasks.examples.set",
        "Replace task example IO sets.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"inputs\": [\"1 2\"], \"outputs\": [\"3\"], \"confirm\": true}",
    ),
    (
        "tasks.examples.add",
        "Append a single example input/output pair.\nExample args: {\"hub\": \"awesome-hub\", \"task_id\": 42, \"input\": \"1 2\", \"output\": \"3\", \"confirm\": true}",
    ),
]


def _sanitize(name: str) -> str:
    return name.replace(".", "_").replace("/", "_")


_TOOL_DETAILS: List[Dict[str, Any]] = []
_NAME_LOOKUP: Dict[str, str] = {}
for raw_name, description in _RAW_TOOLS:
    safe_name = _sanitize(raw_name)
    _TOOL_DETAILS.append(
        {
            "name": safe_name,
            "description": description,
            "inputSchema": {"type": "object"},
            "metadata": {"original": raw_name},
        }
    )
    _NAME_LOOKUP[safe_name] = raw_name
    _NAME_LOOKUP[raw_name] = raw_name


def register(
    router: Router,
    guard: MCPAuthorizationGuard,
    factory: ClientFactory,
    config: MCPServerConfig,
) -> None:
    router.add_tool("tools.capabilities", lambda params, prompt: _capabilities_handler())
    router.add_tool("tools.list", lambda params, prompt: _list_handler())
    router.add_tool("tools/list", lambda params, prompt: _list_handler())
    router.add_tool(
        "tools/call",
        lambda params, prompt: _call_tool(router, guard, params, prompt),
    )


def _capabilities_handler() -> Dict[str, Any]:
    return {
        "tools": [tool["name"] for tool in _TOOL_DETAILS],
        "nextCursor": None,
    }


def _list_handler() -> Dict[str, Any]:
    return {
        "tools": list(_TOOL_DETAILS),
        "nextCursor": None,
    }


def _call_tool(
    router: Router,
    guard: MCPAuthorizationGuard,
    params: Dict[str, Any],
    prompt: ConsentPrompt,
) -> Dict[str, Any]:
    logger = get_logger("tools.call")
    tool_name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("Missing required parameter 'name'.")
    if not isinstance(arguments, dict):
        raise ValueError("Parameter 'arguments' must be an object.")

    normalized = tool_name.split("/")[-1]
    normalized = normalized.replace(".", "_")
    original_name = _NAME_LOOKUP.get(normalized, normalized)

    handler = router.lookup_handler(original_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    def auto_prompt(message: str) -> bool:
        return True
    guard.ensure_session_consent(auto_prompt)

    def _to_text(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    try:
        result = handler(arguments, auto_prompt)
    except Exception as exc:
        logger.exception("tools/call handler '%s' raised", original_name)
        return {
            "content": [{"type": "text", "text": _to_text(str(exc))}],
            "isError": True,
        }

    if isinstance(result, Iterator):
        parts = []
        for item in result:
            if isinstance(item, dict) and "error" in item:
                parts.append({"type": "text", "text": _to_text(item["error"])})
                return {"content": parts, "isError": True}
            parts.append({"type": "text", "text": _to_text(item)})
        return {"content": parts, "isError": False}

    if isinstance(result, dict) and "error" in result:
        return {
            "content": [{"type": "text", "text": _to_text(result["error"])}],
            "isError": True,
        }

    return {"content": [{"type": "text", "text": _to_text(result)}], "isError": False}


def get_tool_details() -> List[Dict[str, Any]]:
    return list(_TOOL_DETAILS)


__all__ = ["register", "get_tool_details"]
