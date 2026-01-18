"""
考试服务补充测试模块
"""

import pytest

from ecjtu_wechat_api.core.exceptions import EducationSystemError, ParseError
from ecjtu_wechat_api.models.exam import ExamSchedule
from ecjtu_wechat_api.services.parse_exam import (
    fetch_exam_schedule,
    parse_exam_schedule,
)

# 测试 fetch 函数
SAMPLE_HTML_EXAM = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>张三</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <mark>2</mark>门考试。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <div class="course"><mark>C语言程序设计</mark></div>
                    <u>第18周</u>
                    <u>
                        2026年01月08日(星期四)14:00-16:00
                    </u>
                    <u>教1-101</u>
                    <span>必修课</span>
                    <span>计算机241班</span>
                    <span>45</span>
                </div>
            </div>
        </div>
    </body>
</html>
"""

# 测试不带学期的 HTML
SAMPLE_HTML_NO_TERM = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>李四</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <mark>1</mark>门考试。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <div class="course"><mark>高等数学</mark></div>
                    <u>第19周</u>
                    <u>
                        2026年01月10日(星期六)09:00-11:00
                    </u>
                    <u>教2-201</u>
                    <span>必修课</span>
                    <span>计算机241班</span>
                    <span>45</span>
                </div>
            </div>
        </div>
    </body>
</html>
"""


# fetch 函数测试
@pytest.mark.asyncio
async def test_fetch_exam_schedule_success(mocker):
    """测试成功获取考试安排"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML_EXAM
    mock_response.encoding = "utf-8"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    result = await fetch_exam_schedule("test_id", "2025.1")

    assert "C语言程序设计" in result
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_exam_schedule_without_term(mocker):
    """测试不带学期参数获取考试安排"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML_NO_TERM
    mock_response.encoding = "utf-8"

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    result = await fetch_exam_schedule("test_id", None)

    assert "高等数学" in result
    # 验证没有传递 term 参数
    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["weiXinID"] == "test_id"
    assert "term" not in call_args[1]["params"]


@pytest.mark.asyncio
async def test_fetch_exam_schedule_network_error(mocker):
    """测试网络错误"""
    import httpx

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get = mocker.AsyncMock(side_effect=httpx.RequestError("Network error"))

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await fetch_exam_schedule("test_id", "2025.1")


# parse 函数测试
def test_parse_exam_schedule_success():
    """测试成功解析考试安排"""
    result = parse_exam_schedule(SAMPLE_HTML_EXAM)

    assert isinstance(result, ExamSchedule)
    assert result.student_name == "张三"
    assert result.current_term == "2025.1"
    assert result.exam_count == 2
    assert len(result.exams) == 1

    exam = result.exams[0]
    assert exam.course_name == "C语言程序设计"
    assert exam.week == "第18周"
    assert exam.exam_date == "2026年01月08日"
    assert exam.day_of_week == "星期四"
    assert exam.time_range == "14:00-16:00"
    assert exam.time_start == "14:00"
    assert exam.time_end == "16:00"
    assert exam.location == "教1-101"
    assert exam.course_type == "必修课"
    assert exam.class_name == "计算机241班"
    assert exam.exam_count_num == 45


def test_parse_exam_schedule_empty_html():
    """测试空 HTML 抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_exam_schedule("")


def test_parse_exam_schedule_none_html():
    """测试 None 输入抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_exam_schedule(None)
