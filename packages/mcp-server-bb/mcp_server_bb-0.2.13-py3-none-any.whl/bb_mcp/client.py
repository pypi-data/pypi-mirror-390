from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Tuple

import httpx
from pydantic import ValidationError
from selectolax.parser import HTMLParser

from .models import (
    Announcement,
    Assignment,
    CalendarItem,
    ContentNode,
    Course,
    File,
    Folder,
    GradedItem,
    Item,
    Link,
)

logger = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    """Raised when Blackboard authentication fails."""


class BlackboardClient:
    AUTH_URL = "https://sts.cuhk.edu.cn/adfs/oauth2/authorize"
    CLIENT_ID = "4b71b947-7b0d-4611-b47e-0ec37aabfd5e"
    REDIRECT_URI = "https://bb.cuhk.edu.cn/webapps/bb-SSOIntegrationOAuth2-BBLEARN/authValidate/getCode"
    SESSION_LIFETIME = timedelta(minutes=20)
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

    def __init__(self, username: str, password: str, base_url: str = "https://bb.cuhk.edu.cn") -> None:
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
        self._login_lock = asyncio.Lock()
        self._session_expiry: Optional[datetime] = None

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def ensure_session(self) -> None:
        if self._client and self._session_expiry and datetime.now(timezone.utc) < self._session_expiry:
            return
        async with self._login_lock:
            if self._client and self._session_expiry and datetime.now(timezone.utc) < self._session_expiry:
                return
            await self._login_with_retry()

    async def _login_with_retry(self, max_retries: int = 3) -> None:
        """带重试机制的登录"""
        last_exception = None
        for attempt in range(max_retries):
            try:
                await self._login()
                return
            except AuthenticationError as e:
                last_exception = e
                logger.warning("Login attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error("All login attempts failed")
            except Exception as e:
                last_exception = e
                logger.error("Unexpected error during login attempt %d: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        if last_exception:
            raise last_exception

    async def _login(self) -> None:
        logger.info("Logging into Blackboard as %s", self._username)
        if self._client is not None:
            await self._client.aclose()

        headers = {
            "User-Agent": self.USER_AGENT,
            "Connection": "close",
        }
        self._client = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(30.0), follow_redirects=True)

        params = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "client-request-id": "d4fcc7f4-c5db-46f8-b5ee-0540020000c8",
        }
        form = {
            "UserName": f"cuhksz\\{self._username}",
            "Password": self._password,
            "Kmsi": "true",
            "AuthMethod": "FormsAuthentication",
        }

        assert self._client is not None
        response = await self._client.post(self.AUTH_URL, params=params, data=form)
        final_url = str(response.url)
        
        # 检查是否成功重定向到Blackboard
        if not final_url.startswith("https://bb.cuhk.edu.cn/webapps"):
            await self._client.aclose()
            self._client = None
            logger.error("Authentication failed: redirected to %s instead of Blackboard", final_url)
            raise AuthenticationError("Username or password incorrect")
        
        self._session_expiry = datetime.now(timezone.utc) + self.SESSION_LIFETIME
        logger.info("Blackboard login succeeded; session valid until %s", self._session_expiry.isoformat())

    async def fetch_courses(self) -> List[Course]:
        await self.ensure_session()
        url = f"{self._base_url}/webapps/portal/execute/tabs/tabAction"
        params = {"tab_tab_group_id": "_2_1"}
        text = await self._get_text(url, params=params)
        tree = HTMLParser(text)
        courses: List[Course] = []
        for li in tree.css("#_22_1termCourses_noterm > ul > li"):
            anchor = li.css_first("a")
            name_span = li.css_first("span.name")
            if not anchor or not name_span:
                continue
            href = (anchor.attributes.get("href") or "").strip()
            title = anchor.text(strip=True)
            instructor = name_span.text(strip=True)
            course_id = self._extract_first(r"id=(_\d+_\d+)", href)
            if not course_id:
                course_id = self._extract_first(r"course_id=(_\d+_\d+)", href)
            if not course_id:
                course_id = "UNKNOWN"
                logger.warning("Invalid course entry: %s", href)
            code = self._extract_first(r"([A-Za-z]{3}\d{4})", title) or "UNKNOWN"
            try:
                course = Course(title=title, code=code, instructor=instructor, id=course_id)
            except ValidationError as exc:
                logger.debug("Skipping invalid course entry: %s", exc)
                continue
            courses.append(course)
        return courses

    async def fetch_announcements(self, course: Course) -> List[Announcement]:
        await self.ensure_session()
        url = f"{self._base_url}/webapps/blackboard/execute/announcement"
        form = {
            "method": "search",
            "viewChoice": "3",
            "editMode": "false",
            "tabAction": "false",
            "announcementId": "",
            "course_id": "",
            "context": "my_announcements",
            "internalHandle": "my_announcements",
            "searchSelect": course.id,
        }
        text = await self._post_text(url, data=form)
        tree = HTMLParser(text)
        announcements: List[Announcement] = []
        for li in tree.css("#announcementList > li"):
            title_node = li.css_first("h3")
            info_paragraph = li.css_first("div.announcementInfo > p")
            time_node = li.css_first("div.details p span")
            detail_node = li.css_first("div.details")

            title = title_node.text(strip=True) if title_node else "UNKNOWN"
            poster = "UNKNOWN"
            if info_paragraph:
                text_content = info_paragraph.text(separator=" ", strip=True)
                poster = text_content.split("Posted by:")[-1].strip() if "Posted by:" in text_content else text_content
            posted_at = None
            if time_node:
                posted_at = self._parse_announcement_time(time_node.text(strip=True))
            detail = None
            if detail_node:
                detail = detail_node.text(separator="\n", strip=True)
            try:
                announcements.append(Announcement(course_id=course.id, title=title, poster=poster, time=posted_at, detail=detail))
            except ValidationError as exc:
                logger.debug("Skipping invalid announcement: %s", exc)
                continue
        announcements.sort(key=lambda a: a.time or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return announcements

    async def fetch_grades(self, course: Course) -> List[GradedItem]:
        await self.ensure_session()
        url = f"{self._base_url}/webapps/bb-mygrades-BBLEARN/myGrades"
        params = {"course_id": course.id, "stream_name": "mygrades"}
        text = await self._get_text(url, params=params)
        tree = HTMLParser(text)
        grades: List[GradedItem] = []
        for div in tree.css("#grades_wrapper > div"):
            title_node = div.css_first("div.cell.gradable > span, div.cell.gradable > a")
            grade_node = div.css_first("div.cell.grade span.grade")
            date_node = div.css_first("div.cell.activity.timestamp span.lastActivityDate")
            max_grade_node = div.css_first("span.maxGrade")
            average_node = div.css_first("div.cell.grade div.itemStats div.ave")
            median_node = div.css_first("div.cell.grade div.itemStats div.med")

            title = title_node.text(strip=True) if title_node else "UNKNOWN"
            grade_text = self._strip_text(grade_node)
            max_grade = self._strip_text(max_grade_node)
            average = self._strip_text(average_node)
            median = self._strip_text(median_node)
            date_value = None
            if date_node:
                parsed = self._parse_datetime(date_node.text(strip=True), "%b %d, %Y %I:%M %p")
                if parsed:
                    date_value = parsed
            try:
                grades.append(
                    GradedItem(
                        course_id=course.id,
                        title=title,
                        grade=grade_text or None,
                        max_grade=max_grade or None,
                        average=average or None,
                        median=median or None,
                        date=date_value,
                    )
                )
            except ValidationError as exc:
                logger.debug("Skipping invalid grade entry: %s", exc)
                continue
        return grades

    async def fetch_calendar(self) -> List[CalendarItem]:
        await self.ensure_session()
        url = f"{self._base_url}/webapps/calendar/calendarFeed/url"
        ics_location = await self._get_text(url)
        if not ics_location.startswith("http"):
            logger.warning("Unexpected calendar feed response: %s", ics_location[:200])
            return []
        ics_text = await self._get_text(ics_location)
        return self._parse_ics(ics_text)

    async def fetch_content_tree(self, course: Course) -> Folder:
        await self.ensure_session()
        module_url = f"{self._base_url}/webapps/blackboard/execute/modulepage/view"
        params = {"course_id": course.id}
        text = await self._get_text(module_url, params=params)
        tree = HTMLParser(text)
        root_folder = Folder(
            parent_id=None,
            course_id=course.id,
            link=f"{self._base_url}/webapps/blackboard/execute/modulepage/view?course_id={course.id}",
            name=f"{course.code}_root",
            id=f"{course.id}_0",
            contents=[],
        )
        folders_to_process: List[Folder] = []
        for anchor in tree.css("#courseMenuPalette_contents > li > a"):
            href = anchor.attributes.get("href") or ""
            if "listContent" not in href:
                continue
            title_span = anchor.css_first("span")
            title = title_span.text(strip=True) if title_span else anchor.text(strip=True)
            folder_id = self._extract_first(r"content_id=(_\\d+_1)", href) or f"{course.id}_{len(folders_to_process)}"
            folders_to_process.append(
                Folder(
                    parent_id=root_folder.id,
                    course_id=course.id,
                    link=self._resolve_link(href),
                    name=title,
                    id=folder_id,
                    contents=[],
                )
            )

        visited: set[str] = set()
        for folder in folders_to_process:
            await self._process_folder(folder, visited, course)
            root_folder.contents.append(folder)
        return root_folder

    async def find_content(self, course: Course, folder_name: str, content_name: str) -> Optional[ContentNode]:
        tree = await self.fetch_content_tree(course)
        folder = self._locate_folder(tree.contents, folder_name)
        if not folder:
            return None
        match_name = content_name.strip().lower()
        for content in folder.contents:
            label = self._content_label(content).lower()
            if label == match_name:
                return content
        return None

    async def download_file(self, url: str, name_hint: str) -> Tuple[bytes, str]:
        await self.ensure_session()
        assert self._client is not None
        response = await self._client.get(url)
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to fetch file: {response.status_code}")
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        data = response.content
        extension = self._determine_extension(content_type, data, name_hint)
        return data, extension

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_text(self, url: str, *, params: Optional[Dict[str, str]] = None) -> str:
        assert self._client is not None
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.text

    async def _post_text(self, url: str, *, data: Dict[str, str]) -> str:
        assert self._client is not None
        response = await self._client.post(url, data=data)
        response.raise_for_status()
        return response.text

    def _extract_first(self, pattern: str, text: str) -> Optional[str]:
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def _parse_announcement_time(self, value: str) -> Optional[datetime]:
        cleaned = value.replace("Posted on:", "").replace("CST", "").strip()
        if not cleaned:
            return None
        candidate = f"{cleaned} +0800"
        try:
            return datetime.strptime(candidate, "%A, %B %d, %Y %I:%M:%S %p %z")
        except ValueError:
            logger.debug("Unable to parse announcement time: %s", value)
            return None

    def _strip_text(self, node) -> str:
        if node is None:
            return ""
        return node.text(separator=" ", strip=True)

    def _parse_datetime(self, value: str, fmt: str) -> Optional[datetime]:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            logger.debug("Unable to parse datetime %s using %s", value, fmt)
            return None

    def _parse_ics(self, ics_text: str) -> List[CalendarItem]:
        events: List[CalendarItem] = []
        blocks = ics_text.split("BEGIN:VEVENT")
        for block in blocks[1:]:
            segment = block.split("END:VEVENT", 1)[0]
            props: Dict[str, str] = {}
            for raw_line in segment.splitlines():
                line = raw_line.strip()
                if not line or line.startswith("SEQUENCE"):
                    continue
                if line.startswith("DTSTAMP") and line.endswith("Z"):
                    key = "DTSTAMP"
                    value = line.split(":", 1)[-1]
                else:
                    key, _, value = line.partition(":")
                if not key:
                    continue
                key = key.split(";")[0]
                props[key] = value
            dtstamp = self._try_parse_utc(props.get("DTSTAMP"))
            dtstart = self._try_parse_local(props.get("DTSTART"))
            dtend = self._try_parse_local(props.get("DTEND"))
            uid = props.get("UID")
            summary = props.get("SUMMARY")
            link = None
            if uid:
                match = re.search(r"(_blackboard\.platform\.gradebook2\.GradableItem-[^@]+)", uid)
                if match:
                    link = f"{self._base_url}/webapps/calendar/launch/attempt/{match.group(1)}"
            events.append(
                CalendarItem(
                    dtstamp=dtstamp,
                    dtstart=dtstart,
                    dtend=dtend,
                    summary=summary,
                    uid=uid,
                    link=link,
                )
            )
        return events

    def _try_parse_utc(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            if value.endswith("Z"):
                return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _try_parse_local(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
            return parsed
        except ValueError:
            return None

    async def _process_folder(self, folder: Folder, visited: set[str], course: Course) -> None:
        if folder.id in visited:
            return
        visited.add(folder.id)
        text = await self._get_text(folder.link)
        tree = HTMLParser(text)
        content_nodes = tree.css("#content_listContainer > li")
        for node in content_nodes:
            image = node.css_first("img")
            alt = image.attributes.get("alt", "") if image else ""
            if alt == "Content Folder":
                await self._handle_content_folder(node, folder, visited, course)
            elif alt in {"Assignment", "Test"}:
                assignment = self._build_assignment(node, folder, course)
                if assignment:
                    folder.contents.append(assignment)
            elif alt == "Item":
                item = self._build_item(node, folder, course)
                if item:
                    folder.contents.append(item)
            elif alt == "File":
                file_node = self._build_file(node, folder, course)
                if file_node:
                    folder.contents.append(file_node)
            elif alt in {"Web Link", "Link"}:
                link_node = self._build_link(node, folder, course)
                if link_node:
                    folder.contents.append(link_node)

    async def _handle_content_folder(self, node, parent: Folder, visited: set[str], course: Course) -> None:
        anchor = node.css_first("div > h3 > a")
        span = anchor.css_first("span") if anchor else None
        if not anchor:
            return
        href = anchor.attributes.get("href", "")
        title = span.text(strip=True) if span else anchor.text(strip=True)
        folder_id = self._extract_first(r"content_id=(_\\d+_1)", href) or f"folder_{len(parent.contents)}"
        sub_folder = Folder(
            parent_id=parent.id,
            course_id=course.id,
            link=self._resolve_link(href),
            name=title,
            id=folder_id,
            contents=[],
        )
        await self._process_folder(sub_folder, visited, course)
        parent.contents.append(sub_folder)

    def _build_assignment(self, node, parent: Folder, course: Course) -> Optional[Assignment]:
        anchor = node.css_first("div > h3 > a")
        span = anchor.css_first("span") if anchor else None
        if not anchor:
            return None
        href = anchor.attributes.get("href", "")
        title = span.text(strip=True) if span else anchor.text(strip=True)
        assignment_id = self._extract_first(r"content_id=(_\\d+_1)", href) or f"assignment_{len(parent.contents)}"
        return Assignment(
            parent_id=parent.id,
            course_id=course.id,
            link=self._resolve_link(href),
            title=title,
            id=assignment_id,
        )

    def _build_item(self, node, parent: Folder, course: Course) -> Optional[Item]:
        title_node = node.css_first("div > h3 > span:nth-child(2)")
        detail_node = node.css_first("div.details > div.vtbegenerated")
        if not title_node:
            return None
        title = title_node.text(strip=True)
        detail = detail_node.text(separator="\n", strip=True) if detail_node else None
        attachments: List[File] = []
        for attachment in node.css("div.details > div.contextItemDetailsHeaders.clearfix > div > ul > li > a"):
            href = attachment.attributes.get("href", "")
            name = attachment.text(strip=True)
            attachments.append(
                File(
                    parent_id=parent.id,
                    course_id=course.id,
                    name=name,
                    link=self._resolve_link(href),
                )
            )
        return Item(
            parent_id=parent.id,
            course_id=course.id,
            title=title,
            detail=detail,
            attachment=attachments,
        )

    def _build_file(self, node, parent: Folder, course: Course) -> Optional[File]:
        anchor = node.css_first("div > h3 > a")
        if not anchor:
            return None
        href = anchor.attributes.get("href", "")
        name = anchor.text(strip=True)
        link = self._resolve_link(href)
        return File(parent_id=parent.id, course_id=course.id, name=name, link=link)

    def _build_link(self, node, parent: Folder, course: Course) -> Optional[Link]:
        anchor = node.css_first("div > h3 > a")
        description_node = node.css_first("div.details > div.vtbegenerated")
        if not anchor:
            return None
        href = anchor.attributes.get("href", "")
        title = anchor.text(strip=True)
        link = self._resolve_link(href)
        description = description_node.text(separator="\n", strip=True) if description_node else None
        return Link(parent_id=parent.id, course_id=course.id, title=title, link=link, description=description)

    def _locate_folder(self, contents: Iterable[ContentNode], name: str) -> Optional[Folder]:
        target = name.strip().lower()
        for content in contents:
            if isinstance(content, Folder):
                if content.name.strip().lower() == target:
                    return content
                nested = self._locate_folder(content.contents, name)
                if nested:
                    return nested
        return None

    def _content_label(self, content: ContentNode) -> str:
        if isinstance(content, Folder):
            return content.name
        if isinstance(content, Assignment):
            return content.title
        if isinstance(content, Item):
            return content.title
        if isinstance(content, File):
            return content.name
        if isinstance(content, Link):
            return content.title
        return ""

    def _determine_extension(self, content_type: str, payload: bytes, filename: str) -> str:
        ext = self._content_type_extension(content_type)
        if ext:
            return ext
        ext = self._magic_number_extension(payload)
        if ext:
            return ext
        ext = self._filename_extension(filename)
        return ext or ""

    def _content_type_extension(self, content_type: str) -> Optional[str]:
        mime_map = {
            "application/pdf": ".pdf",
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.ms-excel": ".xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.ms-powerpoint": ".ppt",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
            "application/vnd.oasis.opendocument.text": ".odt",
            "application/vnd.oasis.opendocument.spreadsheet": ".ods",
            "application/vnd.oasis.opendocument.presentation": ".odp",
            "text/plain": ".txt",
            "text/markdown": ".md",
            "text/html": ".html",
            "text/css": ".css",
            "text/javascript": ".js",
            "application/json": ".json",
            "application/xml": ".xml",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
            "audio/mpeg": ".mp3",
            "audio/wav": ".wav",
            "audio/ogg": ".ogg",
            "audio/mp4": ".m4a",
            "audio/aac": ".aac",
            "video/mp4": ".mp4",
            "video/avi": ".avi",
            "video/mpeg": ".mpg",
            "video/quicktime": ".mov",
            "video/x-msvideo": ".avi",
            "application/zip": ".zip",
            "application/x-rar-compressed": ".rar",
            "application/x-7z-compressed": ".7z",
            "application/gzip": ".gz",
            "application/x-tar": ".tar",
        }
        for prefix, ext in mime_map.items():
            if content_type.startswith(prefix):
                return ext
        return None

    def _magic_number_extension(self, payload: bytes) -> Optional[str]:
        if payload.startswith(b"%PDF"):
            return ".pdf"
        if payload.startswith(b"PK\x03\x04"):
            return ".zip"
        if payload.startswith(b"\xD0\xCF\x11\xE0"):
            return ".doc"
        if payload.startswith(b"\xFF\xD8\xFF"):
            return ".jpg"
        if payload.startswith(b"\x89PNG\r\n\x1A\n"):
            return ".png"
        if payload.startswith(b"GIF87a") or payload.startswith(b"GIF89a"):
            return ".gif"
        if payload.startswith(b"ID3") or payload.startswith(b"\xFF\xFB"):
            return ".mp3"
        if payload.startswith(b"RIFF") and payload[8:12] == b"WAVE":
            return ".wav"
        if len(payload) > 8 and payload[4:8] == b"ftyp":
            return ".mp4"
        return None

    def _filename_extension(self, filename: str) -> Optional[str]:
        if "." not in filename:
            return None
        ext = filename[filename.rfind(".") :].lower()
        valid = {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".md",
            ".html",
            ".css",
            ".js",
            ".json",
            ".xml",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".mp3",
            ".wav",
            ".ogg",
            ".m4a",
            ".aac",
            ".mp4",
            ".avi",
            ".mpg",
            ".mov",
            ".zip",
            ".rar",
            ".7z",
            ".gz",
            ".tar",
        }
        return ext if ext in valid else None

    def _resolve_link(self, href: str) -> str:
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if href.startswith("/"):
            return f"{self._base_url}{href}"
        return f"{self._base_url}/{href}"
