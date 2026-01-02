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


# 全局单例配置对象
settings = Config()
