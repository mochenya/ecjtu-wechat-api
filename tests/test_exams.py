import pytest

from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.exam import ExamSchedule
from ecjtu_wechat_api.services.parse_exam import parse_exam_schedule

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            姓名:<span>张三</span>
            <br />
            当前学期:<span>2025.1</span>
        </div>

        <ul class="dropdown-menu">
            <li><a href="/weixin/ExamArrangeCl?weiXinID=xxx&term=2025.2">2025.2</a></li>
            <li><a href="/weixin/ExamArrangeCl?weiXinID=xxx&term=2025.1">2025.1</a></li>
        </ul>

        <div class="words">
            您好！本学期你共有 <mark>3</mark> 门考试安排。
        </div>

        <div class="row">
            <div class="col-xs-12">
                <div class="text">
                    考试周次:<u>19</u>
                    <br />
                    考试时间:<u>2026年01月08日(星期四)14:00-16:00<br/>
                    <div style='color:red'>携带学生证</div></u>
                    <br />
                    考试地点:<u>进贤1-502</u>
                    <br />
                    课程性质:<span>必修课</span>
                    <br />
                    班级名称:<span>C语言程序设计(20251-5)【小2班】</span>
                    <br />
                    考试人数:<span>29</span>
                    <br />
                </div>
                <div class="course">
                    <mark>C语言程序设计</mark>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-xs-12">
                <div class="text">
                    考试周次:<u>20</u>
                    <br />
                    考试时间:<u>2026年01月10日(星期六)09:00-11:00<br/>
                    <div style='color:red'></div></u>
                    <br />
                    考试地点:<u>进贤2-301</u>
                    <br />
                    课程性质:<span>选修课</span>
                    <br />
                    班级名称:<span>高等数学(20251-1)【大1班】</span>
                    <br />
                    考试人数:<span>35</span>
                    <br />
                </div>
                <div class="course">
                    <mark>高等数学</mark>
                </div>
            </div>
        </div>
    </body>
</html>
"""


def test_parse_exam_schedule():
    result = parse_exam_schedule(SAMPLE_HTML)

    assert isinstance(result, ExamSchedule)
    assert result.student_name == "张三"
    assert result.current_term == "2025.1"
    assert result.exam_count == 3

    # 检查可选学期
    assert len(result.available_terms) == 2
    assert result.available_terms[0].name == "2025.2"
    assert "ExamArrangeCl" in result.available_terms[0].url
    assert result.available_terms[1].name == "2025.1"

    # 检查考试列表
    assert len(result.exams) == 2

    # 第一个考试（包含红色提示）
    exam1 = result.exams[0]
    assert exam1.course_name == "C语言程序设计"
    assert exam1.week == "19"
    assert exam1.exam_date == "2026年01月08日"
    assert exam1.day_of_week == "星期四"
    assert exam1.time_range == "14:00-16:00"
    assert exam1.time_start == "14:00"
    assert exam1.time_end == "16:00"
    assert exam1.location == "进贤1-502"
    assert exam1.course_type == "必修课"
    assert exam1.class_name == "C语言程序设计(20251-5)【小2班】"
    assert exam1.exam_count_num == 29
    assert exam1.note == "携带学生证"

    # 第二个考试（无红色提示）
    exam2 = result.exams[1]
    assert exam2.course_name == "高等数学"
    assert exam2.week == "20"
    assert exam2.exam_date == "2026年01月10日"
    assert exam2.day_of_week == "星期六"
    assert exam2.time_range == "09:00-11:00"
    assert exam2.time_start == "09:00"
    assert exam2.time_end == "11:00"
    assert exam2.location == "进贤2-301"
    assert exam2.course_type == "选修课"
    assert exam2.exam_count_num == 35
    assert exam2.note == ""


def test_parse_empty_html():
    with pytest.raises(ParseError):
        parse_exam_schedule("")
    with pytest.raises(ParseError):
        parse_exam_schedule(None)
