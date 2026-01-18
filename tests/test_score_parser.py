"""
成绩解析服务测试模块
"""

import pytest

from ecjtu_wechat_api.core.exceptions import ParseError
from ecjtu_wechat_api.models.score import StudentScoreInfo
from ecjtu_wechat_api.services.parse_score import parse_score_info

# 正常场景：完整 HTML 样本
SAMPLE_HTML_COMPLETE = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            姓名:
            <span>张三</span>
            <br />
            当前学期:
            <span>2025.1</span>
        </div>
        <ul class="dropdown-menu dropdown-menu-left btn-block" role="menu">
            <li>
                <a href="/weixin/ScoreQuery?weiXinID=xxx&amp;term=2025.1"
                   role="menuitem">2025.1</a>
            </li>
            <li>
                <a href="/weixin/ScoreQuery?weiXinID=xxx&amp;term=2024.2"
                   role="menuitem">2024.2</a>
            </li>
        </ul>
        <div class="words">
            您好！本学期当前你共有
            <strong>2</strong>门考试成绩。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【1500190200】军事技能(学分:1.0)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">合格</span>
                        <br />
                        重考成绩:
                        <span class="score"></span>
                        <br />
                        重修成绩:
                        <span class="score"></span>
                        <br />
                        <span class="flag">主修</span>
                    </div>
                </div>
                <div class="img">
                    <img src="/weixin/imgs/myschedule/dian.png;jsessionid=xxx">
                </div>
                <div class="type">
                    <span class="require"><mark>必修课</mark> </span>
                </div>
            </div>
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【1234567890】高等数学(学分:5.0)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">90</span>
                        <br />
                        重考成绩:
                        <span class="score"></span>
                        <br />
                        重修成绩:
                        <span class="score"></span>
                        <br />
                        <span class="flag">主修</span>
                    </div>
                </div>
                <div class="type">
                    <span class="require"><mark>必修课</mark> </span>
                </div>
            </div>
        </div>
    </body>
</html>
"""

# 包含重考成绩的 HTML
SAMPLE_HTML_WITH_REEXAM = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>李四</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <strong>1</strong>门考试成绩。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【1111111111】大学英语(学分:3.0)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">55</span>
                        <br />
                        重考成绩:
                        <span class="score">60</span>
                        <br />
                        重修成绩:
                        <span class="score"></span>
                    </div>
                </div>
                <div class="type">
                    <mark>必修课</mark>
                </div>
            </div>
        </div>
    </body>
</html>
"""

# 包含重修成绩的 HTML
SAMPLE_HTML_WITH_RETAKE = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>王五</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <strong>1</strong>门考试成绩。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【2222222222】程序设计(学分:4.0)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">45</span>
                        <br />
                        重考成绩:
                        <span class="score"></span>
                        <br />
                        重修成绩:
                        <span class="score">75</span>
                    </div>
                </div>
                <div class="type">
                    <mark>选修课</mark>
                </div>
            </div>
        </div>
    </body>
</html>
"""

# 无成绩的 HTML
SAMPLE_HTML_EMPTY_SCORES = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>赵六</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <strong>0</strong>门考试成绩。
        </div>
    </body>
</html>
"""

# 缺少学生姓名的 HTML
SAMPLE_HTML_NO_STUDENT_NAME = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            姓名:
            <span></span>
            <br />
            当前学期:
            <span>2025.1</span>
        </div>
        <div class="words">
            <strong>1</strong>门考试成绩。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【3333333333】计算机基础(学分:
                        2.5)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">85</span>
                        <br />
                        重考成绩:
                        <span class="score"></span>
                        <br />
                        重修成绩:
                        <span class="score"></span>
                    </div>
                </div>
                <div class="type">
                    <mark>必修课</mark>
                </div>
            </div>
        </div>
    </body>
