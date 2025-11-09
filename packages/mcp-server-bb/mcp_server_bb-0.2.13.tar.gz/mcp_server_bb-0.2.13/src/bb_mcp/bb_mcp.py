from __future__ import annotations

from typing import Annotated
from pydantic import Field
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import dotenv

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .models import Announcement, CalendarItem, DownloadResult, GradedItem
from .service import (
    BlackboardService,
    CourseLookupError,
    render_announcement,
    render_content_tree,
    render_course_summary,
    render_grade,
    render_todo,
)
from .client import AuthenticationError

mcp = FastMCP("BB-MCP")
PAGE_SIZE = 10
dotenv.load_dotenv()
service = BlackboardService()


def _format_section(items: list[str], empty_message: str) -> str:
    return "\n---\n".join(items) if items else f"\n---\n{empty_message}"


def _format_course_not_found(error: CourseLookupError) -> str:
    if error.suggestions:
        suggestion_text = ", ".join(
            f"{course.code} ({course.title})" for course in error.suggestions[:3]
        )
        return f"\n---\nCourse '{error.query}' not found. Did you mean: {suggestion_text}?"
    return f"\n---\nCourse '{error.query}' not found."


@mcp.tool(
        description="获取用户在CUHKSZ已注册的课程列表"
)
async def fetch_course_list() -> str:
    """Get user's enrolled course list from CUHKSZ."""
    try:
        courses = await service.get_courses()
        rendered = [render_course_summary(course) for course in courses]
        return _format_section(rendered, "No course found.")
    except AuthenticationError as error:
        return f"\n---\n认证失败: {error}. 请检查用户名和密码是否正确，或者稍后重试。"
    except Exception as error:
        return f"\n---\n获取课程列表时发生错误: {error}. 请稍后重试。"

