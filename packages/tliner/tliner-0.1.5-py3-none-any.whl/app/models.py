from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import BeforeValidator

strEmpty = Annotated[str, BeforeValidator(lambda x: x or "")]  # converts None/null to empty string #noqa: N816
listEmpty = Annotated[list, BeforeValidator(lambda x: x or [])]  # converts None/null to empty list #noqa: N816
dictEmpty = Annotated[dict, BeforeValidator(lambda x: x or {})]  # converts None/null to empty dict #noqa: N816


# TODO @drkr: check fields docstrings for correctness
class Step(BaseModel):
    task_id: str = Field(..., description="Unique human-friendly identifier for the task (2 words+2 digits number)")
    title: str = Field(..., description="Short description of the step (up to 5 words)")
    outcomes: str = Field(..., description="The detailed outcomes or results of the work done")
    tags: listEmpty = Field([], description="Optional list of tags")
    metadata: dictEmpty = Field({}, description="Optional links to tasks, issues, PRs, commits, etc")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the milestone creation in UTC")
    doc_id: int = Field(default=-1, description="Internal document ID in datastorage, -1 if not saved yet")

    @computed_field
    def step_id(self) -> str:
        """Step ID derived from timestamp in format YYYYMMDDTHHMMSS.ssssssZ"""
        return self.timestamp.strftime("%Y%m%dT%H%M%S.%fZ")


class Task(BaseModel):
    task_id: str = Field(..., description="Unique human-friendly identifier for the task (2 words+2 digits number)")
    title: strEmpty = Field("", description="Several words description of the task")
    doc_id: int = Field(default_factory=lambda: -1, description="Internal document ID in the database, -1 if not saved yet")
    file_path: str = Field("", description="Name of file in which it is stored")
