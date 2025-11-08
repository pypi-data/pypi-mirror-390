# Tool Reference

This document describes every MCP tool exposed by `codeany-hub-mcp-server`,
including parameters, return shapes, and example payloads. All tools mirror the
official `codeany-hub` SDK (≥ 0.2.2.8) and support JSON-RPC transports via
`tools/call`.

- **Consent:** Session consent is enforced automatically. Destructive tools
  require either a user prompt or `confirm=true`.
- **Hubs:** All hub-scoped tools expect a hub slug (e.g., `awesome-hub`).
- **Errors:** Failures are normalized (see “Errors” at the end).

## Invocation Cheatsheet

```jsonc
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tasks_list",
    "arguments": {
      "hub": "awesome-hub",
      "page": 1,
      "filters": { "query": "dp" }
    }
  }
}
```

`tools/list` / `tools.list` return the full catalog (with descriptions and
examples), while `tools.capabilities` provides sanitized names only.

---

## Hubs

### `hubs.list_mine`
- **Purpose:** Discover every hub the authenticated user owns.
- **Parameters:** _(none)_
- **Returns:** Array of hub dicts (slug, display name, visibility, etc.)
- **Example args:** `{}`

### `hubs.detail`
- **Purpose:** Get metadata for a specific hub.
- **Parameters:** `hub`
- **Example args:** `{ "hub": "awesome-hub" }`

---

## Tasks – Core Lifecycle

### `tasks.create`
- **Purpose:** Create a task; accepts the same payload as
  `client.tasks.create`.
- **Parameters:** `hub`, plus the SDK creation fields (`name`,
  `task_type`, etc.)
- **Returns:** The new task as a dict.
- **Example args:** `{ "hub": "awesome-hub", "name": "two-sum", "confirm": true }`

### `tasks.list`
- **Purpose:** Paginated task listing (supports `filters` such as `query`,
  `search`, `visibility`, `type`).
- **Parameters:** `hub`, optional `page`, `page_size`, `filters`.
- **Example args:** `{ "hub": "awesome-hub", "page": 1, "filters": { "query": "sum" } }`

### `tasks.delete`, `tasks.rename`, `tasks.toggle_visibility`
- **Purpose:** Mutate task metadata. All accept `confirm` to bypass prompts.
- **Example args (rename):**
  ```json
  {
    "hub": "awesome-hub",
    "task_id": 42,
    "name": "new-title",
    "confirm": true
  }
  ```

### `tasks.get_settings`
- **Purpose:** Retrieve the task settings blob (statements/testset options).

### `tasks.type.get` / `tasks.type.update`
- **Purpose:** Inspect or mutate the task type (batch/mcq/etc.).
- **Example args (update):**
  ```json
  { "hub": "awesome-hub", "task_id": 42, "payload": { "type": "mcq" }, "confirm": true }
  ```

---

## Tasks – Limits

### `tasks.limits.get`
- **Purpose:** Fetch execution limits (`time_limit`, `memory_limit`).

### `tasks.limits.update`
- **Purpose:** Update execution limits (ms/MB). Provide `time_limit` and
  `memory_limit` either directly or inside `limits`.
- **Example args:** `{ "hub": "awesome-hub", "task_id": 42, "time_limit": 2000, "memory_limit": 256, "confirm": true }`

---

## Tasks – Statements

### `tasks.statements.get`
- **Purpose:** Retrieve statements (optionally per `language`). Accepts task
  ID or slug.

### `tasks.statements.list`
- **Purpose:** List available statement languages.

### `tasks.statements.create_lang`
- **Purpose:** Add a localized statement payload.
- **Example:** `{ "hub": "awesome-hub", "task_id": 42, "language": "en", "content": { ... }, "confirm": true }`

### `tasks.statements.delete_lang`
- **Purpose:** Remove statement content for a locale.

### `tasks.statements.update`
- **Purpose:** Invoke the SDK’s `update_statement`. Requires `statement_id`
  and a `payload` dict.
- **Example:** `{ "hub": "awesome-hub", "task_id": 42, "statement_id": 7, "payload": { "title": "Updated" }, "confirm": true }`

### `tasks.statements.upload_image`
- **Purpose:** Upload inline images (bytes, data URI, or local path if
  `MCP_ALLOW_LOCAL_PATHS=true`).

---

## Tasks – IO & Checker

### `tasks.io.get` / `tasks.io.update`
- **Purpose:** Retrieve/update IO + checker payload (input/output format,
  checker metadata).
