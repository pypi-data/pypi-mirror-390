import os
import re
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
from loguru import logger

from .models import Step, Task


class MdDb:
    def __init__(self) -> None:
        work_folder = os.path.expandvars(os.environ.get("TIMELINER_WORK_FOLDER", "work/docs"))
        self.path_md_files = Path(work_folder)
        self.path_md_files.mkdir(parents=True, exist_ok=True)

    def _read_md(self, file_path: Path, num_lines: int | None = None) -> str:
        """
        Reads a file either entirely or up to a specified number of lines.
        Args:
            file_path (str): Path to the file.
            num_lines (int, optional): Number of lines to read. If None, read the whole file.
        Returns:
            str: Entire file content or indicated number of lines or empty.
        """
        try:
            with file_path.open() as file:
                if num_lines is None:
                    return file.read()  # Read full content as a string
                # Read up to num_lines, or fewer if file is shorter
                lines = []
                for _ in range(num_lines):
                    line = file.readline()
                    if not line:  # End of file reached
                        break
                    lines.append(line)
                return "".join(lines)

        except FileNotFoundError:
            logger.warning(f"File '{file_path}' not found.")

        return ""

    def _get_metadata(self, file_path: Path) -> dict:
        """Read few first lines of file, parse it to metadata and return it."""
        # warning! num_lines valuue must be biggest than numbers of lines of the metadata!
        raw_metadata = self._read_md(file_path=file_path, num_lines=50)
        data = frontmatter.loads(raw_metadata)
        return data.metadata

    def _get_content(self, file_path: Path) -> str:
        """Read whole md file, parse it and return content without metadata."""
        raw_file = self._read_md(file_path=file_path, num_lines=None)
        data = frontmatter.loads(raw_file)
        return data.content

    def _parse_task(self, file_path: Path) -> Task | None:
        """
        Parses file and returns the Task instance or None
        if data structure is not suitable.
        Args:
            file_path: Path to file to parse.
        Returns: Optional[Task]: Task instance or None.
        """
        metadata = self._get_metadata(file_path)
        if not metadata:
            # logger.info(f"File {file} has no metadata")
            return None
        metadata_id = metadata.get("timestamp", "")
        metadata_title = metadata.get("title", "")
        if not metadata_id or not metadata_title:
            # logger.info(f"Invalid metadata of file '{file}'")
            return None
        if not isinstance(metadata_id, str) or not isinstance(metadata_title, str):
            return None
        return Task(task_id=metadata_id, title=metadata_title, file_path=str(file_path))

    def _get_approx_tasks(self, clue: str) -> list[Task]:
        """
        Returns list of all Task data objects (see _get_task_data()).
        """
        md_files_path = Path(self.path_md_files)
        return [task_data for file in md_files_path.glob(clue) if (task_data := self._parse_task(file)) is not None]

    def _check_id(self, id_str: str) -> bool:
        """
        Checks if the input string is a valid timestamp in the format:
        YYYYMMDDTHHMMSS.ssssssZ (e.g., 20250930T123041.163396Z)
        Args:
            id_str: str: Id to check.
        Returns: bool: Is id correspond to format.
        """
        if not isinstance(id_str, str):
            return False
        # Define regex pattern for the format
        pattern = r"^\d{8}T\d{6}\.\d{6}Z$"
        if not re.match(pattern, id_str):
            return False
        try:
            # Try to parse it using datetime
            datetime.strptime(id_str, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return False
        return True

    def _convert_id(self, task_id: str) -> str:
        """
        Converts a task id (timestamp from 'YYYYMMDDTHHMMSS.microsecondsZ' format)
        to timestamp of 'YYYY_MM_DD-HHMMSS' format.

        Note: Intentionally loses microseconds precision for human-readable filenames.
        This is used for glob pattern matching - multiple tasks created in the same second
        will all match the pattern and be filtered by exact task_id afterward.

        WARNING! We expect that id already passed the checking by _check_id() since this
        function is called by get_task() only! Otherwise add some checking.

        Args:
            task_id (str): Input timestamp string, e.g., '20251008T103657.790385Z'
        Returns:
            str: Formatted timestamp string, e.g., '2025_10_08-103657'
        """
        dt = datetime.strptime(task_id, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)
        return dt.strftime("%Y_%m_%d-%H%M%S")

    def _parse_steps(self, content: str, task: Task) -> list[Step]:
        steps = []
        # 1. Split the text by "# Step." at line start while preserving the delimiter
        raw_blocks = re.split(r"(?=^# Step\.)", content, flags=re.MULTILINE)[1:]  # skip the first empty item
        for block in raw_blocks:
            # 2. Extract the title from the first line
            title_match = re.match(r"# Step\.\s*(.+)", block)
            if not title_match:  # skip malformed block
                continue
            title = title_match.group(1).strip()
            # 3. Remove the title line before passing to frontmatter
            body = "\n".join(block.split("\n")[1:]).strip()
            # 4. Parse to get metadata and content
            post = frontmatter.loads(body)
            # 5. Use content as outcomes (title is separate field now)
            outcomes = post.content
            # logger.info(outcomes)
            # 6. Prepare and check metadata
            metadata_time = post.metadata.get("timestamp", None)
            metadata_tags = post.metadata.get("tags", None)
            metadata_metadata = post.metadata.get("metadata", None)
            if not metadata_time or not isinstance(metadata_time, str) or not self._check_id(metadata_time):
                logger.warning("Invalid metadata of step")
                continue
            if not isinstance(metadata_tags, list):
                metadata_tags = []
            if not isinstance(metadata_metadata, dict):
                metadata_metadata = {}
            # 7. Create and save instances
            parsed_timestamp = datetime.strptime(metadata_time, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)
            step = Step(task_id=task.task_id, title=title, outcomes=outcomes, tags=metadata_tags, metadata=metadata_metadata, timestamp=parsed_timestamp)
            steps.append(step)
        return steps

    def _wrap_metadata(self, metadata: dict) -> str:
        res = "\n".join(f"{key}: {value}" for key, value in metadata.items())
        # there is no \n at start of metadata because this block added:
        # 1. on start of file when task creates
        # 2. when step added after "# Step" with necessary newlines
        return f"---\n{res}\n---\n\n"

    def _write_to_file(self, file_path: Path, content: str) -> bool:
        try:
            with file_path.open("a") as file:
                file.write(content)
        except OSError as e:
            logger.error(f"Writing to '{file_path}' failed: {e}")
            return False
        return True

    def _get_valid_filename(self, timestamp: str, name: str) -> str:
        # TODO @drkr: corner cases for e.g. symbols at the start and end of the string
        if not name:
            return f"{timestamp}-unknown"
        # remove redundant whitespaces and convert to hyphen:
        kebab_case = "-".join(name.split())
        # remove any symbols except hyphen:
        valid_name = "".join([x if x.isalnum() or x == "-" else "" for x in kebab_case])
        return f"{timestamp}-{valid_name}"

    def create_task(self, title: str) -> Task | None:
        now = datetime.now(timezone.utc)
        time_micros = now.strftime("%Y%m%dT%H%M%S.%fZ")
        # for a filename, I insitst to use the full year and `_`` in the date, due to human readability: `2023_09_23-123041` is` easier to understand than `230923-123041``
        time_seconds = now.strftime("%Y_%m_%d-%H%M%S")

        task = Task(task_id=time_micros, title=title, file_path="")
        filename = self._get_valid_filename(time_seconds, title)
        file_path = self.path_md_files.joinpath(f"{filename}.md")
        metadata = self._wrap_metadata({"title": title, "timestamp": time_micros, "workspace": self.path_md_files})
        if not self._write_to_file(file_path=file_path, content=metadata):
            logger.error(f"Unable to create new task (id: {task.task_id})")
            return None
        task.file_path = str(file_path)
        logger.info(f"New task has been created (id: {task.task_id})")
        return task

    def _save_step(self, file_path: str, title: str, step: Step) -> bool:
        now = datetime.now(timezone.utc)
        time_micros = now.strftime("%Y%m%dT%H%M%S.%fZ")
        content = step.outcomes
        metadata = self._wrap_metadata({"timestamp": time_micros, "tags": step.tags, "metadata": step.metadata})
        content = f"\n# Step. {title}\n\n{metadata}{content}\n"
        return self._write_to_file(file_path=Path(file_path), content=content)

    def create_step(self, task_id: str, title: str, outcomes: str, tags: list | None = None, metadata: dict | None = None) -> Step | None:
        task = self.get_task(task_id)
        if not task:
            logger.error(f"Step adding failed. Task not found (id: {task_id})")
            return None
        task_file = task.file_path
        if not task_file:
            logger.error(f"Step adding failed. There is no file of the task (id: {task_id})")
            return None
        # create and store the step
        step = Step(task_id=task_id, title=title, outcomes=outcomes, tags=tags or [], metadata=metadata or {})
        if not self._save_step(task_file, title, step):
            logger.error(f"Step adding failed. Unable write to task file (id: {task_id})")
            return None
        logger.info(f"New step has been added to task (id: {task_id})")
        return step

    def get_task(self, task_id: str) -> Task | None:
        """
        Return Task object by its id.
        """
        if not self._check_id(task_id):
            return None
        converted_id = self._convert_id(task_id)
        clue = f"{converted_id}*.md"
        for task in self._get_approx_tasks(clue):
            if task.task_id == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[Task]:
        """
        Returns list of all Task objects.
        """
        md_files_path = Path(self.path_md_files)
        return [task_data for file in md_files_path.glob("*.md") if (task_data := self._parse_task(file)) is not None]

    def get_steps_by_task(self, task: Task) -> list[Step]:
        if not task:
            return []
        content = self._get_content(file_path=Path(task.file_path))
        return self._parse_steps(content, task)

    def get_steps_by_task_id(self, task_id: str = "") -> list[Step]:
        task = self.get_task(task_id)
        if not task:
            return []
        return self.get_steps_by_task(task)

    def get_all_steps(self, since: str = "", until: str = "") -> list[Step]:
        def _convert_timestamp(timestamp: str) -> datetime:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValueError(f"Invalid timestamp format. Expected ISO 8601 UTC: {e}") from e
            return dt

        all_tasks = self.get_all_tasks()
        all_steps = []

        for task in all_tasks:
            steps = self.get_steps_by_task(task)
            all_steps.extend(steps)

        if not since and not until:
            return all_steps

        filtered_steps = []
        since_dt = _convert_timestamp(since) if since else None
        until_dt = _convert_timestamp(until) if until else None

        for step in all_steps:
            if since_dt is not None and step.timestamp < since_dt:
                continue
            if until_dt is not None and step.timestamp >= until_dt:
                continue
            filtered_steps.append(step)

        return filtered_steps

    def get_step_by_doc_id(self, doc_id: int) -> Step | None:
        # TODO @drkr: NIY
        _ = doc_id
        return None

    def get_task_by_doc_id(self, doc_id: int) -> Task | None:
        # TODO @drkr: NIY
        _ = doc_id
        return None

    def generate_task_id(self) -> str:
        """Generate a new task ID based on current timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%dT%H%M%S.%fZ")


# singleton instance (init at the module level, thus thread-safe)
# _instance = TimelinerService()
_instance = MdDb()


def Timeline() -> MdDb:  # noqa: N802 # Upper case intentional for singleton accessor
    return _instance
