"""
华东交通大学教务系统课程表解析服务
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.models.course import Course, CourseSchedule, DateInfo


def fetch_course_schedule(weiXinID: str, date: str) -> tuple[int, str | None]:
    """
    通过教务系统移动端接口获取指定日期的原始课程表 HTML。

    为了模拟真实的微信环境，我们配置了特定且详尽的请求头（Headers），
    特别是模拟了安卓设备上的微信内置浏览器（XWEB/MicroMessenger），
    以绕过教务系统的环境检测。

    Args:
        weiXinID: 微信用户的唯一标识符，通常取自抓包获取的接口参数。
        date: 查询的目标日期，必须符合 YYYY-MM-DD 格式。

    Returns:
        tuple[int, str | None]: 包含 HTTP 状态码和原始 HTML 文本的元组。
            如果发生网络异常，状态码将是异常中的 code 或 500。
    """
    url = f"https://jwxt.ecjtu.edu.cn/weixin/CalendarServlet?weiXinID={weiXinID}&date={date}"

    headers = {
        # 详尽的 User-Agent，包含微信版本、系统内核、设备型号等，
        # 确保请求模拟真实移动端环境
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20250904 MMWEBID/1666 MicroMessenger/8.0.65.2942(0x28004142) WeChat/arm64 Weixin GPVersion/1 NetType/4G Language/zh_CN ABI/arm64",  # noqa: E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        return response.status_code, response.text
    except requests.RequestException as e:
        status_code = 500
        if e.response is not None:
            status_code = e.response.status_code
        print(f"请求教务系统 URL 出错: {e}")
        return status_code, None


def parse_course_schedule(html_content: str) -> CourseSchedule | None:
    """
    解析教务系统返回的课程表 HTML 文本，转换为结构化的 Pydantic 数据模型。

    解析流程：
    1. 使用 BeautifulSoup 提取页面顶部的日期和周次信息。
    2. 定位到 class='calendar' 的容器，遍历其内部的 <li> 标签。
    3. 利用正则表达式从非结构化文本中提取课程名称、状态、教师、地点及时间。
    4. 对时间字符串进行二次解析，提取出具体的周次范围列表和节次数字。

    Args:
        html_content: 待解析的 HTML 源码。

    Returns:
        CourseSchedule: 包含日期详情和课程列表的结构化模型。
        如果 HTML 内容为空则返回 None。
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. 解析日期和周次信息
    # 页面结构中，日期通常包含在 class='center' 的 div 下的 p 标签内
    date_div = soup.find("div", class_="center")
    date_info = {"date": None, "day_of_week": None, "week_info": None}

    if date_div and (p_tag := date_div.find("p")):
        raw_date_str = p_tag.get_text(strip=True)
        # 通常格式为："2026-01-05 星期一 (第17周)"
        parts = raw_date_str.split(" ", 1)
        if len(parts) >= 1:
            date_info["date"] = parts[0]

        if len(parts) >= 2:
            rest = parts[1]
            # 捕获周次和星期几，支持全角和半角括号
            # 模式解释：匹配非括号内容作为星期，然后捕获括号内的数字周次
            match = re.search(r"([^（(]+)[（(]第?(\d+)周[）)]", rest)
            if match:
                date_info["day_of_week"] = match.group(1).strip()
                date_info["week_info"] = match.group(2)
            else:
                date_info["day_of_week"] = rest.strip()

    # 2. 解析具体的课程列表
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
                """提取冒号后的实际值"""
                return line.replace("：", ":").split(":", 1)[-1].strip()

            # 获取 li 下所有的文本行并清洗
            lines = [line.strip() for line in item.stripped_strings if line.strip()]

            # 排除页面上显示的重复节次标签
            period_span = p.find("span", class_="class_span")
            period_label = period_span.get_text(strip=True) if period_span else ""
            lines = [line for line in lines if line != period_label]

            found_name = False
            for line in lines:
                # 3. 提取时间及周次节次
                if line.startswith(("时间", "时间:")):
                    time_val = clean_val(line)
                    course_info["time"] = time_val
                    try:
                        # 原始格式通常为："1-17周 1,2节" 或 "1,3,5周 3,4节"
                        t_parts = time_val.split(" ")
                        if len(t_parts) == 2:
                            # 提取周次
                            weeks_part = t_parts[0].replace("，", ",")
                            for w_range in weeks_part.split(","):
                                if "-" in w_range:
                                    w_start, w_end = w_range.split("-", 1)
                                    course_info["weeks"].append(
                                        [int(w_start), int(w_end)]
                                    )
                                elif w_range.strip():
                                    course_info["weeks"].append([int(w_range)])

                            # 提取节次
                            periods_part = t_parts[1].replace("，", ",")
                            course_info["periods"] = [
                                int(p_p)
                                for p_p in periods_part.split(",")
                                if p_p.strip()
                            ]
                    except (ValueError, IndexError):
                        pass

                # 4. 提取地点和教师
                elif line.startswith(("地点", "地点:")):
                    course_info["location"] = clean_val(line)
                elif line.startswith(("教师", "教师:")):
                    course_info["teacher"] = clean_val(line)

                # 5. 提取课程名和状态
                # 通常作为第一行显示，格式如："高等数学(上课)"
                elif not found_name:
                    # 匹配末尾带括号的状态信息
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


def save_to_local(
    target_date: str, html_content: str, parsed_data: CourseSchedule | dict
):
    """
    将抓取的原始 HTML 网页和解析后的结构化 JSON 数据保存到本地 Data 目录。

    用于数据归档以及离线调试。

    Args:
        target_date: 目标日期字符串，用作文件名。
        html_content: 原始 HTML 内容。
        parsed_data: 解析后的数据，支持 Pydantic 模型或字典。
    """
    out_dir = settings.DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 保存原始 HTML
    if html_content:
        with open(out_dir / f"{target_date}.html", mode="w", encoding="utf-8") as f:
            f.write(html_content)

    # 保存结构化 JSON
    if parsed_data:
        data_to_save = (
            parsed_data.model_dump()
            if isinstance(parsed_data, CourseSchedule)
            else parsed_data
        )
        with open(out_dir / f"{target_date}.json", mode="w", encoding="utf-8") as f:
            f.write(json.dumps(data_to_save, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # 本地调试运行逻辑
    target_date = "2026-01-05"
    print(f"正在从教务系统抓取 {target_date} 的课程表...")
    status_code, html_content = fetch_course_schedule(settings.WEIXIN_ID, target_date)
    if status_code == 200 and html_content:
        parsed_data = parse_course_schedule(html_content)
        save_to_local(target_date, html_content, parsed_data)
        print("解析成功，结果如下：")
        print(json.dumps(parsed_data.model_dump(), indent=4, ensure_ascii=False))
    else:
        print("获取内容失败，请检查请求头或 WEIXIN_ID 是否有效。")
