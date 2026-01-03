#!/bin/bash
#
# build_and_install.sh - 构建并安装 ecjtu-wechat-api 项目包
#
# 该脚本执行以下操作：
# 1. 清理旧的构建产物
# 2. 使用 uv 构建 wheel 和 source 包
# 3. 安装包到当前 Python 环境
# 4. 验证安装是否成功
#

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查 uv 是否安装
check_uv_installed() {
    if ! command -v uv &> /dev/null; then
        print_error "未找到 uv 命令，请先安装 uv"
        print_info "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_info "uv 版本: $(uv --version)"
}

# 清理旧的构建产物
clean_build() {
    print_info "清理旧的构建产物..."
    if [ -d "dist" ]; then
        rm -rf dist/
        print_info "已删除 dist/ 目录"
    fi
    if [ -d "build" ]; then
        rm -rf build/
        print_info "已删除 build/ 目录"
    fi
    if [ -d "*.egg-info" ]; then
        rm -rf *.egg-info/
        print_info "已删除 egg-info 目录"
    fi
}

# 构建项目包
build_package() {
    print_info "开始构建项目包..."

    # 运行代码检查
    print_info "运行代码检查 (ruff check)..."
    uv run ruff check src || print_warning "代码检查发现一些问题，但继续构建..."

    # 运行测试
    print_info "运行测试 (pytest)..."
    if uv run pytest; then
        print_success "所有测试通过"
    else
        print_warning "测试失败，但继续构建..."
    fi

    # 构建包
    print_info "使用 uv build 构建包..."
    uv build

    if [ $? -eq 0 ]; then
        print_success "构建成功！"
    else
        print_error "构建失败"
        exit 1
    fi
}

# 显示构建产物
show_build_artifacts() {
    print_info "构建产物："
    if [ -d "dist" ]; then
        ls -lh dist/
    else
        print_error "dist/ 目录不存在"
        exit 1
    fi
}

# 安装包
install_package() {
    local install_mode=$1

    print_info "开始安装包..."

    case $install_mode in
        "global")
            print_info "全局安装模式 (pip install)"
            uv pip install dist/*.whl
            ;;
        "user")
            print_info "用户安装模式 (pip install --user)"
            uv pip install --user dist/*.whl
            ;;
        "editable")
            print_info "可编辑安装模式 (pip install -e .)"
            uv pip install -e .
            ;;
        *)
            print_info "默认使用可编辑安装模式"
            uv pip install -e .
            ;;
    esac

    if [ $? -eq 0 ]; then
        print_success "安装成功！"
    else
        print_error "安装失败"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    print_info "验证安装..."

    # 检查包是否可以导入
    if uv run python -c "import ecjtu_wechat_api; print(f'包版本: {ecjtu_wechat_api.__version__}')" 2>/dev/null; then
        print_success "包导入验证通过"
    else
        print_error "包导入验证失败"
        exit 1
    fi

    # 显示包信息
    print_info "包详细信息："
    uv run python -c "import ecjtu_wechat_api; print(f'包路径: {ecjtu_wechat_api.__file__}')"
}

# 显示使用帮助
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -g, --global      全局安装 (需要管理员权限)"
    echo "  -u, --user        用户级安装"
    echo "  -e, --editable    可编辑安装 (开发模式)"
    echo "  -b, --build-only  仅构建，不安装"
    echo "  -c, --clean       仅清理构建产物"
    echo "  -h, --help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                 # 默认：构建并可编辑安装"
    echo "  $0 --global        # 构建并全局安装"
    echo "  $0 --build-only    # 仅构建"
    echo "  $0 --clean         # 仅清理"
}

# 主函数
main() {
    local install_mode="editable"
    local build_only=false
    local clean_only=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -g|--global)
                install_mode="global"
                shift
                ;;
            -u|--user)
                install_mode="user"
                shift
                ;;
            -e|--editable)
                install_mode="editable"
                shift
                ;;
            -b|--build-only)
                build_only=true
                shift
                ;;
            -c|--clean)
                clean_only=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # 执行清理
    if [ "$clean_only" = true ]; then
        clean_build
        print_success "清理完成"
        exit 0
    fi

    # 打印项目信息
    echo "=========================================="
    echo "  ecjtu-wechat-api 构建与安装脚本"
    echo "=========================================="
    echo ""

    # 检查环境
    check_project_root
    check_uv_installed

    # 清理旧产物
    clean_build

    # 构建包
    build_package

    # 显示构建产物
    show_build_artifacts

    # 如果只构建，不安装
    if [ "$build_only" = true ]; then
        print_success "构建完成（未安装）"
        exit 0
    fi

    # 安装包
    install_package "$install_mode"

    # 验证安装
    verify_installation

    echo ""
    echo "=========================================="
    print_success "所有操作完成！"
    echo "=========================================="
    echo ""
    echo "快速开始："
    echo "  1. 启动 API 服务器:"
    echo "     uv run uvicorn ecjtu_wechat_api.main:app --reload"
    echo ""
    echo "  2. 查看文档:"
    echo "     http://127.0.0.1:6894/docs"
    echo ""
}

# 运行主函数
main "$@"
