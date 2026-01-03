import pytest

from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.course import CourseSchedule
from ecjtu_wechat_api.services.parse_course import parse_course_schedule

SAMPLE_HTML = """
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
                <li>
                    <p>
                        <span class="class_span">5-6节<br /> </span>
                        高等数学(A)Ⅰ(上课)
                        <br />
                        时间：1-19 5,6
                        <br />
                        地点：进贤2-309
                        <br />
                        教师：李四
                        <br />
                    </p>
                </li>
            </ul>
        </div>
    </body>
</html>
"""


def test_parse_course_schedule():
    result = parse_course_schedule(SAMPLE_HTML)

    assert isinstance(result, CourseSchedule)
    assert result.date_info is not None
    assert result.date_info.date == "2026-01-05"
    assert result.date_info.day_of_week == "星期一"
    assert result.date_info.week_info == "19"

    assert len(result.courses) == 2

    # Test first course (Exam)
    course1 = result.courses[0]
    assert course1.name == "大学英语Ⅰ"
    assert course1.status == "考试"
    assert course1.location == "进贤2-212"
    assert course1.teacher == "张三"
    assert course1.periods == [3, 4]
    assert course1.weeks == [[19]]

    # Test second course (Class)
    course2 = result.courses[1]
    assert course2.name == "高等数学(A)Ⅰ"
    assert course2.status == "上课"
    assert course2.location == "进贤2-309"
    assert course2.teacher == "李四"
    assert course2.periods == [5, 6]
    assert course2.weeks == [[1, 19]]


def test_parse_empty_html():
    with pytest.raises(ParseError):
        parse_course_schedule("")
    with pytest.raises(ParseError):
        parse_course_schedule(None)