@mcp.tool(
    description="获取用户在CUHKSZ的待办事项列表（分页，默认每页10条，按时间倒序）"
)
async def fetch_todo(
    page: Annotated[int, Field(description="页码，从1开始")] = 1,
) -> str:
    """Get user's todo list from CUHKSZ with pagination."""
    # 拉取并按时间倒序（最新在前）排序
    items = await service.get_calendar()

    def item_time(itm: CalendarItem):
        t = itm.dtstart or itm.dtend or itm.dtstamp
        if t is None:
            return datetime.min
        return t.astimezone(timezone.utc).replace(tzinfo=None) if t.tzinfo else t

    items_sorted = sorted(items, key=item_time, reverse=True)

    # 分页参数
    total = len(items_sorted)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 0
    # 规范化页码显示与切片
    if total_pages > 0:
        current_page = min(max(1, page), total_pages)
        start = (current_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = items_sorted[start:end]
    else:
        # 无数据时，显示为第0页
        current_page = 0
        page_items = []

    rendered = [_format_calendar(item) for item in page_items]
    body = _format_section(rendered, "No todo items found. You are all set!")
    return body + f"\n---\n页码: {current_page} 总数: {total}"


def _format_calendar(item: CalendarItem) -> str:
    return render_todo(item)


@mcp.tool(
        description="获取用户在CUHKSZ的指定课程的公告信息（分页，默认每页10条，按时间倒序）"
)
async def fetch_announcements(
    code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")],
    page: Annotated[int, Field(description="页码，从1开始")] = 1,
) -> str:
    """Get user's announcements from CUHKSZ with pagination."""
    try:
        announcements = await service.get_announcements(code, None)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    except AuthenticationError as error:
        return f"\n---\n认证失败: {error}. 请检查用户名和密码是否正确，或者稍后重试。"
    except Exception as error:
        return f"\n---\n获取公告时发生错误: {error}. 请稍后重试。"
    # 排序（最新在前）
    def item_time(itm: Announcement):
        t = itm.time or datetime.min
        return t.astimezone(timezone.utc).replace(tzinfo=None) if t.tzinfo else t
    items_sorted = sorted(announcements, key=item_time, reverse=True)
    # 分页
    total = len(items_sorted)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 0
    if total_pages > 0:
        current_page = min(max(1, page), total_pages)
        start = (current_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = items_sorted[start:end]
    else:
        current_page = 0
        page_items = []
    rendered = [render_announcement(announcement) for announcement in page_items]
    body = _format_section(rendered, "No announcements found.")
    return body + f"\n---\n页码: {current_page} 总数: {total}"


@mcp.tool(
        description="获取用户在CUHKSZ的指定课程的成绩信息（分页，默认每页10条，按时间倒序）"
)
async def fetch_grades(
    code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")],
    page: Annotated[int, Field(description="页码，从1开始")] = 1,
) -> str:
    """Get user's grades from CUHKSZ with pagination."""
    try:
        grades = await service.get_grades(code)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    except AuthenticationError as error:
        return f"\n---\n认证失败: {error}. 请检查用户名和密码是否正确，或者稍后重试。"
    except Exception as error:
        return f"\n---\n获取成绩时发生错误: {error}. 请稍后重试。"
    # 排序（最新在前）
    def item_time(itm: GradedItem):
        return itm.date or datetime.min
    items_sorted = sorted(grades, key=item_time, reverse=True)
    # 分页
    total = len(items_sorted)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 0
    if total_pages > 0:
        current_page = min(max(1, page), total_pages)
        start = (current_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = items_sorted[start:end]
    else:
        current_page = 0
        page_items = []
    rendered = [render_grade(grade) for grade in page_items]
    body = _format_section(rendered, "No grades found.")
    return body + f"\n---\n页码: {current_page} 总数: {total}"


@mcp.tool(
    description="获取用户在CUHKSZ的指定课程的内容（分页，默认每页10条；非verbose模式下按原有顺序分页）"
)
async def fetch_content(
    code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")],
    verbose: Annotated[bool, Field(description="是否原始的json信息，否则返回树状结构的文本")] = False,
    page: Annotated[int, Field(description="页码，从1开始")] = 1,
) -> str:
    """Get course content from CUHKSZ (paginated when not verbose)."""
    try:
        folder = await service.get_content_tree(code)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    if verbose:
        # 保持与以往一致：verbose模式返回完整JSON，不做分页
        return folder.model_dump_json(indent=2)
    # 非verbose：对树形文本进行行级分页（保持原有显示顺序）
    tree_text = render_content_tree(folder)
    lines = tree_text.splitlines()
    total = len(lines)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 0
    if total_pages > 0:
        current_page = min(max(1, page), total_pages)
        start = (current_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_lines = lines[start:end]
    else:
        current_page = 0
        page_lines = []
    body = "\n---\n" + "\n".join(page_lines) if page_lines else "\n---\nNo content found."
    return body + f"\n---\n页码: {current_page} 总数: {total}"


@mcp.tool(
        description="通过关键词搜索用户在CUHKSZ的指定课程的指定文件夹的指定文件信息"
)
async def search_file_info(
    course_code: Annotated[str, Field(description="课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)")],
    folder: Annotated[str, Field(description="文件夹名称")],
    keyword: Annotated[str, Field(description="关键词")]
) -> str:
    """
    Search file info in course folder by keyword. (Title or Description)
    
    Args:
        course_code: 课程代码(如 CSC3002, CSC代表学科, 3002代表课程编号)
        folder: 文件夹名称
        keyword: 关键词

    Returns:
        str: 文件信息
    """
    try:
        node = await service.find_content(course_code, folder, keyword)
    except CourseLookupError as error:
        return _format_course_not_found(error)
    if node is None:
        return "\n---\nFile not found."
    return "\n---\n" + node.model_dump_json(indent=2)


@mcp.tool(
    description="使用url下载用户在CUHKSZ Blackboard的文件，保存到指定目录"
)
async def download_file(
    url: Annotated[str, Field(description="文件下载链接")],
    name: Annotated[str, Field(description="文件名称")],
    download_dir: Annotated[str | os.PathLike[str], Field(description="保存目录")] = "~"
) -> str:
    """Download file from url."""
    try:
        data, extension = await service.download_file(url, name)
        target_dir = Path(download_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        base_name = Path(name).stem
        file_name = base_name + extension if extension and not name.endswith(extension) else name
        file_path = target_dir / file_name
        await asyncio.to_thread(file_path.write_bytes, data)

        payload = DownloadResult(
            success=True,
            message=f"File downloaded successfully to {file_path}",
            suggested_extension=extension or None,
            file_path=str(file_path),
        )
    except Exception as exc:  # noqa: BLE001
        payload = DownloadResult(success=False, message=str(exc), suggested_extension=None, file_path=None)
    return "\n---\n" + payload.model_dump_json(indent=2)


async def test():
    print("BB_BASE_URL:", get_settings().bb_base_url)
    while True:
        print("\n请选择要测试的功能：")
        print("1. 获取课程列表(fetch_course_list)")
        print("2. 获取待办(fetch_todo)")
        print("3. 获取公告(fetch_announcements)")
        print("4. 获取成绩(fetch_grades)")
        print("5. 获取内容(fetch_content)")
        print("6. 查找具体内容(find_content_detail)")
        print("7. 下载文件(download_file)")
        print("0. 退出")
        choice = input("输入选项编号: ").strip()
        if choice == "1":
            result = await fetch_course_list()
            print(result)
        elif choice == "2":
            page_str = input("页码(默认1): ").strip()
            page_value = int(page_str) if page_str else 1
            result = await fetch_todo(page_value)
            print(result)
        elif choice == "3":
            code = input("课程代码: ").strip()
            page_str = input("页码(默认1): ").strip()
            page_value = int(page_str) if page_str else 1
            result = await fetch_announcements(code, page_value)
            print(result)
        elif choice == "4":
            code = input("课程代码: ").strip()
            page_str = input("页码(默认1): ").strip()
            page_value = int(page_str) if page_str else 1
            result = await fetch_grades(code, page_value)
            print(result)
        elif choice == "5":
            code = input("课程代码: ").strip()
            verbose = input("是否返回详细信息? (y/n): ").strip().lower() == "y"
            page_str = input("页码(默认1): ").strip()
            page_value = int(page_str) if page_str else 1
            result = await fetch_content(code, verbose, page_value)
            print(result)
        elif choice == "6":
            code = input("课程代码: ").strip()
            folder = input("文件夹名称: ").strip()
            content = input("内容名称: ").strip()
            result = await search_file_info(code, folder, content)
            print(result)
        elif choice == "7":
            url = input("文件URL: ").strip()
            name = input("文件名称(含后缀，可选): ").strip() or "downloaded_file"
            download_dir = input("保存目录(默认为当前目录): ").strip() or "."
            result = await download_file(url, name, download_dir)
            print(result)
        elif choice == "0":
            print("退出测试。")
            break
        else:
            print("无效选项，请重新输入。")
    await service.close()


if __name__ == "__main__":
    asyncio.run(test())
