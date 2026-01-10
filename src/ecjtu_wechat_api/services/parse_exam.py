"""
华东交通大学教务系统考试安排解析服务
"""

import json
import re
from contextlib import suppress

from bs4 import BeautifulSoup

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.exam import ExamItem, ExamSchedule, ExamTermItem
from ecjtu_wechat_api.utils.http import get_page
from ecjtu_wechat_api.utils.logger import logger
from ecjtu_wechat_api.utils.persistence import save_debug_data


async def fetch_exam_schedule(weiXinID: str, term: str | None = None) -> str:
    """
    通过教务系统移动端接口获取考试安排 HTML。

    Args:
        weiXinID: 微信用户的唯一标识符。
        term: 查询的学期，如 "2025.1"。如果为 None，则获取当前学期。

    Returns:
        str: 原始 HTML 文本。

    Raises:
        EducationSystemError: 请求失败时抛出。
    """
    params = {
        "weiXinID": weiXinID,
    }
    if term:
        params["term"] = term

    logger.info(
        f"正在请求教务系统考试安排: weiXinID={weiXinID}, term={term or 'current'}"
    )
    return await get_page(settings.EXAM_URL, params=params)


def parse_exam_schedule(html_content: str) -> ExamSchedule:
    """
    解析考试安排页面 HTML。

    Raises:
        ParseError: 解析失败时抛出。
    """
    if not html_content:
        raise ParseError("HTML 内容为空，无法解析")

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. 提取学生姓名和当前查询学期
        right_div = soup.find("div", class_="right")
        student_name = ""
        current_term = ""
        if right_div:
            spans = right_div.find_all("span")
            if len(spans) >= 2:
                student_name = spans[0].get_text(strip=True)
                current_term = spans[1].get_text(strip=True)

        # 2. 提取下拉菜单中的可选学期列表
        available_terms = []
        term_ul = soup.find("ul", class_="dropdown-menu")
        if term_ul:
            for li in term_ul.find_all("li"):
                a = li.find("a")
                if a:
                    available_terms.append(
                        ExamTermItem(name=a.get_text(strip=True), url=a.get("href", ""))
                    )

        # 3. 提取考试汇总数量
        exam_count = 0
        words_div = soup.find("div", class_="words")
        if words_div and (mark := words_div.find("mark")):
            with suppress(ValueError):
                exam_count = int(mark.get_text(strip=True))

        # 4. 遍历并提取具体考试安排 (<div class="row">)
        # 原始片段包含考试周次、时间（含红色备注 div）、地点、性质、班级、人数等
        exams = []
        for row in soup.find_all("div", class_="row"):
            text_div = row.find("div", class_="text")
            if not text_div:
                continue

            # 4.1 提取课程名称（来自 course div 中的 mark 标签）
            # 原始片段: <div class="course"><mark>C语言程序设计</mark></div>
            course_name = ""
            course_div = row.find("div", class_="course")
            if course_div and (mark := course_div.find("mark")):
                course_name = mark.get_text(strip=True)

            if not course_name:
                continue

            # 4.2 提取各个字段（u 标签内为数据，span 标签内为数据）
            # HTML 结构固定: 考试周次<u> 考试时间<u> 考试地点<u> 课程性质<span> ...
            week = ""
            location = ""
            course_type = ""
            class_name = ""
            exam_count_num_str = ""
            exam_date = ""
            day_of_week = ""
            time_range = ""
            time_start = ""
            time_end = ""
            note = ""

            # 查找所有 u 和 span 标签，按顺序提取
            u_tags = text_div.find_all("u")
            span_tags = text_div.find_all("span")

            # u_tags[0]: 考试周次, u_tags[1]: 考试时间, u_tags[2]: 考试地点
            if len(u_tags) >= 1:
                week = u_tags[0].get_text(strip=True)
            if len(u_tags) >= 2:
                time_u = u_tags[1]
                # 提取红色提示文字（备注）
                note_div = time_u.find("div")
                if note_div:
                    note = note_div.get_text(strip=True)
                # 提取纯文本时间部分（去除 div 标签）
                time_parts = []
                for content in time_u.contents:
                    if hasattr(content, "name") and content.name == "div":
                        continue
                    text_content = (
                        content.get_text(strip=True)
                        if hasattr(content, "get_text")
                        else str(content).strip()
                    )
                    if text_content:
                        time_parts.append(text_content)
                time_text = "".join(time_parts)
                # 使用正则拆分时间文本
                # 模式: 2026年01月08日(星期四)14:00-16:00
                time_pattern = (
                    r"(\d{4}年\d{2}月\d{2}日)\((.*?)\)(\d{2}:\d{2}-\d{2}:\d{2})"
                )
                time_match = re.search(time_pattern, time_text)
                if time_match:
                    exam_date = time_match.group(1)
                    day_of_week = time_match.group(2)
                    time_range = time_match.group(3)
                    # 拆分开始和结束时间
                    if "-" in time_range:
                        time_start, time_end = time_range.split("-", 1)
                    else:
                        time_start, time_end = "", ""
                else:
                    exam_date = time_text
                    time_start, time_end = "", ""
            if len(u_tags) >= 3:
                location = u_tags[2].get_text(strip=True)

            # span_tags[0]: 课程性质, span_tags[1]: 班级名称, span_tags[2]: 考试人数
            if len(span_tags) >= 1:
                course_type = span_tags[0].get_text(strip=True)
            if len(span_tags) >= 2:
                class_name = span_tags[1].get_text(strip=True)
            if len(span_tags) >= 3:
                exam_count_num_str = span_tags[2].get_text(strip=True)
            exam_count_num = 0
            with suppress(ValueError):
                exam_count_num = int(exam_count_num_str)

            exams.append(
                ExamItem(
                    course_name=course_name,
                    week=week,
                    exam_date=exam_date,
                    day_of_week=day_of_week,
                    time_range=time_range,
                    time_start=time_start,
                    time_end=time_end,
                    location=location,
                    course_type=course_type,
                    class_name=class_name,
                    exam_count_num=exam_count_num,
                    note=note,
                )
            )

        return ExamSchedule(
            student_name=student_name,
            current_term=current_term,
            available_terms=available_terms,
            exam_count=exam_count,
            exams=exams,
        )
    except Exception as e:
        logger.error(f"解析考试安排 HTML 出错: {e}")
        raise ParseError(f"考试安排解析失败: {str(e)}") from e


if __name__ == "__main__":
    import asyncio

    async def main():
        # 本地调试运行逻辑
        logger.info("正在从教务系统抓取考试安排...")
        try:
            html_content = await fetch_exam_schedule(settings.WEIXIN_ID)
            parsed_data = parse_exam_schedule(html_content)
            # 保存到本地归档
            save_debug_data(
                "exams",
                f"{parsed_data.student_name}_{parsed_data.current_term}",
                html_content,
                parsed_data,
            )
            logger.info("解析成功，结果已保存。")
            print(json.dumps(parsed_data.model_dump(), indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"运行失败: {e}")

    asyncio.run(main())
