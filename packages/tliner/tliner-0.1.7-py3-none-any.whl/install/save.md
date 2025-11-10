---
description: "Save findings/outcomes into a Timeline"
allowed_tools: ["Read", "Write", "Edit", "Glob", "LS", "mcp__timeliner__task_create", "mcp__timeliner__save_step", "mcp__timeliner__show_task"]
---

# Save Command
Execute the save operation according to the next rules.

## Flow

1.  **Generate Content**:
    *   Generate the outcomes for the current step following the "Content Structure" and "Rules".
2.  **Save to Timeliner**:
    *   Call `mcp__timeliner__save_step` with the following parameters:
        *   `task_id`: Use the memorized `task_id` if you have one. If this is the first time saving for this task, send an **empty string** (`""`). The system will create a new task and return the new `task_id`.
        *   `title`: Up to 5 words which represent essence of the step.
        *   `outcomes`: The exact content that you just generated.
    *   **VERY IMPORTANT**: If a new `task_id` is returned, you MUST memorize it for all future `save_step` calls for this task.
    
## Content Structure

1. **Summary**: Describe current step summary and general flow of investigation.
2. **Facts**: Main goal is describing outcomes as facts with GREAT details (not only summary).
3. **User Input**: Note ALL user's input and direction they want to go.
4. **Resources**: Note ALL resources used (files, links, tools, commands, etc) with direct links (full path/URL/command).
5. **Lessons Learned**: *Avoid to add this section in MOST cases*, except: 
    - **Use for**: User-insisted memories ("NEVER", "ALWAYS", "MEMORIZE") OR really high-impact, cross-task wisdom (important for the whole project).
    - **NEVER for:** Task-specific observations, general outcomes, history, what you did in this step.
    - **Format**: Short fundamental rules. Up to 10 items (max 200 characters each).
   

## Rules
1. **Title**: The `outcomes` content MUST NOT include the title. The title is passed as a separate `title` parameter to the tool.
2. **Content Headings**: All main sections within the `outcomes` (e.g., Summary, Facts, User Input) MUST start with a level 2 heading (`##`). Do NOT use level 1 headings.
3. **Avoids**: NO conclusions, NO hypothesis, NO proposals, NO assumptions, NO speculations, NO generalizations.
4. **Terminology**: Do not use "final", "real solution", "ultimate", "perfect", "best", "ideal", "correct" - use "current" instead. We are documenting current state of investigation, not final solution.
5. **Evidence**: Including evidences for statements is mandatory:
    - Link to source files with line numbers: `[cmd line flags](../src/go/flags.go#L94)`
    - Links to external resources: `[config docs](https://example.com/docs/setup.html)`
6. **Structure**: 
    - Fit all outcomes in ONE chapter, don't split into several chapters.
    - Feel free to use multiple sub-sections inside the step chapter.
