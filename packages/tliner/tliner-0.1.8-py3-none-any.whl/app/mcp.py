from fastmcp import FastMCP
from loguru import logger

from .services import Timeline

app = FastMCP("timeliner")
service = Timeline()


@app.tool(enabled=False)
def task_create(task_title: str, user_prompt: str = "") -> dict:
    """
    Creates a new task with an auto-generated task ID.
    Args:
        task_title: Title of the task to be created
        user_prompt: Optional initial user prompt to save with task creation
    Returns: dict: Task creation result
    """
    task = service.create_task(task_title)
    if not task:
        raise ValueError(f"Unable to create task '{task_title}'")

    logger.info(f"Created new task '{task_title}' with id: {task.task_id}")

    # If user_prompt is provided, immediately save it as the first step
    if user_prompt:
        service.create_step(task.task_id, "Initial prompt", user_prompt, tags=["prompt"])
        logger.info(f"Saved initial prompt as step for task {task.task_id}")

    return {"task_id": task.task_id, "md_file": task.file_path}


@app.tool(enabled=False)  # disable for now, use get_steps() with task_id as param
def task_show(task_id: str) -> dict:
    """
    Retrieves all steps for a given task.
    Args: task_id: The task identifier
    Returns: dict: List of steps for the task
    """
    steps = service.get_steps_by_task_id(task_id)
    return {"task_id": task_id, "steps": [m.model_dump() for m in steps]}


@app.tool()
def task_list() -> dict:
    """
    Lists all tasks in the system.

    WHEN TO USE:
    - To discover existing tasks
    - To find a task_id when you need to add steps to existing work
    - To review what work has been tracked in the Timeline

    Returns: dict containing list of all tasks with their task_id, title, and file paths
    """
    tasks = service.get_all_tasks()
    return {"tasks": [task.model_dump() for task in tasks]}


@app.tool()
def save_step(task_id: str, title: str, outcomes: str, tags: list[str] | None = None, metadata: dict[str, str] | None = None) -> dict:
    """
    Records the step in the Timeline for tracking AI agent work outcomes.

    WHEN TO USE:
    - After completing any significant work (bug fix, feature implementation, investigation)
    - To document decisions, findings, or outcomes that future context might need
    - To create audit trail of what was done and why

    WORKFLOW:
    1. First time? Pass "new" as task_id to auto-create new task (also accepts: "", '""', '"new"')
    2. Subsequent steps? Use the task_id returned from previous save_step call (e.g., "happy-cloud-42")
    3. Add descriptive tags to make steps searchable (e.g., ["bugfix", "authentication"])
    4. Include metadata links to related resources (GitHub issues, PRs, commits)

    Args:
        task_id: Task identifier. To CREATE NEW: use "new". To APPEND: use existing task_id (e.g., "happy-cloud-42")
        title: Concise step description (e.g., "Fixed login timeout bug")
        outcomes: Detailed explanation of what was done, decisions made, and results
        tags: Optional categorization tags ["feature", "refactor", "investigation"]
        metadata: Optional links {"github_issue": "https://...", "pr": "https://...", "commit": "abc123"}

    Returns: dict with task_id, step_id, and file_path to the task's markdown file
    """
    # Check correctness of 'task_id'
    if task_id is None or not isinstance(task_id, str):
        raise ValueError(f"Invalid type of task_id ({task_id}). Please provide a valid task_id type or empty string.")

    # Normalize pseudo-empty strings that LLMs sometimes send
    # Support: "", '""', "new", '"new"' as indicators to create new task
    normalized_task_id = task_id.strip()
    if normalized_task_id in ['""', "new", '"new"', "'new'"]:
        normalized_task_id = ""

    # fetch Task instance and check if task exist
    if not normalized_task_id:
        task = service.create_task(title=title)
        if not task:
            raise ValueError(f"Unable to create task ({task_id}). Failed when at file creating.")  # TODO @vz: what llm should do?
    else:
        task = service.get_task(normalized_task_id)
        if not task:
            raise ValueError(f"Task with id {normalized_task_id} does not exist. Please provide a valid task_id or empty string.")

    # Create step
    step = service.create_step(task.task_id, title, outcomes, tags, metadata)
    if not step:
        raise ValueError("Failed to create the step.")  # TODO @vz: what llm should do?

    logger.info(f"Successfully saved step for task {task_id}")
    return {"task_id": task.task_id, "step_id": step.step_id, "file_path": task.file_path}


@app.tool(enabled=False)
def get_task_file_path(task_id: str) -> dict:
    """
    Returns the absolute file path to a task's markdown documentation file.

    WHEN TO USE:
    - When you need to read the full task history as markdown
    - To provide file path references to users or other systems
    - To verify a task exists before adding steps

    Args:
        task_id: The task identifier

    Returns: dict containing task_id and absolute file_path to markdown file
    """
    task = service.get_task(task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} does not exist")
    return {"task_id": task_id, "file_path": task.file_path}


@app.tool()
def get_steps(since: str = "", until: str = "", task_ids: list[str] | None = None) -> dict:
    """
    Retrieves steps from the Timeline with optional filtering by time or tasks.

    WHEN TO USE:
    - To load context from previous work sessions
    - To find relevant past decisions or implementations
    - To review what was done recently or on specific tasks

    FILTERING OPTIONS:
    - No filters: Returns ALL steps across all tasks
    - since only: Get steps from a specific time [include] onwards (ISO format: "2025-01-01T00:00:00Z")
    - until only: Get steps up to a specific time [exclude] (ISO format: "2025-02-01T00:00:00Z")
    - since and until: Get steps in a specific time range
    - task_ids: Get steps only from specific tasks
    - Combine: Mix time and task filters for precise queries
    - NOTE: Steps and tasks always use the UTC timezone for timestamps. Convert local time to UTC BEFORE providing 'since' and 'until' filters.

    Args:
        since: Optional ISO UTC format timestamp to filter steps from  [include] (e.g., "2025-01-01T00:00:00Z")
        until: Optional ISO UTC format timestamp to filter steps until [exclude] (e.g., "2025-02-01T00:00:00Z")
        task_ids: Optional list of task IDs to filter steps (e.g., ["happy-cloud-42", "gentle-wind-77"])

    Returns: dict: List of all steps, optionally filtered by time and task IDs
    """
    steps = service.get_all_steps(since=since, until=until)

    # Filter by task_ids if provided
    if task_ids:
        steps = [m for m in steps if m.task_id in task_ids]

    step_dicts = []
    for m in steps:
        m_dict = m.model_dump()
        m_dict["timestamp"] = m.timestamp.isoformat()
        step_dicts.append(m_dict)
    return {"steps": step_dicts, "count": len(steps)}


@app.tool(enabled=False)
def get_step(doc_id: int) -> dict:
    """
    Retrieves a specific step by its document ID.
    Args:
        doc_id: The document ID of the step to retrieve
    Returns: dict: The step data or error if not found
    """
    step = service.get_step_by_doc_id(doc_id)
    if not step:
        raise ValueError(f"Step with doc_id {doc_id} not found")
    m_dict = step.model_dump()
    m_dict["timestamp"] = step.timestamp.isoformat()
    return {"step": m_dict}
