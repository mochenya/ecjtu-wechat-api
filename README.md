<div align="center">

# 🏫 ECJTU WeChat API
### 华东交通大学教务系统微信版 API

[![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/uv-managed-430098?style=for-the-badge&logo=python&logoColor=white)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#-核心功能">核心功能</a> •
  <a href="#-技术栈">技术栈</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-api-文档">API 文档</a> •
  <a href="#-贡献指南">贡献指南</a>
</p>

</div>

---

## 📖 项目简介

**ECJTU WeChat API** 是一个非官方的教务系统数据接口服务。通过抓包与逆向工程分析华东交通大学教务系统在微信公众号的接口，我们将其封装为现代化、类型安全且易于使用的 RESTful API。

该项目旨在为校园开发者提供稳定可靠的数据接入方案，支持**课程表查询**、**成绩获取**、**考试安排查询**等核心教务功能，并提供结构化的 JSON 数据响应，彻底告别繁琐的 HTML 解析。

## ✨ 核心功能

| 功能 | 描述 | API 路径 |
| :--- | :--- | :--- |
| 📅 **每日课表** | 获取指定日期的详细课程安排，支持自动解析课程节点、教室及教师信息。 | `GET /courses/daily` |
| 📊 **成绩查询** | 获取指定学期的成绩数据（默认为当前学期），包含所有可选学期列表、原始分数、学分、绩点及补考状态。 | `GET /scores/info` |
| 📝 **考试安排** | 获取指定学期的考试安排（默认为当前学期），包含考试时间、地点、课程信息及所有可选学期列表。 | `GET /exams/schedule` |
| 🛡️ **类型安全** | 全面使用 Pydantic 模型定义数据结构，API 响应清晰、字段明确。 | - |
| ⚡ **高性能** | 基于 FastAPI 构建，异步处理请求，响应速度极快。 | - |

## 🛠️ 技术栈

- **Core**: Python 3.12+
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Data Parsing**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **HTTP Client**: [httpx](https://www.python-httpx.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Linting & Formatting**: [Ruff](https://docs.astral.sh/ruff/)

## 🚀 快速开始

### 1. 环境准备

本项目采用新一代 Python 包管理工具 **uv**。请先确保您的环境中已安装 uv：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆与安装

```bash
# 克隆仓库
git clone https://github.com/mochenya/ecjtu-wechat-api
cd ecjtu-wechat-api

# 同步依赖 (uv 会自动创建并管理虚拟环境)
uv sync
```

### 3. 启动服务

```bash
# 开启开发服务器 (支持热重载)
uv run uvicorn ecjtu_wechat_api.main:app --host 0.0.0.0 --port 6894 --reload
```

服务启动成功后，终端将显示如下信息：
```
INFO:     Uvicorn running on http://0.0.0.0:6894 (Press CTRL+C to quit)
```

## 📖 API 文档

服务启动后，您可以通过浏览器访问交互式 API 文档，直接在线测试接口：

- **Swagger UI** (推荐): [http://localhost:6894/docs](http://localhost:6894/docs)
- **ReDoc**: [http://localhost:6894/redoc](http://localhost:6894/redoc)

### 接口调用示例

#### 获取当日课表

```http
GET /courses/daily?weiXinID=微信教务公众号里的WEIXINID&date=2026-01-01
```

#### 获取成绩信息

```http
GET /scores/info?weiXinID=微信教务公众号里的WEIXINID&term=2025.1
```

> `term` 参数可选，不传则默认查询当前学期。

#### 获取考试安排

```http
GET /exams/schedule?weiXinID=微信教务公众号里的WEIXINID&term=2025.1
```

> `term` 参数可选，不传则默认查询当前学期。

## 📂 项目结构

```bash
ecjtu_wechat_api/
├── src/
│   └── ecjtu_wechat_api/
│       ├── api/            # 路由层：定义 API 接口
│       ├── core/           # 核心层：配置、异常处理
│       ├── models/         # 模型层：Pydantic 数据结构
│       ├── services/       # 服务层：业务逻辑与 HTML 解析
│       ├── utils/          # 工具层：辅助函数
│       └── main.py         # 应用入口
├── tests/                  # 测试套件
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
└── build_and_install.sh    # 构建脚本
```

## ⚠️ 免责声明

> 本项目仅供编程学习与技术研究使用。
>
> 1. 开发者不对使用本 API 产生的任何后果负责。
> 2. 请勿将本工具用于任何非法用途（如恶意爬虫、暴力破解等）。
> 3. 请遵守学校网络管理规定，合理使用校园网资源。

---
<p align="center">Made with ❤️ by mochenyaa</p>
