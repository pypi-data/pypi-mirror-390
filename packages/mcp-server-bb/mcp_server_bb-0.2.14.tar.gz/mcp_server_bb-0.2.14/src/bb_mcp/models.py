from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class Course(BaseModel):
    title: str
    code: str
    instructor: str
    id: str


class Announcement(BaseModel):
    course_id: str
    title: str
    poster: str
    time: Optional[datetime] = None
    detail: Optional[str] = None


class AssignmentState(str, Enum):
    UNFINISHED = "UnFinished"
    GRADING = "Grading"
    GRADED = "Graded"


class AssignmentDetails(BaseModel):
    assignment_id: str
    state: AssignmentState
    due: Optional[datetime] = None
    grade: Optional[str] = None
    max_grade: Optional[str] = None
    description: Optional[str] = None


class GradedItem(BaseModel):
    course_id: str
    title: str
    grade: Optional[str] = None
    date: Optional[datetime] = None
    max_grade: Optional[str] = None
    average: Optional[str] = None
    median: Optional[str] = None


class CalendarItem(BaseModel):
    dtstamp: Optional[datetime] = None
    dtstart: Optional[datetime] = None
    dtend: Optional[datetime] = None
    summary: Optional[str] = None
    uid: Optional[str] = None
    link: Optional[str] = None


class ContentType(str, Enum):
    FOLDER = "folder"
    ASSIGNMENT = "assignment"
    ITEM = "item"
    FILE = "file"
    LINK = "link"


class ContentBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    parent_id: Optional[str] = None
    course_id: str
    type: ContentType


class Folder(ContentBase):
    type: ContentType = Field(default=ContentType.FOLDER, init=False)
    link: str
    name: str
    id: str
    contents: List["ContentNode"] = Field(default_factory=list)


class Assignment(ContentBase):
    type: ContentType = Field(default=ContentType.ASSIGNMENT, init=False)
    title: str
    id: str
    link: str


class Item(ContentBase):
    type: ContentType = Field(default=ContentType.ITEM, init=False)
    title: str
    detail: Optional[str] = None
    attachment: List["File"] = Field(default_factory=list)


class File(ContentBase):
    type: ContentType = Field(default=ContentType.FILE, init=False)
    name: str
    link: str
    item_id: Optional[int] = None
    suggested_path: Optional[Path] = None


class Link(ContentBase):
    type: ContentType = Field(default=ContentType.LINK, init=False)
    title: str
    link: str
    description: Optional[str] = None


ContentNode = Union[Folder, Assignment, Item, File, Link]


class DownloadResult(BaseModel):
    success: bool
    message: str
    suggested_extension: Optional[str] = None
    file_path: Optional[str] = None


Folder.model_rebuild()
Assignment.model_rebuild()
Item.model_rebuild()
File.model_rebuild()
Link.model_rebuild()
