"""
华东交通大学教务系统成绩查询解析服务
"""

import json
import re
from contextlib import suppress

import requests
from bs4 import BeautifulSoup

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.models.score import ScoreItem, StudentScoreInfo, TermItem


def fetch_score_info(weiXinID: str, term: str | None = None) -> tuple[int, str | None]:
    """
    通过教务系统移动端接口获取成绩 HTML。

    Args:
        weiXinID: 微信用户的唯一标识符。
        term: 查询的学期，如 "2025.1"。如果为 None，则获取当前学期。

    Returns:
        tuple[int, str | None]: 包含 HTTP 状态码和原始 HTML 文本的元组。
    """
    url = "https://jwxt.ecjtu.edu.cn/weixin/ScoreQuery"
    params = {
        "weiXinID": weiXinID,
    }
    if term:
        params["term"] = term

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20250904 MMWEBID/1666 MicroMessenger/8.0.65.2942(0x28004142) WeChat/arm64 Weixin GPVersion/1 NetType/4G Language/zh_CN ABI/arm64",  # noqa: E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.encoding = "utf-8"
        return response.status_code, response.text
    except requests.RequestException as e:
        status_code = 500
        if e.response is not None:
            status_code = e.response.status_code
        print(f"请求教务系统获取成绩出错: {e}")
        return status_code, None


def parse_score_info(html_content: str) -> StudentScoreInfo | None:
    """
    解析成绩页面 HTML。
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. 解析姓名和当前学期
    right_div = soup.find("div", class_="right")
    student_name = ""
    current_term = ""
    if right_div:
        spans = right_div.find_all("span")
        if len(spans) >= 2:
            student_name = spans[0].get_text(strip=True)
            current_term = spans[1].get_text(strip=True)

    # 2. 解析可查学期列表
    available_terms = []
    term_ul = soup.find("ul", class_="dropdown-menu")
    if term_ul:
        for li in term_ul.find_all("li"):
            a = li.find("a")
            if a:
                available_terms.append(
                    TermItem(name=a.get_text(strip=True), url=a.get("href", ""))
                )

    # 3. 解析成绩数量
    score_count = 0
    words_div = soup.find("div", class_="words")
    if words_div and (strong := words_div.find("strong")):
        with suppress(ValueError):
            score_count = int(strong.get_text(strip=True))

    # 4. 解析具体成绩
    scores = []
    for row in soup.find_all("div", class_="row"):
        text_div = row.find("div", class_="text")
        if not text_div:
            continue

        course_span = text_div.find("span", class_="course")
        if not course_span:
            continue

        raw_course_text = course_span.get_text(strip=True)
        # 格式示例：【主修】【1500190211】专业创新创业实践Ⅰ(学分:0.5)
        # 提取括号中的学分
        credit = 0.0
        credit_match = re.search(r"\(学分:([\d.]+)\)", raw_course_text)
        if credit_match:
            with suppress(ValueError):
                credit = float(credit_match.group(1))

        # 提取课程名称和代码
        # 模式解释：匹配【类型】【代码】名称
        name_match = re.search(r"【(.*?)】【(.*?)】(.*?)(?:\(|$)", raw_course_text)
        major = name_match.group(1) if name_match else None
        course_code = name_match.group(2) if name_match else None
        course_name = name_match.group(3).strip() if name_match else raw_course_text

        # 提取成绩
        grade_div = text_div.find("div", class_="grade")
        final_score = ""
        reexam_score = None
        retake_score = None
        if grade_div:
            score_spans = grade_div.find_all("span", class_="score")
            # 通常顺序是：期末，重考，重修
            if len(score_spans) >= 1:
                final_score = score_spans[0].get_text(strip=True)
            if len(score_spans) >= 2:
                reexam_score = score_spans[1].get_text(strip=True) or None
            if len(score_spans) >= 3:
                retake_score = score_spans[2].get_text(strip=True) or None

        # 提取课程类型 (必修/选修)
        course_type = ""
        type_div = row.find("div", class_="type")
        if type_div and (mark := type_div.find("mark")):
            course_type = mark.get_text(strip=True)

        scores.append(
            ScoreItem(
                course_name=course_name,
                course_code=course_code,
                final_score=final_score,
                reexam_score=reexam_score,
                retake_score=retake_score,
                course_type=course_type,
                credit=credit,
                major=major,
            )
        )

    return StudentScoreInfo(
        student_name=student_name,
        current_term=current_term,
        available_terms=available_terms,
        score_count=score_count,
        scores=scores,
    )


def save_score_to_local(
    student_name: str,
    term: str,
    html_content: str,
    parsed_data: StudentScoreInfo | dict,
):
    """
    保存成绩数据到本地。
    """
    out_dir = settings.DATA_DIR / "scores"
    out_dir.mkdir(parents=True, exist_ok=True)

    filename_base = f"{student_name}_{term}"

    # 保存原始 HTML
    if html_content:
        with open(out_dir / f"{filename_base}.html", mode="w", encoding="utf-8") as f:
            f.write(html_content)

    # 保存结构化 JSON
    if parsed_data:
        data_to_save = (
            parsed_data.model_dump()
            if isinstance(parsed_data, StudentScoreInfo)
            else parsed_data
        )
        with open(out_dir / f"{filename_base}.json", mode="w", encoding="utf-8") as f:
            f.write(json.dumps(data_to_save, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # 本地调试运行逻辑
    print("正在从教务系统抓取成绩...")
    # 可以通过 term 参数查询特定学期，默认 None 获取当前学期
    status_code, html_content = fetch_score_info(settings.WEIXIN_ID)
    if status_code == 200 and html_content:
        parsed_data = parse_score_info(html_content)
        if parsed_data:
            # 保存到本地归档
            save_score_to_local(
                parsed_data.student_name,
                parsed_data.current_term,
                html_content,
                parsed_data,
            )
            print("解析成功，结果如下：")
            print(json.dumps(parsed_data.model_dump(), indent=4, ensure_ascii=False))
        else:
            print("解析失败：未能提取到成绩信息")
    else:
        print(
            f"获取内容失败，状态码: {status_code}，请检查请求头或 WEIXIN_ID 是否有效。"
        )
