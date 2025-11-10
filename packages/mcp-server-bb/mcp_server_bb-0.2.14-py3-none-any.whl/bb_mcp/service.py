from __future__ import annotations

from datetime import timedelta
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from pydantic import ValidationError

from .cache import DEFAULT_TTLS, JsonCache
from .client import BlackboardClient
from .config import get_settings
from .models import Announcement, CalendarItem, Course, Folder, GradedItem


class CourseLookupError(ValueError):
    def __init__(self, query: str, suggestions: List[Course]):
        self.query = query
        self.suggestions = suggestions
        suggestion_text = ", ".join(f"{course.code} ({course.title})" for course in suggestions[:3])
        message = f"Course '{query}' not found."
        if suggestion_text:
            message += f" Did you mean: {suggestion_text}?"
        super().__init__(message)


class BlackboardService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = BlackboardClient(settings.bb_username, settings.bb_password, settings.bb_base_url)
        self._cache = JsonCache(settings.cache_file)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_courses(self, force_refresh: bool = False) -> List[Course]:
        return await self._get_cached_list(
            key="courses",
            loader=self._client.fetch_courses,
            model=Course,
            ttl=DEFAULT_TTLS["courses"],
            force_refresh=force_refresh,
        )

    async def get_announcements(self, course_code: str, limit: Optional[int] = None) -> List[Announcement]:
        course = await self._require_course(course_code)
        cache_key = f"announcements:{course.id}"
        announcements = await self._get_cached_list(
            key=cache_key,
            loader=lambda: self._client.fetch_announcements(course),
            model=Announcement,
            ttl=DEFAULT_TTLS["announcements"],
        )
        if limit is not None:
            return announcements[:limit]
        return announcements

    async def get_grades(self, course_code: str) -> List[GradedItem]:
        course = await self._require_course(course_code)
        cache_key = f"grades:{course.id}"
        return await self._get_cached_list(
            key=cache_key,
            loader=lambda: self._client.fetch_grades(course),
            model=GradedItem,
            ttl=DEFAULT_TTLS["grades"],
        )

    async def get_calendar(self) -> List[CalendarItem]:
        return await self._get_cached_list(
            key="todo",
            loader=self._client.fetch_calendar,
            model=CalendarItem,
            ttl=DEFAULT_TTLS["todo"],
        )

    async def get_content_tree(self, course_code: str) -> Folder:
        course = await self._require_course(course_code)
        cache_key = f"content_tree:{course.id}"
        entry = await self._cache.read(cache_key)
        if entry and not entry.expired:
            try:
                return Folder.model_validate(entry.payload)
            except ValidationError:
                await self._cache.clear(cache_key)
        folder = await self._client.fetch_content_tree(course)
        await self._cache.write(cache_key, folder.model_dump(mode="json"), DEFAULT_TTLS["content_tree"])
        return folder

    async def find_content(self, course_code: str, folder_name: str, content_name: str):
        root = await self.get_content_tree(course_code)
        folder = _locate_folder(root, folder_name)
        if folder is None:
            return None
        target = content_name.strip().lower()
        for node in folder.contents:
            label = _content_node_label(node).strip().lower()
            if label == target:
                return node
        return None

    async def download_file(self, url: str, name: str):
        data, extension = await self._client.download_file(url, name)
        return data, extension

    async def _get_cached_list(self, key: str, loader, model, ttl: timedelta, force_refresh: bool = False):
        if not force_refresh:
            entry = await self._cache.read(key)
            if entry and not entry.expired:
                try:
                    return [model.model_validate(item) for item in entry.payload]
                except ValidationError:
                    await self._cache.clear(key)
        data = await loader()
        await self._cache.write(key, [item.model_dump(mode="json") for item in data], ttl)
        return data

    async def _require_course(self, code: str) -> Course:
        course, suggestions = await self._resolve_course(code)
        if course is None:
            raise CourseLookupError(code, suggestions)
        return course

    async def _resolve_course(self, code: str) -> Tuple[Optional[Course], List[Course]]:
        courses = await self.get_courses()
        if not courses:
            return None, []

        query = code.strip()
        normalized = query.lower()

        for course in courses:
            if normalized == course.code.lower() or normalized == course.id.lower():
                return course, []

        substring_matches = [
            course for course in courses
            if normalized and (
                normalized in course.code.lower()
                or normalized in course.id.lower()
                or normalized in course.title.lower()
            )
        ]
        if len(substring_matches) == 1:
            return substring_matches[0], []

        suggestions = self._suggest_courses(courses, normalized)
        return None, suggestions

    def _suggest_courses(self, courses: List[Course], normalized_query: str) -> List[Course]:
        if not courses:
            return []
        scored: List[Tuple[float, Course]] = []
        for course in courses:
            code = course.code.lower()
            course_id = course.id.lower()
            title = course.title.lower()
            score = 0.0
            if normalized_query:
                if (
                    normalized_query in code
                    or normalized_query in course_id
                    or normalized_query in title
                ):
                    score = 1.0
                else:
                    score = max(
                        SequenceMatcher(None, normalized_query, code).ratio(),
                        SequenceMatcher(None, normalized_query, course_id).ratio(),
                        SequenceMatcher(None, normalized_query, title).ratio(),
                    )
            scored.append((score, course))

        scored.sort(key=lambda item: item[0], reverse=True)
        suggestions = [course for score, course in scored if score > 0.3][:3]
        if not suggestions:
            suggestions = [course for _, course in scored[:3]]
        return suggestions


