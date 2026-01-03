import json
from typing import Any

from pydantic import BaseModel

from ecjtu_wechat_api.core.config import settings
from ecjtu_wechat_api.utils.logger import logger


def save_debug_data(
    category: str,
    name: str,
    html_content: str | None = None,
    parsed_data: Any | None = None,
):
    """
    保存抓取的数据到本地用于调试。

    Args:
        category: 类别目录名 (如 "scores", "courses")
        name: 文件名标识
        html_content: 原始 HTML 内容
        parsed_data: 解析后的数据 (支持 BaseModel 或 dict)
    """
    out_dir = settings.DATA_DIR / category
    out_dir.mkdir(parents=True, exist_ok=True)

    # 保存原始 HTML
    if html_content:
        html_path = out_dir / f"{name}.html"
        try:
            with open(html_path, mode="w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            logger.warning(f"无法保存调试 HTML: {e}")

    # 保存结构化 JSON
    if parsed_data:
        json_path = out_dir / f"{name}.json"
        try:
            data_to_save = (
                parsed_data.model_dump()
                if isinstance(parsed_data, BaseModel)
                else parsed_data
            )
            with open(json_path, mode="w", encoding="utf-8") as f:
                f.write(json.dumps(data_to_save, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"无法保存调试 JSON: {e}")