</html>
"""

# 整数学分
SAMPLE_HTML_INTEGER_CREDIT = """
<!DOCTYPE html>
<html>
    <body>
        <div class="right">
            <span>孙七</span>
            <span>2025.1</span>
        </div>
        <div class="words">
            <strong>1</strong>门考试成绩。
        </div>
        <div class="row ">
            <div class="col-xs-12">
                <div class="text">
                    <span class="course">【主修】【4444444444】体育(学分:2)</span>
                    <div class="grade">
                        期末成绩:
                        <span class="score">通过</span>
                        <br />
                        重考成绩:
                        <span class="score"></span>
                        <br />
                        重修成绩:
                        <span class="score"></span>
                    </div>
                </div>
                <div class="type">
                    <mark>必修课</mark>
                </div>
            </div>
        </div>
    </body>
</html>
"""


# 正常场景测试
def test_parse_score_info_success():
    """测试完整 HTML 样本的正常解析"""
    result = parse_score_info(SAMPLE_HTML_COMPLETE)

    # 类型断言
    assert isinstance(result, StudentScoreInfo)

    # 基本字段断言
    assert result.student_name == "张三"
    assert result.current_term == "2025.1"
    assert result.score_count == 2

    # 可选学期列表断言
    assert len(result.available_terms) == 2
    assert result.available_terms[0].name == "2025.1"
    assert result.available_terms[1].name == "2024.2"

    # 成绩列表断言
    assert len(result.scores) == 2

    # 第一门课程
    course1 = result.scores[0]
    assert course1.course_name == "军事技能"
    assert course1.course_code == "1500190200"
    assert course1.final_score == "合格"
    assert course1.reexam_score is None
    assert course1.retake_score is None
    assert course1.course_type == "必修课"
    assert course1.credit == 1.0
    assert course1.major == "主修"

    # 第二门课程
    course2 = result.scores[1]
    assert course2.course_name == "高等数学"
    assert course2.course_code == "1234567890"
    assert course2.final_score == "90"
    assert course2.credit == 5.0


def test_parse_score_info_multiple_courses():
    """测试多门课程成绩解析"""
    result = parse_score_info(SAMPLE_HTML_COMPLETE)

    assert len(result.scores) == 2

    # 验证所有课程都有必要字段
    for score in result.scores:
        assert score.course_name
        assert score.course_code
        assert score.final_score
        assert score.course_type
        assert score.major


def test_parse_score_info_with_reexam():
    """测试包含重考成绩的课程解析"""
    result = parse_score_info(SAMPLE_HTML_WITH_REEXAM)

    assert len(result.scores) == 1
    course = result.scores[0]

    assert course.course_name == "大学英语"
    assert course.final_score == "55"
    assert course.reexam_score == "60"
    assert course.retake_score is None


def test_parse_score_info_with_retake():
    """测试包含重修成绩的课程解析"""
    result = parse_score_info(SAMPLE_HTML_WITH_RETAKE)

    assert len(result.scores) == 1
    course = result.scores[0]

    assert course.course_name == "程序设计"
    assert course.final_score == "45"
    assert course.reexam_score is None
    assert course.retake_score == "75"


# 边界场景测试
def test_parse_score_info_empty_scores():
    """测试无成绩的 HTML 解析"""
    result = parse_score_info(SAMPLE_HTML_EMPTY_SCORES)

    assert result.student_name == "赵六"
    assert result.score_count == 0
    assert len(result.scores) == 0


def test_parse_score_info_missing_student_name():
    """测试缺少学生姓名的 HTML 解析"""
    result = parse_score_info(SAMPLE_HTML_NO_STUDENT_NAME)

    assert result.student_name == ""
    assert result.current_term == "2025.1"
    assert len(result.scores) == 1


def test_parse_score_info_parse_credit_variations():
    """测试不同格式的学分解析（整数和浮点数）"""
    # 测试整数学分
    result_int = parse_score_info(SAMPLE_HTML_INTEGER_CREDIT)
    assert result_int.scores[0].credit == 2.0

    # 测试浮点数学分
    result_float = parse_score_info(SAMPLE_HTML_COMPLETE)
    assert result_float.scores[0].credit == 1.0
    assert result_float.scores[1].credit == 5.0


# 异常场景测试
def test_parse_score_info_empty_html():
    """测试空 HTML 抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_score_info("")


def test_parse_score_info_none_html():
    """测试 None 输入抛出 ParseError"""
    with pytest.raises(ParseError, match="HTML 内容为空"):
        parse_score_info(None)
