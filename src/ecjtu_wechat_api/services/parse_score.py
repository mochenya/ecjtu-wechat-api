"""
华东交通大学教务系统成绩查询解析服务
"""

import json
import re
from contextlib import suppress

from bs4 import BeautifulSoup

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.score import ScoreItem, StudentScoreInfo, TermItem
from ecjtu_wechat_api.utils.http import get_page
from ecjtu_wechat_api.utils.logger import logger
from ecjtu_wechat_api.utils.persistence import save_debug_data


async def fetch_score_info(weiXinID: str, term: str | None = None) -> str:
    """
    通过教务系统移动端接口获取成绩 HTML。

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

    logger.info(f"正在请求教务系统成绩: weiXinID={weiXinID}, term={term or 'current'}")
    return await get_page(settings.SCORE_URL, params=params)


def parse_score_info(html_content: str) -> StudentScoreInfo:
    """
    解析成绩页面 HTML。

    Raises:
        ParseError: 解析失败时抛出。
    """
    if not html_content:
        raise ParseError("HTML 内容为空，无法解析")

    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. 提取学生姓名和当前查询学期
        # 原始片段:
        # <div class="right">姓名:<span>张三</span><br />学期:<span>2025.1</span></div>
        right_div = soup.find("div", class_="right")
        student_name = ""
        current_term = ""
        if right_div:
            spans = right_div.find_all("span")
            if len(spans) >= 2:
                student_name = spans[0].get_text(strip=True)
                current_term = spans[1].get_text(strip=True)

        # 2. 提取下拉菜单中的可选学期列表
        # 原始片段: <li><a href="/ScoreQuery?term=2025.2">2025.2</a></li>
        available_terms = []
        term_ul = soup.find("ul", class_="dropdown-menu")
        if term_ul:
            for li in term_ul.find_all("li"):
                a = li.find("a")
                if a:
                    available_terms.append(
                        TermItem(name=a.get_text(strip=True), url=a.get("href", ""))
                    )

        # 3. 提取成绩汇总数量
        # 原始片段: <div class="words">共有<strong>3</strong>门考试成绩。</div>
        score_count = 0
        words_div = soup.find("div", class_="words")
        if words_div and (strong := words_div.find("strong")):
            with suppress(ValueError):
                score_count = int(strong.get_text(strip=True))

        # 4. 遍历并提取具体课程成绩 (<div class="row">)
        # 原始片段:
        # <div class="row"><div class="text">
        #     <span class="course">【主修】【1500190200】军事技能(学分:1.0)</span>
        #     <div class="grade">期末成绩:<span class="score">合格</span>...</div>
        # </div></div>
        scores = []
        for row in soup.find_all("div", class_="row"):
            text_div = row.find("div", class_="text")
            if not text_div:
                continue

            # 4.1 提取原始课程信息文本
            # 格式示例: "【主修】【1500190200】军事技能(学分:1.0)"
            course_span = text_div.find("span", class_="course")
            if not course_span:
                continue

            raw_course_text = course_span.get_text(strip=True)
            # 提取学分 (如: 1.0)
            credit = 0.0
            credit_match = re.search(r"\(学分:([\d.]+)\)", raw_course_text)
            if credit_match:
                with suppress(ValueError):
                    credit = float(credit_match.group(1))

            # 使用正则解析课程修读类型、代码和名称
            # 模式解释: 匹配 【类型】【代码】名称
            name_match = re.search(r"【(.*?)】【(.*?)】(.*?)(?:\(|$)", raw_course_text)
            major = name_match.group(1) if name_match else None
            course_code = name_match.group(2) if name_match else None
            course_name = name_match.group(3).strip() if name_match else raw_course_text

            # 4.2 提取各项具体成绩
            # 原始片段: 期末成绩:<span class="score">85</span>...
            grade_div = text_div.find("div", class_="grade")
            final_score = ""
            reexam_score = None
            retake_score = None
            if grade_div:
                score_spans = grade_div.find_all("span", class_="score")
                # 页面通常按顺序排列: 0:期末, 1:重考, 2:重修
                if len(score_spans) >= 1:
                    final_score = score_spans[0].get_text(strip=True)
                if len(score_spans) >= 2:
                    reexam_score = score_spans[1].get_text(strip=True) or None
                if len(score_spans) >= 3:
                    retake_score = score_spans[2].get_text(strip=True) or None

            # 4.3 提取课程性质 (如: 必修课, 选修课)
            # 原始片段:
            # <div class="type"><span class="require"><mark>必修课</mark></span></div>
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
    except Exception as e:
        logger.error(f"解析成绩 HTML 出错: {e}")
        raise ParseError(f"成绩解析失败: {str(e)}") from e


if __name__ == "__main__":
    import asyncio

    async def main():
        # 本地调试运行逻辑
        logger.info("正在从教务系统抓取成绩...")
        try:
            html_content = await fetch_score_info(settings.WEIXIN_ID)
            parsed_data = parse_score_info(html_content)
            # 保存到本地归档
            save_debug_data(
                "scores",
                f"{parsed_data.student_name}_{parsed_data.current_term}",
                html_content,
                parsed_data,
            )
            logger.info("解析成功，结果已保存。")
            print(json.dumps(parsed_data.model_dump(), indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f"运行失败: {e}")

    asyncio.run(main())
