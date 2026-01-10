import os
from pathlib import Path

from dotenv import load_dotenv

# 从项目根目录加载 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """
    项目全局配置类，负责管理环境变量加载及路径常量定义。
    """

    # 教务系统绑定的微信用户ID，用于向教务系统请求课程数据
    WEIXIN_ID = os.getenv("WEIXIN_ID")

    # 后端 API 基准地址，默认为本地 6894 端口
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:6894")

    # 项目根目录路径
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

    # 调试运用数据存储目录，用于保存抓取的原始 HTML 和解析后的 JSON。
    DATA_DIR = PROJECT_ROOT / "data"

    # 微信移动端 User-Agent（模拟安卓设备上的微信内置浏览器）
    WECHAT_USER_AGENT = (
        "Mozilla/5.0 (Linux; Android 16; 24129PN74C Build/BP2A.250605.031.A3; wv) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 "
        "Mobile Safari/537.36 XWEB/1160117 MMWEBSDK/20250904 MMWEBID/1666 "
        "MicroMessenger/8.0.65.2942(0x28004142) WeChat/arm64 Weixin GPVersion/1 "
        "NetType/5G Language/zh_CN ABI/arm64"
    )

    # 标准请求头（用于模拟微信环境绕过教务系统检测）
    DEFAULT_HEADERS = {
        "User-Agent": WECHAT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 教务系统相关接口地址
    SCORE_URL = "https://jwxt.ecjtu.edu.cn/weixin/ScoreQuery"
    COURSE_URL = "https://jwxt.ecjtu.edu.cn/weixin/CalendarServlet"
    EXAM_URL = "https://jwxt.ecjtu.edu.cn/weixin/ExamArrangeCl"


# 全局单例配置对象
settings = Config()