- **Example (update):** `{ "hub": "awesome-hub", "task_id": 42, "io": { "input": "...", "checker": ... }, "confirm": true }`

### `tasks.checker.get`
- **Purpose:** Return checker metadata from the SDK’s `get_checker` endpoint
  (checker type, precision, custom code, etc.)

### `tasks.checker.update`
- **Purpose:** Update the checker via `update_checker`. `checker_type` is
  required. Supported built-ins:
  - `compare_lines_ignore_whitespaces.cpp`
  - `single_or_multiple_double_ignore_whitespaces.cpp`
  - `single_or_multiple_int64_ignore_whitespaces.cpp`
  - `single_or_multiple_yes_or_no_case_insensitive.cpp`
  - `single_yes_or_no_case_insensitive.cpp`
  - `custom_checker` (include `checker` source and optional
    `checker_language`, e.g., `cpp:20-clang13`)
- **Example:**  
  `{ "hub": "awesome-hub", "task_id": 42, "checker": { "checker_type": "custom_checker", "checker": "// C++", "checker_language": "cpp:20-clang13" }, "confirm": true }`

---

## Tasks – Testsets

### `tasks.testsets.list`
- **Purpose:** Paginated list of testsets. Defaults to `page=1`,
  `page_size=10` (clamped to a max of 50). Response includes the final
  `page`/`page_size`.
- **Example:** `{ "hub": "awesome-hub", "task_id": 42 }`

### `tasks.testsets.get`
- **Purpose:** Fetch testset metadata by `testset_id`.

### `tasks.testsets.create`
- **Purpose:** Create a new testset (optional `index`). Requires confirm.

### `tasks.testsets.update`
- **Purpose:** Call `client.tasks.update_testset`. Provide `update` with at
  least one field (e.g., `index`, `score`, `metadata`).
- **Example:** `{ "hub": "awesome-hub", "task_id": 42, "testset_id": 7, "update": { "index": 1 }, "confirm": true }`

### `tasks.testsets.delete`
- **Purpose:** Delete a testset (requires confirm).

### `tasks.testsets.upload_zip`
- **Purpose:** Upload a ZIP archive to a specific testset. Provide
  `testset_id`, `zip` bytes/data URI/path, and `stream` flag. When `stream=true`
  the handler yields SSE-style events; when `false` it returns the final event.
- **Example:** `{ "hub": "awesome-hub", "task_id": 42, "testset_id": 7, "zip": "data:application/zip;base64,...", "stream": true, "confirm": true }`

---

## Tasks – Tests

### `tasks.tests.get`
- **Purpose:** Retrieve a single testcase by `testset_id`/`index`.

### `tasks.tests.upload_single`
- **Purpose:** Use the SDK’s `upload_single_test`. Accepts byte blobs, data
  URIs, or file paths (`input_data`, `answer_data`) and optional
  `position` (defaults to `-1`).

### `tasks.tests.delete_one` / `tasks.tests.delete_many`
- **Purpose:** Remove testcases. `delete_many` accepts `indexes` array.

---

## Tasks – Examples

### `tasks.examples.get`
- **Purpose:** Fetch example IO sets.

### `tasks.examples.set`
- **Purpose:** Replace example sets. Provide `inputs`, `outputs`, or both.

### `tasks.examples.add`
- **Purpose:** Append a single example pair.

---

## Capabilities & Discovery

- **`tools.capabilities`** – sanitized names.
- **`tools.list` / `tools/list`** – detailed metadata (description + example
  args + sanitized/original names).
- **`tools/call`** – Execute any tool via sanitized name (`tasks_list`) or dotted name (`tasks.list`).

---

## Common Fields

- `hub`: Always a hub slug (allowlist enforced when configured).
- `task`, `task_id`: Accept string or integer. Some handlers resolve slugs to IDs (e.g., statements).
- `confirm`: Optional; required to skip destructive prompts.
- Upload parameters (`zip`, `input_data`, `answer_data`, `image`): Accept
  raw bytes, base64 data URIs, or file paths if `MCP_ALLOW_LOCAL_PATHS=true`.

---

## Errors

All unexpected exceptions are normalized via
`codeany_mcp_server.errors.to_mcp_error`. Typical payload:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Time limit must be positive",
    "data": { "status_code": 422 }
  }
}
```

Common `code` values:

- `consent_rejected`
- `hub_not_allowed`
- `not_found`
- `auth_error`
- `rate_limited`
- `validation_error`
- `api_error`
- `invalid_request`
- `internal_error`

For streaming handlers, errors may appear as `{ "error": {...} }` in the
iterator stream; clients should stop processing when encountered.