def render_course_summary(course: Course) -> str:
    return (
        f"Title: {course.title}\n"
        f"Code: {course.code}\n"
        f"Instructor: {course.instructor}\n"
        f"ID: {course.id}"
    )


def render_announcement(announcement: Announcement) -> str:
    time_part = announcement.time.isoformat() if announcement.time else "Unknown"
    detail = announcement.detail or "No detail provided."
    return (
        f"Title: {announcement.title}\n"
        f"Poster: {announcement.poster}\n"
        f"Time: {time_part}\n"
        f"Detail: {detail}"
    )


def render_grade(grade: GradedItem) -> str:
    date = grade.date.isoformat() if grade.date else "Unknown"
    return (
        f"Title: {grade.title}\n"
        f"Grade: {grade.grade or 'Unknown'}\n"
        f"Max Point possible: {grade.max_grade or 'Unknown'}\n"
        f"Average: {grade.average or 'Unknown'}\n"
        f"Median: {grade.median or 'Unknown'}\n"
        f"Date: {date}"
    )


def render_todo(calendar: CalendarItem) -> str:
    return (
        f"Summary: {calendar.summary or 'Unknown'}\n"
        f"Link: {calendar.link or 'Unknown'}\n"
        f"Start: {calendar.dtstart.isoformat() if calendar.dtstart else 'Unknown'}\n"
        f"End: {calendar.dtend.isoformat() if calendar.dtend else 'Unknown'}"
    )


def render_content_tree(folder: Folder) -> str:
    lines: List[str] = []

    def walk(current: Folder, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{current.name}")
        next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
        for index, node in enumerate(current.contents):
            last = index == len(current.contents) - 1
            if isinstance(node, Folder):
                walk(node, next_prefix, last)
            else:
                label = _content_node_label(node)
                lines.append(f"{next_prefix}{'└── ' if last else '├── '}{label}")

    walk(folder)
    return "\n".join(lines)


def _content_node_label(node) -> str:
    if hasattr(node, "name"):
        return getattr(node, "name")
    if hasattr(node, "title"):
        return getattr(node, "title")
    return "item"


def _locate_folder(root: Folder, name: str) -> Optional[Folder]:
    target = name.strip().lower()
    if root.name.strip().lower() == target:
        return root
    for node in root.contents:
        if isinstance(node, Folder):
            found = _locate_folder(node, name)
            if found:
                return found
    return None
