"""
课程服务补充测试模块
"""

import asyncio
import pytest

from ecjtu_wechat_api.core.exceptions import EducationSystemError, ParseError
from ecjtu_wechat_api.models.course import CourseSchedule
from ecjtu_wechat_api.services.parse_course import (
    fetch_course_schedule,
    parse_course_schedule,
)

# 测试 fetch 函数
SAMPLE_HTML_COURSE = """
<!DOCTYPE html>
<html>
    <body>
        <div class="center">
            <p>2026-01-05 星期一（第19周）</p>
        </div>
        <div class="calendar">
            <ul class="rl_info">
                <li>
                    <p>
                        <span class="class_span">3-4节<br /> </span>
                        大学英语Ⅰ(考试)
                        <br />
                        时间：19 3,4
                        <br />
                        地点：进贤2-212
                        <br />
                        教师：张三
                        <br />
                    </p>
                </li>
            </ul>
        </div>
    </body>
</html>
"""

# 测试不同周次格式的 HTML
SAMPLE_HTML_VARIOUS_WEEK_FORMATS = """
<!DOCTYPE html>
<html>
    <body>
        <div class="center">
            <p>2026-01-06 星期二（第20周）</p>
        </div>
        <div class="calendar">
            <ul class="rl_info">
                <li>
                    <p>
                        <span class="class_span">1-2节<br /> </span>
                        高等数学(上课)
                        <br />
                        时间：1-18 1,2
                        <br />
                        地点：教1-101
                        <br />
                        教师：李四
                        <br />
                    </p>
                </li>
                <li>
                    <p>
                        <span class="class_span">5-6节<br /> </span>
                        程序设计(上课)
                        <br />
                        时间：15,17 5,6
                        <br />
                        地点：机房302
                        <br />
                        教师：王五
                        <br />
                    </p>
                </li>
            </ul>
        </div>
    </body>
</html>
"""

# 测试无课程的 HTML
SAMPLE_HTML_NO_COURSES = """
<!DOCTYPE html>
<html>
    <body>
        <div class="center">
            <p>2026-01-07 星期三（第21周）</p>
        </div>
        <div class="calendar">
            <ul class="rl_info"></ul>
        </div>
    </body>
</html>
"""


@pytest.fixture(autouse=True)
def reset_http_client():
    """每个测试前后重置 HTTP 客户端"""
    from ecjtu_wechat_api.utils.http import close_http_client

    asyncio.run(close_http_client())
    yield
    asyncio.run(close_http_client())


# fetch 函数测试
@pytest.mark.asyncio
async def test_fetch_course_schedule_success(mocker):
    """测试成功获取课程表"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML_COURSE
    mock_response.encoding = "utf-8"

    mock_client_instance = mocker.AsyncMock()
    mock_client_instance.get = mocker.AsyncMock(return_value=mock_response)
    mock_client_instance.aclose = mocker.AsyncMock()

    mocker.patch(
        "ecjtu_wechat_api.utils.http.get_http_client",
        return_value=mock_client_instance,
    )

    result = await fetch_course_schedule("test_id", "2026-01-05")

    assert "2026-01-05" in result
    mock_client_instance.get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_course_schedule_network_error(mocker):
    """测试网络错误"""
    import httpx

    mock_client_instance = mocker.AsyncMock()
    mock_client_instance.get = mocker.AsyncMock(
        side_effect=httpx.RequestError("Network error")
    )
    mock_client_instance.aclose = mocker.AsyncMock()

    mocker.patch(
        "ecjtu_wechat_api.utils.http.get_http_client",
        return_value=mock_client_instance,
    )

    with pytest.raises(EducationSystemError, match="网络请求失败"):
        await fetch_course_schedule("test_id", "2026-01-05")


# parse 函数测试
def test_parse_course_schedule_various_week_formats():
    """测试不同周次格式的解析"""
    result = parse_course_schedule(SAMPLE_HTML_VARIOUS_WEEK_FORMATS)

    assert isinstance(result, CourseSchedule)
    assert result.date_info is not None
    assert result.date_info.date == "2026-01-06"
    assert result.date_info.day_of_week == "星期二"
    assert result.date_info.week_info == "20"

    assert len(result.courses) == 2

    # 第一门课程：周次范围 1-18
    course1 = result.courses[0]
    assert course1.name == "高等数学"
    assert course1.weeks == [[1, 18]]
    assert course1.periods == [1, 2]

    # 第二门课程：单周 15, 17
    course2 = result.courses[1]
    assert course2.name == "程序设计"
    assert course2.weeks == [[15], [17]]
    assert course2.periods == [5, 6]


def test_parse_course_schedule_no_courses():
    """测试无课程的 HTML 解析"""
    result = parse_course_schedule(SAMPLE_HTML_NO_COURSES)

    assert isinstance(result, CourseSchedule)
    assert result.date_info is not None
    assert result.date_info.date == "2026-01-07"
    assert len(result.courses) == 0


def test_parse_course_schedule_empty_html():
    """测试空 HTML 抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_course_schedule("")


def test_parse_course_schedule_none_html():
    """测试 None 输入抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_course_schedule(None)
