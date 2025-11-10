---
description: "Generate issue progress summary from work folder"
allowed_tools: ["Read", "mcp__timeliner__get_steps", "mcp__timeliner__task_list"]
---

# Report Command

Generate a summary of work done on a specific topic by analyzing task files in the work folder.

## Command Format and Parameters

```
/report <topic> [since] [until]
```

- `topic`: Plain text keyword for searching (case-insensitive)
- `since`, `until`: (Optional) Time period filter with informal date formats

## Flow

### 1. Parse Input Parameters

**Extract topic keyword:**
- Use `topic` as plain text keyword for content search
- No URL parsing or issue number extraction
- Search case-insensitively in step titles and outcomes

**Parse time period:**
- Convert natural language inputs to ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`) using UTC midnight boundaries
- IF not provided: Pass empty strings "" (no time filter)
- "last week" = previous calendar week (Monday 00:00:00Z, until next Monday 00:00:00Z exclusive)
- Calculate dates relative to current UTC date
- **IMPORTANT**: `until` is EXCLUSIVE (steps < until, not <=)

**Examples:** If today is 2025-10-30 (Thursday):
- "2 days ago" → since: "2025-10-28T00:00:00Z" (includes 2025-10-28 and later)
- "last week" → since: "2025-10-20T00:00:00Z", until: "2025-10-27T00:00:00Z" (Mon Oct 20 to Sun Oct 26, inclusive)
- "yesterday" → since: "2025-10-29T00:00:00Z", until: "2025-10-30T00:00:00Z" (Oct 29 only)
- "all time" → omit both parameters (empty strings)
- "on 2025-10-28" → since: "2025-10-28T00:00:00Z", until: "2025-10-29T00:00:00Z" (single day)
- "this week" → since: "2025-10-27T00:00:00Z", until: "2025-11-03T00:00:00Z" (Mon Oct 27 to Sun Nov 2, inclusive)

### 2. Retrieve Work Data

Call `mcp__timeliner__get_steps` with:
- `since`, `until`: ISO timestamp or "" if not provided
- `task_ids`: None (search all tasks)

Filter steps by keyword in `title` and `outcomes` (case-insensitive). IF no matches: Print message and exit.

### 3. Analyze and Group Steps

Group by temporal proximity (1-2 days) and thematic similarity. Each group = one "Approach" section (aim for 2-5).

Extract per approach:
- Main activities (from outcomes)
- Implementation details (files, functions, algorithms)
- Results/status (completed, in progress, blocked)
- Metadata (PR links, commits, issues)

### 4. Generate Report

**Format:**
```markdown
# Report: [Topic Name]
**Time period:** [parsed time period or "All time"]
**Generated:** [current UTC timestamp]

---

## Approach 1: [Descriptive Name]

- [Key activity 1 with brief implementation detail]
- [Key activity 2 with brief implementation detail]
- [Key activity 3 with brief implementation detail]
- [Result/outcome achieved]

**Status:** [Completed/In progress/Blocked]

---

## Approach 2: [Descriptive Name]

...

---
```

**Writing style:**
- 3-5 bullets per approach, past tense
- Include technical details (files, algorithms) but stay concise
- No code blocks or function signatures
- 1-2 sentences per bullet
- Final bullet = result/outcome
- Status: Completed, In progress, or Blocked

### 5. Output Report

Print the fully formatted markdown report to terminal for user review.

## Example Usage

**Command:**
```
/report "MkDocs integration" "3 days ago" "today"
```

**Output:**
```markdown
# Report: MkDocs Integration
**Time period:** 2025-10-27T00:00:00Z to 2025-10-30T00:00:00Z (exclusive)
**Generated:** 2025-10-30T14:23:00Z

---

## Approach 1: Hierarchical Navigation Implementation

- Analyzed existing flat navigation structure in MkDocs sidebar
- Designed Year → Month → Week grouping algorithm using ISO calendar weeks
- Implemented `nav_titles.py` hook with timestamp parsing from `YY.MM.DD-HH` format
- Tested with 10+ existing task files, verified chronological ordering
- Result: Successfully deployed hierarchical navigation

**Status:** Completed

---

## Approach 2: Port Stability Improvements

- Investigated race conditions in port allocation for MkDocs serve
- Identified bootloop problem in port binding logic
- Experimented with retry mechanisms and port availability checks

**Status:** In progress

---
```

## Edge Cases and Notes

- **No matches**: Print "No work found for [topic] in period" and exit
- **Single step**: Create one approach section
- **Missing metadata**: Omit if not present
- **Ambiguous time format**: Ask user to clarify
- **Calendar week**: "last week" always refers to previous Monday-Sunday period
- **Exclusive end date**: `until` parameter excludes the boundary (steps < until, not <=)
  - To include a full day: set `until` to next day's midnight
  - Example: "on Oct 28" = since: "2025-10-28T00:00:00Z", until: "2025-10-29T00:00:00Z"
- Keywords for searching must be case-insensitive
- Single date parameter allowed (backend filters with open conditionals)
