"""
华东交通大学教务系统课程表解析服务
"""

import json
import re

from bs4 import BeautifulSoup

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.course import Course, CourseSchedule, DateInfo
from ecjtu_wechat_api.utils.http import get_page
from ecjtu_wechat_api.utils.logger import logger
from ecjtu_wechat_api.utils.persistence import save_debug_data


async def fetch_course_schedule(weiXinID: str, date: str) -> str:
    """
    通过教务系统移动端接口获取指定日期的原始课程表 HTML。

    Args:
        weiXinID: 微信用户的唯一标识符。
        date: 查询的目标日期，必须符合 YYYY-MM-DD 格式。

    Returns:
        str: 原始 HTML 文本。

    Raises:
        EducationSystemError: 请求失败时抛出。
    """
    params = {
        "weiXinID": weiXinID,
        "date": date,
    }

    logger.info(f"正在请求教务系统课程表: weiXinID={weiXinID}, date={date}")
    return await get_page(settings.COURSE_URL, params=params)


def parse_course_schedule(html_content: str) -> CourseSchedule:
    """
    解析课程表 HTML。

    Raises:
        ParseError: 解析失败时抛出。
    """
    if not html_content:
        raise ParseError("HTML 内容为空，无法解析")

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. 提取日期和周次信息
        # 原始片段: <div class="center"><p>2026-01-05 星期一（第19周）</p></div>
        date_div = soup.find("div", class_="center")
        date_info = {"date": None, "day_of_week": None, "week_info": None}

        if date_div and (p_tag := date_div.find("p")):
            raw_date_str = p_tag.get_text(strip=True)
            # 拆分日期 (2026-01-05) 和后续部分 (星期一（第19周）)
            parts = raw_date_str.split(" ", 1)
            if len(parts) >= 1:
                date_info["date"] = parts[0]

            if len(parts) >= 2:
                rest = parts[1]
                # 使用正则匹配星期和周次，支持 "星期一（第19周）" 或 "星期一(19)"
                match = re.search(r"([^（(]+)[（(]第?(\d+)周[）)]", rest)
                if match:
                    date_info["day_of_week"] = match.group(1).strip()
                    date_info["week_info"] = match.group(2)
                else:
                    date_info["day_of_week"] = rest.strip()

        # 2. 遍历课程列表容器 (<div class="calendar"><ul class="rl_info">)
        # 原始 HTML 片段示例:
        # <li><p>
        #     <span class="class_span">3-4节<br /> </span>
        #     大学英语Ⅰ(考试)<br />
        #     时间：19 3,4<br />
        #     地点：进贤2-212<br />
        #     教师：<br />
        # </p></li>
        courses = []
        calendar_div = soup.find("div", class_="calendar")
        if calendar_div and (ul_list := calendar_div.find("ul", class_="rl_info")):
            for item in ul_list.find_all("li"):
                if not (p := item.find("p")):
                    continue

                course_info = {
                    "name": "",
                    "status": "",
                    "time": "",
                    "location": "",
                    "teacher": "",
                    "weeks": [],
                    "periods": [],
                }

                def clean_val(line):
                    return line.replace("：", ":").split(":", 1)[-1].strip()

                # 获取所有文本行并清理空白
                lines = [line.strip() for line in item.stripped_strings if line.strip()]
                # 提取节次快捷标签 (如: "3-4节")
                period_span = p.find("span", class_="class_span")
                period_label = period_span.get_text(strip=True) if period_span else ""
                lines = [line for line in lines if line != period_label]

                found_name = False
                for line in lines:
                    # 2.1 提取时间并解析周次和节次
                    # 原始行示例: "时间：19 3,4" (表示第19周，第3,4节)
                    if line.startswith(("时间", "时间:")):
                        time_val = clean_val(line)
                        course_info["time"] = time_val
                        try:
                            t_parts = time_val.split(" ")
                            if len(t_parts) == 2:
                                # 解析周次范围，支持 "1-18" (Range) 或 "1,3,5" (List)
                                weeks_part = t_parts[0].replace("，", ",")
                                for w_range in weeks_part.split(","):
                                    if "-" in w_range:
                                        w_start, w_end = w_range.split("-", 1)
                                        course_info["weeks"].append(
                                            [int(w_start), int(w_end)]
                                        )
                                    elif w_range.strip():
                                        course_info["weeks"].append([int(w_range)])

                                # 解析具体节次 (如: "3,4")
                                periods_part = t_parts[1].replace("，", ",")
                                course_info["periods"] = [
                                    int(p_p)
                                    for p_p in periods_part.split(",")
                                    if p_p.strip()
                                ]
                        except (ValueError, IndexError):
                            pass
                    # 2.2 提取地点 (原始行示例: "地点：进贤2-212")
                    elif line.startswith(("地点", "地点:")):
                        course_info["location"] = clean_val(line)
                    # 2.3 提取教师 (原始行示例: "教师：张三")
                    elif line.startswith(("教师", "教师:")):
                        course_info["teacher"] = clean_val(line)
                    # 2.4 提取课程名称和考核状态
                    # 原始行示例: "大学英语Ⅰ(考试)"
                    elif not found_name:
                        match = re.search(r"(.+?)[（(]([^（()）]+)[)）]$", line)
                        if match:
                            course_info["name"] = match.group(1).strip()
                            course_info["status"] = match.group(2).strip()
                        else:
                            course_info["name"] = line
                        found_name = True

                if course_info["name"]:
                    courses.append(course_info)

        return CourseSchedule(
            date_info=DateInfo(**date_info) if date_info["date"] else None,
            courses=[Course(**c) for c in courses],
        )
    except Exception as e:
        logger.error(f"解析课程表 HTML 出错: {e}")
        raise ParseError(f"课程表解析失败: {str(e)}") from e


if __name__ == "__main__":
    import asyncio

    async def main():
        # 本地调试运行逻辑
        target_date = "2026-01-05"
        logger.info(f"正在从教务系统抓取 {target_date} 的课程表...")
        try:
            html_content = await fetch_course_schedule(settings.WEIXIN_ID, target_date)
            parsed_data = parse_course_schedule(html_content)
            save_debug_data("courses", target_date, html_content, parsed_data)
            logger.info("解析成功，结果已保存。")
            print(json.dumps(parsed_data.model_dump(), indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"运行失败: {e}")

    asyncio.run(main())
